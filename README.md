# resume-advisor-backend

**Backend API for Resume Advisor application**  
Stores user profiles (resumes, education, projects), job descriptions, and provides analysis using LLM to help users tailor their resumes for job applications.  

---

## Table of Contents
1. [Project Description](#project-description)  
2. [Features](#features)  
3. [Tech Stack](#tech-stack)  
4. [Setup](#setup)  
5. [API Endpoints](#api-endpoints)  
6. [LLM Integration](#llm-integration)  
7. [License](#license)  

---

## Project Description
The Resume Advisor backend is designed for students, graduates, and engineers who want to quickly customize resumes for different jobs.  
It stores structured user and job data, and provides AI-assisted recommendations to improve application quality and save time.  

---

## Features
- CRUD operations for users, resumes, education, projects, and jobs  
- Provides RESTful API for web and mobile frontend clients
- Secure database connection (MySQL)  
- Placeholder endpoint for LLM analysis (resume vs job description)  

---

## Tech Stack
- Python 3.11+
- Flask  
- MySQL  
- Flask-MySQLdb  
- (Future) OpenAI / LLM integration  

---

## Setup
1. Clone the repo:  
```bash
git clone https://github.com/<your-username>/resume-advisor-backend.git
cd resume-advisor-backend

---

## Run
```bash
docker compose up --build
docker compose up
