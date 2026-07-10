from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

import pdfplumber
import sqlite3
import io
import hashlib
import os

import google.generativeai as genai
from passlib.context import CryptContext

# ----------------------------------------------------
# FASTAPI APP
# ----------------------------------------------------

app = FastAPI(
    title="WriteFlow AI",
    version="1.0.0"
)

# ----------------------------------------------------
# GEMINI CONFIG
# ----------------------------------------------------

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# ----------------------------------------------------
# CORS
# ----------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# STATIC FILES
# ----------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory="."),
    name="static",
)

# ----------------------------------------------------
# PASSWORD HASHING
# ----------------------------------------------------

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

# ----------------------------------------------------
# DATABASE
# ----------------------------------------------------

conn = sqlite3.connect(
    "users.db",
    check_same_thread=False,
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)
""")

conn.commit()

# ----------------------------------------------------
# PASSWORD FUNCTIONS
# ----------------------------------------------------

def hash_password(password: str):

    password = password.strip()

    password = hashlib.sha256(
        password.encode()
    ).hexdigest()

    return pwd_context.hash(password)


def verify_password(
    plain: str,
    hashed: str,
):

    plain = plain.strip()

    plain = hashlib.sha256(
        plain.encode()
    ).hexdigest()

    return pwd_context.verify(
        plain,
        hashed,
    )
    # ----------------------------------------------------
# HOME
# ----------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


# ----------------------------------------------------
# PDF UPLOAD
# ----------------------------------------------------

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    text = ""

    try:

        contents = await file.read()

        with pdfplumber.open(io.BytesIO(contents)) as pdf:

            for page in pdf.pages:

                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        return {
            "success": True,
            "text": text
        }

    except Exception as e:

        print("UPLOAD ERROR:", e)

        return {
            "success": False,
            "text": "",
            "error": str(e)
        }


# ----------------------------------------------------
# SIGNUP
# ----------------------------------------------------

@app.post("/signup")
async def signup(
    email: str = Form(...),
    password: str = Form(...)
):

    try:

        email = email.strip().lower()
        password = password.strip()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            return {
                "error": "User already exists ❌"
            }

        hashed_password = hash_password(password)

        cursor.execute(
            "INSERT INTO users(email,password) VALUES(?,?)",
            (
                email,
                hashed_password,
            ),
        )

        conn.commit()

        return {
            "message": "Signup successful ✅"
        }

    except Exception as e:

        print("SIGNUP ERROR:", e)

        return {
            "error": str(e)
        }


# ----------------------------------------------------
# LOGIN
# ----------------------------------------------------

@app.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...)
):

    try:

        email = email.strip().lower()
        password = password.strip()

        cursor.execute(
            "SELECT password FROM users WHERE email=?",
            (email,),
        )

        user = cursor.fetchone()

        if not user:
            return {
                "error": "User not found ❌"
            }

        stored_password = user[0]

        if verify_password(
            password,
            stored_password,
        ):

            return {
                "message": "Login successful ✅"
            }

        return {
            "error": "Wrong password ❌"
        }

    except Exception as e:

        print("LOGIN ERROR:", e)

        return {
            "error": str(e)
        }
        # ----------------------------------------------------
# AI SUMMARY
# ----------------------------------------------------

@app.post("/summary")
async def generate_summary(
    text: str = Form(...)
):
    try:

        prompt = f"""
You are WriteFlow AI.

Create a clean study summary from the following PDF.

Rules:

• Use simple English.
• Use bullet points.
• Highlight important concepts.
• Keep headings.
• Don't add information that is not present.
• If formulas are present, include them.
• If definitions are present, explain them simply.

PDF CONTENT:

{text}
"""

        response = model.generate_content(prompt)

        return {
            "success": True,
            "summary": response.text
        }

    except Exception as e:

        print("SUMMARY ERROR:", e)

        return {
            "success": False,
            "error": str(e)
        }
        # ----------------------------------------------------
# CHAT WITH PDF
# ----------------------------------------------------

@app.post("/ask")
async def ask_ai(
    question: str = Form(...),
    text: str = Form(...)
):
    try:

        prompt = f"""
You are WriteFlow AI.

You are answering questions ONLY from the uploaded PDF.

RULES:

1. Answer ONLY using the PDF.
2. Never make up information.
3. If the answer is not found in the PDF, reply exactly:

"This information is not available in the uploaded PDF."

4. Explain in simple English.
5. If possible, answer using bullet points.
6. If the user asks for an example, give an example ONLY if it exists in the PDF.

------------------------------------
PDF CONTENT
------------------------------------

{text}

------------------------------------
USER QUESTION
------------------------------------

{question}
"""

        response = model.generate_content(prompt)

        return {
            "success": True,
            "answer": response.text
        }

    except Exception as e:

        print("ASK AI ERROR:", e)

        return {
            "success": False,
            "error": str(e)
        }
        # ----------------------------------------------------
# HEALTH CHECK
# ----------------------------------------------------

@app.get("/health")
async def health_check():

    return {
        "status": "online",
        "service": "WriteFlow AI Backend",
        "version": "1.0.0"
    }


# ----------------------------------------------------
# FUTURE FEATURES
# ----------------------------------------------------
#
# Upcoming Endpoints
#
# /notes
# /quiz
# /flashcards
# /translate
# /readaloud
# /explain
# /bookmark
# /history
#
# ----------------------------------------------------
# END OF FILE
# ----------------------------------------------------
