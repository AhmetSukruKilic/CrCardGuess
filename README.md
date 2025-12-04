# CrCardGuess

A full-stack card-guessing (or card-based) game API + service, built with Python, SQLAlchemy, Docker, and more.

## 🚀 What is CrCardGuess

CrCardGuess is a backend service implementing a game where users can guess cards (or perform some “card guess” logic) — with user authentication, scoring, leaderboards, scheduled resets and reward distribution.  
It uses JWT authentication, a MySQL database (via SQLAlchemy), Docker for containerization, and defines a modular structure for models, schemas, database config, utilities, etc.

## ✅ Features

- User signup / login with email + password (hashed with bcrypt via Passlib)  
- JWT-based stateless authentication (token contains `sub = user_id`, expiry configurable via environment variables)  
- User scoreboard and rewards per game mode / period  
- Automatic scheduled resets and reward distributions using a scheduler (cron jobs)  
- Clean database layer using SQLAlchemy ORM (MySQL 8)  
- Modular project structure (separate modules for API logic, DB models, schemas, utilities)  
- Docker + `docker-compose.yml` support for easy setup and deployment  

## 📦 Getting Started

### Prerequisites

- Docker & Docker Compose  
- (Optional) Python 3.x and pip, if you want to run without Docker  
- MySQL (if not using Dockerized DB)  

### Quick Start (with Docker Compose)

```bash
cp .env.sample .env   # copy example env file and configure as needed  
docker compose up --build
