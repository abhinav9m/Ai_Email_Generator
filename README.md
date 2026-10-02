# AI Email Generator Using Generative AI ✉️🤖

An intelligent, full-stack AI Email Generator built using **FastAPI**, **Python**, **Generative AI (Gemini API)**, and **SQLite**. It allows users to compose, customize, and refine professional emails across 12 distinct categories with precise tone and length controls.

---

## ✨ Features

- 📑 **12 Email Categories**:
  - Leave Request
  - Internship Request
  - Job Application
  - Permission Request
  - Meeting Request
  - Complaint
  - Follow-up Email
  - Thank You Email
  - Apology Email
  - Resignation Email
  - Request for Information
  - Custom Email

- 🎭 **Tone Control**:
  - Formal, Professional, Friendly, Polite, Direct

- 📏 **Length Control**:
  - Short (50–80 words), Medium (80–150 words), Detailed (150–250 words)

- 👤 **Recipient Normalization**:
  - Automatically formats recipient titles cleanly (e.g. `to manager` $\rightarrow$ `Dear Manager,`, `HR` $\rightarrow$ `Dear HR Team,`).

- 🔒 **Strict No-Fact-Invention**:
  - Generates emails using strictly user-supplied details without hallucinating fake dates, medical details, or unstated facts.

- 🔄 **Versioned Email History & Refinement**:
  - SQLite backend persists every generation, regeneration, and refinement as separate history items (`v1`, `v2`, etc.).

- 📋 **One-Click Actions**:
  - Copy Subject, Copy Full Email, Export `.txt`, Toggle Favorites, Delete & Clear History.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, Modern Vanilla JavaScript
- **Backend**: Python, FastAPI, Uvicorn
- **GenAI Integration**: Google Gemini API (`google-genai` / `google-generativeai`)
- **Database**: SQLite3

---

## 🚀 Local Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/abhinav9m/Ai_Email_Generator.git
   cd Ai_Email_Generator
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   PORT=8000
   ```

4. **Run the Application**:
   ```bash
   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

5. **Open in Browser**:
   Navigate to `http://127.0.0.1:8000`

---

## ☁️ Deployment on Railway

1. Push this repository to GitHub.
2. Log into [Railway.app](https://railway.app) and create a **New Project**.
3. Select **Deploy from GitHub repo** and pick `Ai_Email_Generator`.
4. Add Environment Variable in Railway dashboard:
   - `GEMINI_API_KEY`: *Your Gemini API Key*
5. Railway will automatically detect the `Procfile` and deploy your app!
