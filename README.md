# Web Agent

## 📋 Requirements

- Python 3.12
- Docker (Optional)

## 🔧 Environment Setup

To run the application, you need to create a `.env` file at the project root. This file stores sensitive credentials and configuration settings for API services, the database, and backend authentication.

---

### Steps to Create and Configure the .env File

1. **Create a file named `.env` in the project's root directory.**
2. **Copy and paste the following template into the `.env` file:**
   ```env
   OPENAI_API_KEY=
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
