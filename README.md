# Web Agent
The Web Agent is a Python-based application designed to automate web interactions. It utilizes Selenium WebDriver to control a web browser and perform tasks as directed by a user through a chat interface powered by a large language model.

## 📋 Requirements

- Python 3.12
- Docker

## 🔧 Environment Setup

To run the application, you need to create a `.env` file at the project root. This file stores sensitive credentials and configuration settings for API services.

---

### Steps to Create and Configure the .env File

1. **Create a file named `.env` in the project's root directory.**
2. **Copy and paste the following template into the `.env` file and fill in the variables:**
   ```env
    BASE_URL= # OpenAI API Compatible
    API_KEY=
    MODEL_NAME=gemini-2.5-pro-preview-05-06 # Reasoning Model
   ```

## 📦 Project Setup

To set up the project environment, follow these steps:

1. **Create a virtual environment** (recommended):
  ```bash
  python -m venv venv
  ```

2. **Activate the virtual environment**
  ```bash
  source venv/bin/activate
  ```

3. **Install dependencies**
  ```bash
  pip install -r requirements.txt
  ```

## 🚀 Running the Project

To run the application:

1. Start the Remote WebDriver using Docker Compose (Recommended):
```bash
docker compose up -d
```

2. Run the chat application:
```bash
streamlit run src/webAgent/main.py
```

3. Open Chat & WebDriver

Remote WebDriver: [http://172.18.0.2:7900/](http://172.18.0.2:7900/)
  * Password: secret

Chat: [http://localhost:8501/](http://localhost:8501/)
  * Select Remote WebDriver (Recommended)
