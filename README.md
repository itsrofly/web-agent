# Web Agent

## 📋 Requirements

- Python 3.12
- Docker

## 🔧 Environment Setup

To run the application, you need to create a `.env` file at the project root. This file stores sensitive credentials and configuration settings for API services, the database, and backend authentication.

---

### Steps to Create and Configure the .env File

1. **Create a file named `.env` in the project's root directory.**
2. **Copy and paste the following template into the `.env` file:**
   ```env
   OPENAI_API_KEY=
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

1. Start the web driver using Docker Compose:
```bash
docker compose up -d
```

2. Run the Streamlit application in a separate terminal:
```bash
streamlit run src/webAgent/main.py
```
