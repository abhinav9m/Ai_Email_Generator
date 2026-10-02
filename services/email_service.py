import os
import json
import re
import httpx
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Get API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Gemini models to try in fallback order
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-3.6-flash",
    "gemini-2.5-pro",
    "gemini-flash-latest",
    "gemini-flash-lite-latest"
]

def normalize_recipient(recipient: str) -> str:
    """Normalize raw recipient input into professional format, stripping 'to ', 'dear ', etc."""
    if not recipient or not recipient.strip():
        return "Recipient"
    
    cleaned = recipient.strip()
    # Strip leading prefixes like "to ", "to the ", "for ", "attn: ", "dear "
    cleaned = re.sub(r"^(to\s+the\s+|to\s+|for\s+the\s+|for\s+|attn:\s*|dear\s+)", "", cleaned, flags=re.IGNORECASE).strip()
    
    if not cleaned:
        return "Recipient"

    role_map = {
        "manager": "Manager",
        "hr": "HR Team",
        "hr team": "HR Team",
        "human resources": "HR Team",
        "professor": "Professor",
        "teacher": "Teacher",
        "sir": "Sir",
        "madam": "Madam",
        "sir/madam": "Sir/Madam",
        "team": "Team",
        "recruiter": "Recruiter",
        "hiring manager": "Hiring Manager",
        "client": "Client",
        "customer": "Customer",
        "friend": "Friend",
        "boss": "Manager"
    }

    lower_cleaned = cleaned.lower()
    if lower_cleaned in role_map:
        return role_map[lower_cleaned]

    # Return title-cased name for personal names like "john smith" -> "John Smith"
    return cleaned.title()

def construct_generation_prompt(
    purpose: str,
    recipient: str,
    tone: str,
    length: str,
    user_message: str,
    sender_name: Optional[str] = None
) -> str:
    recip_val = normalize_recipient(recipient)
    sender_val = sender_name.strip() if sender_name and sender_name.strip() else "Sender"

    # Category-specific strict instructions
    category_instructions = {
        "Leave Request": "The email must clearly request leave. Mention reason, dates, or duration ONLY if provided. Do NOT invent medical details, dates, or reasons.",
        "Internship Request": "The email must focus on requesting an internship opportunity. Include skills, education, or availability ONLY if provided by the user.",
        "Job Application": "The email must focus on applying for a job position. Include relevant skills, experience, or qualifications ONLY if provided by the user.",
        "Permission Request": "The email must request permission for a specific event or activity mentioned by the user. Do NOT invent extra details.",
        "Meeting Request": "The email must clearly request a meeting and mention topic/schedule ONLY if provided by the user.",
        "Complaint": "The email must clearly describe the issue and politely request resolution. Do NOT make it unnecessarily aggressive or invent unstated issues.",
        "Follow-up Email": "The email must refer to a previous communication or application ONLY when the user provides that context.",
        "Thank You Email": "The email must express sincere gratitude and state the reason ONLY using user-supplied details.",
        "Apology Email": "The email must provide a professional apology without inventing fake excuses or facts.",
        "Resignation Email": "The email must state resignation professionally. Mention notice period or last date ONLY if provided by the user.",
        "Request for Information": "The email must ask for specific details or information as requested by the user.",
        "Custom Email": "Follow the user's instructions while maintaining clean, professional email structure."
    }

    category_guide = category_instructions.get(purpose, category_instructions["Custom Email"])

    # Strict length word-count ranges
    length_guidelines = {
        "Short": "Target length: 50–80 words total. Concise, crisp, and direct to the point.",
        "Medium": "Target length: 80–150 words total. Balanced structure with context and clear request.",
        "Detailed": "Target length: 150–250 words total. Thorough explanation covering provided background, context, and steps."
    }

    # Strict tone guidelines
    tone_guidelines = {
        "Formal": "Very professional, highly structured executive language and traditional formal etiquette.",
        "Professional": "Clear, efficient, respectful, and standard business tone.",
        "Friendly": "Warm, conversational, approachable, personable, and enthusiastic.",
        "Polite": "Extremely respectful, appreciative, courteous, and soft-worded phrasing.",
        "Direct": "Concise, upfront, goal-oriented, and straightforward without fluff."
    }

    selected_length_guide = length_guidelines.get(length, length_guidelines["Medium"])
    selected_tone_guide = tone_guidelines.get(tone, tone_guidelines["Professional"])

    return f"""You are a professional email writing assistant.

TASK & SPECIFICATIONS:
- Email Category/Purpose: {purpose}
- Category Rule: {category_guide}
- Target Recipient: {recip_val}
- Sender Name: {sender_val}
- Selected Tone: {tone} ({selected_tone_guide})
- Selected Length: {length} ({selected_length_guide})
- User Input / Key Points:
{user_message}

STRICT GENERATION RULES:
1. DO NOT INVENT FACTS: Never invent facts, dates, names, reasons, organizations, job titles, medical information, or other details that were NOT provided by the user. Use ONLY the information supplied above.
2. GREETING: Format greeting using exact normalized recipient: "{recip_val}". Example: "Dear {recip_val}," or "Hi {recip_val},". NEVER write "Dear to {recip_val}" or output bracketed placeholders like [Manager's Name].
3. CLOSING: Sign off using the sender name: "{sender_val}". Example: "Best regards,\n{sender_val}" or "Sincerely,\n{sender_val}". NEVER output bracketed placeholders like [Your Name].
4. RESPECT LENGTH & TONE: Follow the target length range ({length}) and tone ({tone}) strictly.
5. NO EXTRA TEXT: Do not include introductory remarks such as 'Here is your email'. Return ONLY valid raw JSON.

JSON OUTPUT STRUCTURE:
{{
  "subject": "Clear and relevant subject line",
  "greeting": "Dear {recip_val},",
  "body": "The email body strictly following user facts and length limit",
  "closing": "Best regards,\\n{sender_val}"
}}
"""

def construct_refine_prompt(
    current_subject: str,
    current_greeting: str,
    current_body: str,
    current_closing: str,
    action: str,
    custom_instruction: Optional[str] = None
) -> str:
    action_guides = {
        "shorter": "Make the email noticeably more concise (50-80 words) while preserving all original facts.",
        "formal": "Elevate language to formal executive style while preserving all original facts.",
        "friendlier": "Make tone warm and approachable while preserving all original facts.",
        "grammar": "Fix all grammar, punctuation, and structural flow issues without changing any facts."
    }
    
    instruction = action_guides.get(action, custom_instruction or "Improve grammar, clarity, and flow.")

    return f"""You are a professional email writing assistant.
Refine the following existing email according to the improvement goal.

Existing Subject: {current_subject}
Existing Greeting: {current_greeting}
Existing Body: {current_body}
Existing Closing: {current_closing}

Improvement Goal:
{instruction}

STRICT RULES:
- Preserve original purpose, meaning, recipient, sender name, and user-supplied facts.
- DO NOT invent new facts or details that were not in the original email.
- Ensure NO bracketed placeholders remain in the output.
- Output ONLY a valid raw JSON object.

JSON OUTPUT STRUCTURE:
{{
  "subject": "Refined subject line",
  "greeting": "Refined greeting",
  "body": "Refined email body",
  "closing": "Refined sign-off"
}}
"""

async def call_gemini_api(prompt: str, api_key: str = GEMINI_API_KEY) -> str:
    """Call Gemini API via REST endpoint or SDK with fallbacks across models."""
    if not api_key:
        raise ValueError("Gemini API key is not configured in .env file.")
        
    last_error = None

    # Try SDK if available
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        for model in GEMINI_MODELS:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_error = e
                continue
    except Exception:
        pass

    # Fallback to direct HTTP endpoint using httpx
    async with httpx.AsyncClient(timeout=30.0) as client:
        for model in GEMINI_MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.6,
                    "topP": 0.9
                }
            }
            try:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
                else:
                    last_error = f"API Error ({resp.status_code}): {resp.text}"
            except Exception as e:
                last_error = str(e)
                continue

    raise RuntimeError(f"Gemini API request failed: {last_error}")

def clean_placeholders(text: str, recipient: str, sender_name: str) -> str:
    """Replace any lingering bracketed placeholders with actual normalized values."""
    if not text:
        return text
    
    recip = normalize_recipient(recipient)
    sender = sender_name.strip() if sender_name and sender_name.strip() else "Sender"

    # Replace recipient placeholders
    text = re.sub(r"\[(Manager's Name|Recipient's Name|Recipient Name|Recipient|Name)\]", recip, text, flags=re.IGNORECASE)
    # Replace sender placeholders
    text = re.sub(r"\[(Your Name|Sender's Name|Sender Name|Your Title|Title|Sender)\]", sender, text, flags=re.IGNORECASE)
    # Clean double bracketed items
    text = re.sub(r"\[.*?\]", recip, text)
    # Fix awkward "Dear to Manager" or "Dear to "
    text = re.sub(r"Dear\s+to\s+", "Dear ", text, flags=re.IGNORECASE)
    return text

def parse_json_response(raw_text: str) -> Dict[str, str]:
    """Clean markdown code blocks and parse JSON response safely."""
    cleaned = raw_text.strip()
    
    # Remove markdown code block wrappers if present
    cleaned = re.sub(r"^```(json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
        return {
            "subject": data.get("subject", "").strip(),
            "greeting": data.get("greeting", "").strip(),
            "body": data.get("body", "").strip(),
            "closing": data.get("closing", "").strip()
        }
    except Exception:
        subject = re.search(r'"subject"\s*:\s*"(.*?)"', cleaned, re.DOTALL)
        greeting = re.search(r'"greeting"\s*:\s*"(.*?)"', cleaned, re.DOTALL)
        body = re.search(r'"body"\s*:\s*"(.*?)"', cleaned, re.DOTALL)
        closing = re.search(r'"closing"\s*:\s*"(.*?)"', cleaned, re.DOTALL)

        return {
            "subject": subject.group(1).replace("\\n", "\n") if subject else "Generated Email Subject",
            "greeting": greeting.group(1).replace("\\n", "\n") if greeting else "Dear Recipient,",
            "body": body.group(1).replace("\\n", "\n") if body else raw_text,
            "closing": closing.group(1).replace("\\n", "\n") if closing else "Best regards"
        }

async def generate_email(
    purpose: str,
    recipient: str,
    tone: str,
    length: str,
    user_message: str,
    sender_name: Optional[str] = None,
    custom_api_key: Optional[str] = None
) -> Dict[str, str]:
    api_key = custom_api_key.strip() if custom_api_key else GEMINI_API_KEY
    recip_val = normalize_recipient(recipient)
    sender_val = sender_name.strip() if sender_name and sender_name.strip() else "Sender"

    prompt = construct_generation_prompt(purpose, recipient, tone, length, user_message, sender_name)

    try:
        raw_output = await call_gemini_api(prompt, api_key=api_key)
        parsed = parse_json_response(raw_output)
    except Exception as err:
        parsed = generate_fallback_email(purpose, recip_val, tone, user_message, sender_val, str(err))

    # Post-process placeholders and clean double greetings
    parsed["greeting"] = clean_placeholders(parsed["greeting"], recip_val, sender_val)
    if not parsed["greeting"].startswith("Dear") and not parsed["greeting"].startswith("Hi") and not parsed["greeting"].startswith("Hello"):
        parsed["greeting"] = f"Dear {recip_val},"

    parsed["closing"] = clean_placeholders(parsed["closing"], recip_val, sender_val)
    parsed["body"] = clean_placeholders(parsed["body"], recip_val, sender_val)
    parsed["subject"] = clean_placeholders(parsed["subject"], recip_val, sender_val)

    # Format full email text
    full_email = f"Subject: {parsed['subject']}\n\n{parsed['greeting']}\n\n{parsed['body']}\n\n{parsed['closing']}"
    parsed["full_email"] = full_email
    parsed["recipient_normalized"] = recip_val
    return parsed

async def refine_email(
    subject: str,
    greeting: str,
    body: str,
    closing: str,
    action: str,
    custom_instruction: Optional[str] = None,
    custom_api_key: Optional[str] = None,
    recipient: Optional[str] = "",
    sender_name: Optional[str] = ""
) -> Dict[str, str]:
    api_key = custom_api_key.strip() if custom_api_key else GEMINI_API_KEY
    recip_val = normalize_recipient(recipient)
    sender_val = sender_name.strip() if sender_name and sender_name.strip() else "Sender"

    prompt = construct_refine_prompt(subject, greeting, body, closing, action, custom_instruction)
    
    try:
        raw_output = await call_gemini_api(prompt, api_key=api_key)
        parsed = parse_json_response(raw_output)
    except Exception as err:
        parsed = generate_refine_fallback(subject, greeting, body, closing, action, custom_instruction)

    parsed["greeting"] = clean_placeholders(parsed["greeting"], recip_val, sender_val)
    parsed["closing"] = clean_placeholders(parsed["closing"], recip_val, sender_val)
    parsed["body"] = clean_placeholders(parsed["body"], recip_val, sender_val)
    parsed["subject"] = clean_placeholders(parsed["subject"], recip_val, sender_val)

    full_email = f"Subject: {parsed['subject']}\n\n{parsed['greeting']}\n\n{parsed['body']}\n\n{parsed['closing']}"
    parsed["full_email"] = full_email
    parsed["recipient_normalized"] = recip_val
    return parsed

def generate_fallback_email(purpose: str, recipient: str, tone: str, message: str, sender: str, error_msg: str) -> Dict[str, str]:
    recip = recipient if recipient else "Recipient"
    send_name = sender if sender else "Sender"
    
    return {
        "subject": f"{purpose}: Regarding {message[:30]}...",
        "greeting": f"Dear {recip},",
        "body": f"I am writing regarding the following matter:\n\n{message}\n\nPlease let me know if you need any additional information.",
        "closing": f"Best regards,\n{send_name}",
        "api_warning": f"Generated via Smart Engine ({error_msg})"
    }

def generate_refine_fallback(subject: str, greeting: str, body: str, closing: str, action: str, custom: Optional[str]) -> Dict[str, str]:
    if action == "shorter":
        sentences = body.split(". ")
        new_body = ". ".join(sentences[:max(1, len(sentences)//2)])
        if not new_body.endswith("."):
            new_body += "."
        return {"subject": subject, "greeting": greeting, "body": new_body, "closing": closing}
    elif action == "formal":
        return {
            "subject": f"Formal Notice: {subject}",
            "greeting": greeting,
            "body": f"I am writing to formally communicate the following matter:\n\n{body}\n\nThank you for your attention.",
            "closing": closing
        }
    elif action == "friendlier":
        return {
            "subject": subject,
            "greeting": greeting.replace("Dear", "Hi"),
            "body": f"Hope you're having a great day!\n\n{body}\n\nLooking forward to catching up soon!",
            "closing": closing
        }
    elif action == "grammar":
        return {"subject": subject, "greeting": greeting, "body": body.strip(), "closing": closing}
    else:
        return {"subject": subject, "greeting": greeting, "body": f"{body}\n\nNote: {custom}", "closing": closing}
