# 🔗 Short URL API with QR & Optional Auth

[![CI](https://img.shields.io/github/actions/workflow/status/avital3278/short-url-api/ci.yml?style=for-the-badge)](https://github.com/avital3278/short-url-api/actions/workflows/ci.yml)
![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen?style=for-the-badge)
![GitHub top language](https://img.shields.io/github/languages/top/avital3278/short-url-api?style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/avital3278/short-url-api?style=for-the-badge)
![GitHub repo size](https://img.shields.io/github/repo-size/avital3278/short-url-api?style=for-the-badge)

A robust, production-ready REST API for URL shortening, featuring QR code generation, stateless JWT authentication, and an optional-auth architecture. 

Built with FastAPI and packaged with Docker, this project is designed with a focus on clean architecture, security, and developer experience.

## ✨ Key Features
* Optional Authentication: The core POST /links endpoint seamlessly handles both anonymous guests and authenticated users, providing tracked, manageable links for registered accounts.
* Custom Aliases & Conflict Prevention: Users can specify a custom identifier for their link. The system enforces uniqueness and ensures robust conflict management with a 409 Conflict response.
* Stateless Security (JWT): Secure session management using JSON Web Tokens with cryptographically hashed passwords (bcrypt).
* QR Code Generation: Integrated QR code generation for any shortened URL, returned as a PNG response.
* Persistent Storage: Data integrity ensured through a persistent SQLite database using SQLAlchemy ORM.
* Idempotency: Optimized database interactions where authenticated users requesting the same URL receive their existing short code.
* Rate Limiting: Built-in protection against API abuse and spam.
* Reliability & DevOps: Fully containerized with Docker, featuring an automated CI pipeline with pytest and code quality linting.

## 🏗️ Architecture & Design Decisions
### Resource Ownership & Security
Question: How to handle unauthorized access/deletion of private links?
Decision: Returning a 404 Not Found rather than a 403 Forbidden.
Rationale: This approach prevents Resource Enumeration (IDOR) attacks, ensuring that unauthorized users cannot verify the existence of resources within the database.

## 🚀 How to Run (Docker)
1. Clone the repository: git clone https://github.com/avital3278/short-url-api.git && cd short-url-api
2. Set up Environment Variables: cp .env.example .env
3. Run with Docker Compose: docker compose up --build
4. Testing the API:
   - Interactive API Documentation (Swagger): http://localhost:8000/docs
   - API Health Check: http://localhost:8000/health
   - Run Tests: uv run pytest

## 🛠️ Tech Stack
* Framework: FastAPI
* Language: Python 3.12
* Database: SQLite & SQLAlchemy
* Auth: JWT (python-jose) & bcrypt
* Containerization: Docker & Docker Compose