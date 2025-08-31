# Knowledge Navigator

An AI-powered learning platform designed to simplify complex topics through a structured, modular approach and real-time AI assistance. This application helps users learn and understand new concepts at their own pace.

---

## ✨ Features

* **User Authentication:** Secure user registration, login, and session management.
* **Modular Learning:** Access a library of structured learning modules.
* **AI-Powered Explanations:** Get instant, simplified explanations for any topic using the Gemini API.
* **Subscription Model:** Paystack-powered payments to unlock premium, members-only content.
* **Database Integration:** MySQL-backed persistence for users and modules.

---

## 🚀 Technology Stack

* **Backend:** Python 3.x
* **Web Framework:** Flask
* **Database:** MySQL (local) and MySQL on Railway (production)
* **Hosting:** Render
* **Environment Management:** `python-dotenv`
* **Password Hashing:** `werkzeug.security`
* **API Integrations:**

  * **Google Gemini API** for AI explanations
  * **Paystack API** for payments

---

## 🧭 Project Structure (suggested)

```
knowledge-navigator/
├─ app.py
├─ requirements.txt
├─ .env            # local environment variables
├─ README.md
├─ templates/      # Flask Jinja templates
├─ static/         # CSS, JS, images
├─ models/         # (optional) database models / helpers
└─ sql/            # SQL schema & seed files
```

---

## 💻 Local Setup

### 1) Clone the Repository

```bash
git clone https://github.com/Deeja-ish/KNOWLWDGENAVIGATOR.git
cd KNOWLWDGENAVIGATOR
```

### 2) Create & Activate a Virtual Environment

```bash
python3 -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 3) Install Dependencies

```bash
pip install -r requirements.txt
```

### 4) Configure Environment Variables

Create a `.env` file in the project root and add:

```
# Paystack API Keys
PAYSTACK_SECRET_KEY="your_paystack_secret_key"
PAYSTACK_PUBLIC_KEY="your_paystack_public_key"

# Google Gemini API Key
GEMINI_API_KEY="your_gemini_api_key"

# Flask Secret Key
SECRET_KEY="your_flask_secret_key"

# Local Database Configuration
MYSQL_HOST="localhost"
MYSQL_USER="root"
MYSQL_PASSWORD="your_local_db_password"
MYSQL_DB="knowledge_navigator"

# (Production) Use DATABASE_URL when deploying
# DATABASE_URL="mysql://user:password@host:port/knowledge_navigator"
```

> **Note:** In production, prefer `DATABASE_URL` from your cloud host. Locally, use the discrete MySQL variables above.

---

## 🗄️ Database Setup (MySQL)

Start your MySQL server, then run the following to create the database and basic tables:

```sql
CREATE DATABASE knowledge_navigator;

USE knowledge_navigator;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE modules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    content TEXT
);

INSERT INTO modules (title, description, content) VALUES
('Python Basics', 'A foundational course on Python programming, covering syntax, data types, and functions.', 'python-basics', 0),
('Data Science Fundamentals', 'An introduction to data analysis, visualization, and basic machine learning concepts.', 'data-science', 1),
('AI & Machine Learning', 'An in-depth look into artificial intelligence, neural networks, and model building.', 'ai', 1),
('Cybersecurity Essentials', 'Learn the basics of digital security, including threat identification and system protection.', 'cybersecurity', 0),
('Cloud Computing 101', 'An introductory guide to cloud infrastructure and popular services like AWS and Azure.', 'cloud-computing', 0);
```

---

## ▶️ Run the Application

```bash
# Option A: using Flask default
flask run

# Option B: specify app module (if needed)
# flask --app app run
```

The app will be available at `http://127.0.0.1:5000`.

---

## ⚙️ Deployment

This application is designed for deployment on **Render** with a managed MySQL instance hosted on **Railway** (or any other cloud provider). Ensure your deployment uses a `DATABASE_URL` environment variable.

**Production Checklist:**

* Set all required env vars (Paystack, Gemini, SECRET\_KEY, DATABASE\_URL).
* Run database migrations / schema SQL on the production database.
* Configure allowed hosts, SSL/TLS, and logging as needed.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/awesome-change`
3. Commit your changes: `git commit -m "Add awesome change"`
4. Push to the branch: `git push origin feat/awesome-change`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **\[License Name]** — see `LICENSE.md` for details.

---

## 📧 Contact

For questions or collaboration inquiries, reach out at **\khadijaismail696@gmail.com**.

---

## 🧩 Build Prompt (for reproducibility)

Use the following prompt to recreate or iterate on this project:

```
You are an accomplished software developer, well-versed in the intricacies of sustainable development goals such as Education, Health, and Food security. You possess innovative ideas on leveraging technology to address real-world challenges. Your mission is to assist me in creating a multi-page web application from the ground up that tackles one of the pressing issues I've mentioned.

We will embark on this journey step-by-step, crafting a straightforward and effective solution. I would like guidance on integrating a backend system suitable for beginners, using HTML, CSS, JavaScript, Python, and MySQL. Let's keep the process uncomplicated yet impactful, ensuring that the user interface is visually stunning and engaging. We can incorporate artistic illustrations where necessary to enhance the overall experience.

To make our app more vibrant and user-friendly, we'll utilize Font Awesome for icons and select an appealing Google font for our typography. Additionally, we should explore and integrate a relevant AI API that suits the purpose of our site, enriching the user experience and functionality. Together, we'll bring this vision to life!
```
