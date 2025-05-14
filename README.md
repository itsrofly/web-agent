# Web Agent

## 📋 Requirements

- Python 3.12
- Docker (Optional)
- Make (Optional)

## 🔧 Environment Setup

To run the application, you need to create a `.env` file at the project root. This file stores sensitive credentials and configuration settings for API services, the database, and backend authentication.

---

### 📄 Steps to Create and Configure the .env File

1. **Create a file named `.env` in the project's root directory.**
2. **Copy and paste the following template into the `.env` file:**
   ```
   env N/A=
   ```

Once the environment is set up, you can use these Makefile commands for quick configuration:

- ```bash
  make setup
  source env/bin/activate
  ```
  Or
- ```bash
  pip install -r requirements.txt
  tar -xzf geckodriver-v0.36.0-linux64.tar.gz -C src/build/
  chmod +x src/build/geckodriver
  ```

## 🚀 Running the Project

### With Python

- ```bash
  python -m ...
  ```

### With Docker

- ```bash
  docker compose up --build
  ```

🔗**Information:**

- Access at: [http://localhost](http://localhost)

To stop the Docker container:

- ```bash
    docker compose down
  ```

📚 Enjoy your project! 🌟