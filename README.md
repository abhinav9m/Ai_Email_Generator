# AI Email Generator Using Generative AI ✉️🤖

An intelligent, full-stack web application that uses Google Gemini Generative AI to compose, customize, and refine clear, professional emails tailored for students, employees, and professionals.

---

## 📌 Problem Statement

Writing professional emails can be challenging and time-consuming, especially when choosing the appropriate tone, structure, and wording for different situations. Traditional templates provide static content that cannot adapt to specific recipients or unique contexts. 

This system uses Generative AI to convert rough notes and user intent into well-structured, personalized emails without inventing unstated facts or hallucinating details.

---

## ✨ Features

- 📑 **12 Email Purpose Categories**:
  - **Leave Request**: Requests leave with clear duration and context.
  - **Internship Request**: Highlights skills and availability.
  - **Job Application**: Emphasizes qualifications and career interest.
  - **Permission Request**: Solicits permission for events/activities.
  - **Meeting Request**: Proposes agendas and meeting requests.
  - **Complaint**: Expresses concerns politely while seeking resolution.
  - **Follow-up Email**: Follows up on past applications or communications.
  - **Thank You Email**: Expresses gratitude for interviews or assistance.
  - **Apology Email**: Delivers professional apologies without fake excuses.
  - **Resignation Email**: Communicates formal departure respectfully.
  - **Request for Information**: Asks for specific clarification or details.
  - **Custom Email**: Tailored email generation based on custom user prompts.

- 👤 **Smart Recipient Normalization**:
  - Automatically cleans raw recipient input (e.g. `to manager` $\rightarrow$ `Dear Manager,`, `HR` $\rightarrow$ `Dear HR Team,`, `John Smith` $\rightarrow$ `Dear John Smith,`).

- 🔒 **Strict Fact Preservation**:
  - Generates content strictly from user-supplied details without inventing fake dates, medical details, or unstated facts.

- 🎭 **Tone Control**:
  - **Formal**: Structured executive language and formal etiquette.
  - **Professional**: Clear, efficient, standard business tone.
  - **Friendly**: Warm, conversational, and approachable.
  - **Polite**: Extremely courteous and soft-worded.
  - **Direct**: Concise, goal-oriented, and straightforward.

- 📏 **Length Control**:
  - **Short**: 50–80 words
  - **Medium**: 80–150 words
  - **Detailed**: 150–250 words

- 🔄 **Versioned Email History**:
  - SQLite backend saves every generation, regeneration, and improvement as a separate history record (`v1`, `v2`, etc.).

- 📋 **Productivity Tools**:
  - One-click copy for Subject & Full Email.
  - Export email as a `.txt` file.
  - Toggle favorite stars and manage history entries.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, Modern JavaScript (Vanilla JS)
- **Backend**: Python 3.12, FastAPI, Uvicorn
- **AI Integration**: Google Gemini API (`google-genai` / `google-generativeai`)
- **Database**: SQLite3

---

## 📁 Project Structure

```
ai email generator/
├── .env.example          # Sample environment variables
├── .gitignore            # Git ignore definitions
├── Procfile              # Web process server configuration
├── README.md             # Project documentation
├── database.py           # SQLite database schema and CRUD operations
├── main.py               # FastAPI backend server endpoints
├── requirements.txt      # Python dependencies
├── services/
│   └── email_service.py  # Prompt engineering, Gemini API & recipient normalization
└── static/
    ├── index.html        # Main web interface
    ├── css/
    │   └── style.css     # Styling & glassmorphic dark theme
    └── js/
        └── app.js        # Interactive frontend script
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the single-page application interface. |
| `GET` | `/api/health` | Checks API key configuration & SQLite database connection. |
| `POST` | `/api/generate` | Generates a new email based on category, tone, length, and content. |
| `POST` | `/api/refine` | Improves an existing email (*shorter, formal, friendly, grammar, custom*). |
| `GET` | `/api/history` | Retrieves stored email history items. |
| `POST` | `/api/history/{id}/favorite` | Toggles favorite status for a history entry. |
| `DELETE` | `/api/history/{id}` | Deletes a single history entry. |
| `DELETE` | `/api/history` | Clears all history entries after user confirmation. |

---

## 🚀 Local Setup & Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/abhinav9m/Ai_Email_Generator.git
   cd Ai_Email_Generator
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   PORT=8000
   ```

4. **Start the FastAPI Server**:
   ```bash
   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

5. **Access the Application**:
   Open your browser and navigate to **`http://127.0.0.1:8000`**.
