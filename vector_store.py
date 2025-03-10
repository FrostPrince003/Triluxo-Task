import os
import json
from typing import List
from langchain.docstore.document import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def load_course_data() -> List[dict]:
    """Load course data from JSON file"""
    try:
        with open("courses_data.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Error: courses_data.json not found. Please run the scraper first.")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in courses_data.json")
        return []

def prepare_documents(courses: List[dict]) -> List[Document]:
    """Convert course data into LangChain documents"""
    documents = []
    for course in courses:
        # Create content with all course information
        content_parts = [
            f"Title: {course.get('title', '')}",
            f"Description: {course.get('course_description', course.get('short_description', ''))}",
            f"Price: ${course.get('price_per_session', '')} {course.get('price_text', '')}",
            f"Number of Lessons: {course.get('lessons_count', '')}"
        ]
        
        # Add main features if available
        if 'main_features' in course:
            content_parts.append("Main Features:")
            content_parts.extend([f"- {feature}" for feature in course['main_features']])
        
        # Create metadata for quick access to important fields
        metadata = {
            "title": course.get('title', ''),
            "url": course.get('course_url', ''),
            "image_url": course.get('image_url', ''),
            "price": course.get('price_per_session', 0)
        }
        
        # Create document
        doc = Document(
            page_content="\n".join(content_parts),
            metadata=metadata
        )
        documents.append(doc)
    
    return documents

def create_vector_store(documents: List[Document]) -> Chroma:
    """Create and populate the vector store"""
    # Initialize the embeddings (MiniLM model)
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # Create and populate vector store
    vector_store = Chroma(
        collection_name="brainlox_courses",
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )
    
    # Add documents
    vector_store.add_documents(documents)
    
    return vector_store

def search_courses(vector_store: Chroma, query: str, k: int = 3) -> List[Document]:
    """Search for courses using semantic similarity"""
    return vector_store.similarity_search(query, k=k)

def main():
    # Load course data
    print("Loading course data...")
    courses = load_course_data()
    if not courses:
        return
    
    # Prepare documents
    print("Preparing documents...")
    documents = prepare_documents(courses)
    
    # Create vector store
    print("Creating vector store...")
    vector_store = create_vector_store(documents)
    print(f"Successfully created vector store with {len(documents)} courses!")

if __name__ == "__main__":
    main()
