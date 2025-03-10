from flask import Flask, request, jsonify
import os
from scrape import scrape_brainlox
from vector_store import load_course_data, prepare_documents, create_vector_store
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Global variables to store our instances
vector_store = None
conversation_chain = None
chat_history = []

def initialize_system():
    """Initialize the system by scraping data and creating vector store"""
    global vector_store, conversation_chain
    
    print("Starting system initialization...")
    
    # Step 1: Scrape the data if it doesn't exist
    if not os.path.exists("courses_data.json"):
        print("Scraping course data...")
        scrape_brainlox()
    
    # Step 2: Load and prepare the data
    print("Loading and preparing course data...")
    courses = load_course_data()
    if not courses:
        raise Exception("No course data available")
    
    documents = prepare_documents(courses)
    
    # Step 3: Create vector store
    print("Creating vector store...")
    vector_store = create_vector_store(documents)
    
    # Step 4: Initialize the chat model with OpenRouter
    llm = ChatOpenAI(
        model="openai/gpt-4o-mini",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        default_headers={
            "HTTP-Referer": os.getenv("SITE_URL", "http://localhost:5000"),
            "X-Title": os.getenv("SITE_NAME", "Course Chatbot")
        }
    )
    
    # Step 5: Create conversation chain
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(),
        memory=memory,
        verbose=True
    )
    
    print("System initialization complete!")

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message']
        
        # Ensure the conversation chain is initialized
        if conversation_chain is None:
            return jsonify({'error': 'System not initialized'}), 500
        
        # Get the response from the conversation chain
        response = conversation_chain({
            "question": user_message,
            "chat_history": chat_history
        })
        
        # Update chat history
        chat_history.append((user_message, response['answer']))
        
        return jsonify({
            'response': response['answer'],
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/reset', methods=['POST'])
def reset_conversation():
    """Reset the conversation history"""
    global chat_history
    chat_history = []
    return jsonify({'message': 'Conversation history reset', 'success': True})

@app.route('/prompt', methods=['POST'])
def prompt_vector_store():
    """Directly query the vector store"""
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({'error': 'No query provided'}), 400
            
        if vector_store is None:
            return jsonify({'error': 'Vector store not initialized'}), 500
            
        # Search the vector store
        docs = vector_store.similarity_search(data['query'])
        
        # Format results
        results = [{"content": doc.page_content, "metadata": doc.metadata} for doc in docs]
        
        return jsonify({
            'results': results,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

if __name__ == "__main__":
    # Initialize the system before starting the Flask app
    initialize_system()
    
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
