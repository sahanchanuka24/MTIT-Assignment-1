# 🤖 Generative AI in Software Engineering

### Secure Login System using Python Flask

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Framework-Flask-black)
![Database](https://img.shields.io/badge/Database-SQLite-green)
![Security](https://img.shields.io/badge/Security-Bcrypt%20%7C%20CSRF-red)
![License](https://img.shields.io/badge/License-Academic-yellow)

---

# 📌 Table of Contents

* [Project Overview](#-project-overview)
* [Objectives](#-objectives)
* [Project Scope](#-project-scope)
* [System Architecture](#-system-architecture)
* [Tech Stack](#-tech-stack)
* [Key Features](#-key-features)
* [Project Structure](#-project-structure)
* [Installation Guide](#-installation-guide)
* [Usage](#-usage)
* [AI Tools Evaluation](#-ai-tools-evaluation)
* [Future Improvements](#-future-improvements)
* [Learning Outcomes](#-learning-outcomes)
* [Author](#-author)

---

# 📝 Project Overview

This project explores the **practical application of Generative AI (GenAI) tools in modern Software Engineering workflows**.

The objective of the project is to demonstrate how AI-powered development assistants can support engineers in performing common development tasks such as:

* Code generation
* Debugging
* Documentation writing
* System design support

As part of this assignment, **Option A – Software Engineering** was selected.

A **secure authentication system** was developed using **Python Flask**, with AI tools assisting during the development process.

---

# 🎯 Objectives

The main goal of this project is to **experiment with and evaluate two leading Generative AI tools** in solving real-world software engineering problems.

The tools used are:

* **ChatGPT**
* **Claude AI**

These tools were applied to different development tasks and later evaluated based on their performance and output quality.

---

# 🛠 Project Scope

This project covers several important areas in the software development lifecycle.

## 1️⃣ Code Generation

Developing a **secure login system module** using:

* Python Flask
* SQLite database
* HTML templates

The AI tools assisted in generating functional code structures and implementation logic.

## 2️⃣ Debugging and Error Resolution

AI tools were used to:

* Detect errors in existing code
* Suggest corrections
* Improve overall application stability

## 3️⃣ Technical Documentation

AI-generated content was used to create **structured documentation** explaining:

* System functionality
* Security mechanisms
* Application architecture

## 4️⃣ Comparative Evaluation

Both AI tools were analyzed based on:

* Output Quality
* Prompt Sensitivity
* Technical Limitations
* Overall Performance

---

# 🏗 System Architecture

The system follows a **basic web application architecture**:

```
User Browser
      │
      ▼
HTML Templates (Jinja2)
      │
      ▼
Flask Backend (app.py)
      │
      ▼
SQLite Database
```

Security layers include:

* Password Hashing
* CSRF Protection
* Session Management

---

# 💻 Tech Stack

| Technology    | Purpose                      |
| ------------- | ---------------------------- |
| Python        | Backend programming language |
| Flask         | Web framework                |
| SQLite        | Lightweight database         |
| HTML + Jinja2 | Frontend templates           |
| Flask-Bcrypt  | Password hashing             |
| Flask-WTF     | CSRF protection              |
| Git & GitHub  | Version control              |
| VS Code       | Development environment      |
| Postman       | API testing                  |

---

# 🚀 Key Features

### 🔐 Secure Authentication

* User Registration
* Password Hashing using Bcrypt

### 👤 Login System

* Email and password validation
* Secure login process

### 🧠 Session Management

* Logged-in users can access protected pages
* Unauthorized users are restricted

### 🛡 Security Features

* CSRF protection
* Input validation
* Secure password storage

### ⚠ Error Handling

* Custom **404 Page**
* Custom **500 Server Error Page**

---

# 📂 Project Structure

```
Claude
│
├── templates
│   ├── base.html
│   ├── dashboard.html
│   ├── error.html
│   ├── login.html
│   ├── register.html
├── app.py
├── auth.log
├── requirements.txt
├── users.db
├── users.db-shm
└── users.db-wal
```

---

# ⚙️ Installation Guide

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/genai-login-system.git
```

### 2️⃣ Navigate to the Project Directory

```bash
cd genai-login-system
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Application

```bash
python app.py
```

### 5️⃣ Open the Application

Open your browser and go to:

```
http://127.0.0.1:5000
```

---

# 📊 AI Tools Evaluation

| Criteria              | ChatGPT   | Claude AI |
| --------------------- | --------- | --------- |
| Output Quality        | High      | High      |
| Prompt Sensitivity    | Moderate  | High      |
| Technical Accuracy    | Very Good | Good      |
| Documentation Ability | Excellent | Good      |

Both tools demonstrated strong capabilities in assisting software engineering tasks.

---

# 🔮 Future Improvements

* Password Reset functionality
* Email verification system
* User profile management
* Role-based access control
* JWT authentication
* Docker container deployment
* CI/CD pipeline integration

---

# 🎓 Learning Outcomes

* Understanding the role of **Generative AI in software engineering**
* Implementing **secure authentication systems**
* Improving **debugging and code review workflows**
* Evaluating **AI-assisted development tools**

---

👤 Author

Sahan Chanuka
Student ID: IT22231864
Sri Lanka 🇱🇰
