# 🔗 Short URL API with QR & Optional Auth

A robust, production-ready REST API for URL shortening, featuring QR code generation, stateless JWT authentication, and an optional-auth architecture. 

Built with **FastAPI** and packaged with **Docker**, this project is designed with a focus on clean architecture, security, and developer experience.

## ✨ Features & Bonuses Achieved

* **Optional Authentication:** The core `POST /links` endpoint seamlessly handles both anonymous guests (creating untrackable links) and authenticated users (creating tracked, manageable links).
* **Stateless Security (JWT):** User sessions are managed via secure JSON Web Tokens. Passwords are cryptographically hashed (bcrypt) and never stored in plain text.
* **QR Code Generation:** Instantly generates a scannable PNG QR code for any shortened URL.
* **🏆 Bonus: Real Database (SQLite):** Upgraded from in-memory storage to a persistent SQLite database using SQLAlchemy.
* **🏆 Bonus: Idempotency:** Authenticated users shortening the exact same URL multiple times will receive their existing short code, optimizing database storage and ensuring consistent responses.
* **🏆 Bonus: Rate Limiting:** Implemented API rate limiting to protect the server from spam and abuse.
* **🛡️ Automated Testing:** Includes a robust test suite built with `pytest` and FastAPI's `TestClient` to verify core flows and ensure API reliability.
* **DevOps & CI:** Fully containerized using Docker and `docker-compose`, with dependency management powered by `uv` for reproducible builds.

## 🏗️ Architecture & Design Decisions

### The 403 vs. 404 Dilemma (Resource Ownership)
**Question:** What status code should be returned when a user attempts to access or delete a link they do not own?
**Decision:** `404 Not Found`.
**Rationale:** While `403 Forbidden` technically describes the permission issue, returning a 403 confirms to a potential attacker that the specific short code exists in the database. Returning a `404 Not Found` masks the existence of the resource from unauthorized users, preventing Resource Enumeration attacks (IDOR prevention). The system effectively says: "As far as your permissions are concerned, this resource does not exist."

## 🚀 How to Run (Docker)

The application is fully containerized. You don't need to install Python or any dependencies locally.

1. **Clone the repository:**
    git clone https://github.com/avital3278/short-url-api.git
    cd short-url-api

2. **Set up Environment Variables:**
    Copy the example environment file:
    cp .env.example .env
    (Ensure you generate a secure SECRET_KEY in your .env file).

3. **Run with Docker Compose:**
    docker compose up --build

4. **Access the Application:**
    * API Health Check: http://localhost:8000/health
    * Interactive API Documentation (Swagger): http://localhost:8000/docs
    * Run Tests: `uv run pytest`

## 🛠️ Tech Stack
* **Framework:** FastAPI
* **Language:** Python 3.12
* **Package Manager:** uv
* **Database:** SQLite & SQLAlchemy ORM
* **Testing:** Pytest
* **Authentication:** JWT (python-jose) & bcrypt (passlib)
* **Containerization:** Docker & Docker Composeg