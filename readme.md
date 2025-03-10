# Running the Project

Follow these steps to set up and run the project on your local machine using PowerShell on Windows.

## Prerequisites

- Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
- Make sure PowerShell is available on your system.

## Setup Instructions

1. **Clone the Repository**

   First, clone the repository to your local machine.

   ```powershell
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a Virtual Environment**

   Create a virtual environment to manage dependencies.

   ```powershell
   python -m venv .venv
   ```

3. **Activate the Virtual Environment**

   Activate the virtual environment using the following command:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. **Install Dependencies**

   Install the required dependencies using the `requirements.txt` file.

   ```powershell
   pip install -r chatbot/requirements.txt
   ```

5. **Set Environment Variables**

   Create a `.env` file in the root directory and set the necessary environment variables. You can refer to the `.env.example` file if available.

6. **Run the Application**

   Start the application using the following command:

   ```powershell
   python chatbot/main.py
   ```

   The application should now be running, and you can access it at `http://localhost:5000`.

## Additional Notes

- Ensure that the `courses_data.json` file is present in the `chatbot` directory. If not, the application will attempt to scrape the data automatically.
- If you encounter any issues, ensure that all dependencies are correctly installed and that the environment variables are set properly.
