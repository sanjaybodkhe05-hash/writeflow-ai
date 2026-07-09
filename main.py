from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

import pdfplumber
import sqlite3
import io
import hashlib
import google.generativeai as genai
import os
from passlib.context import CryptContext

app = FastAPI()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# 🔥 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 STATIC FILES
app.mount("/static", StaticFiles(directory="."), name="static")

# 🔥 PASSWORD CONFIG
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔥 DATABASE
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)
""")
conn.commit()

# 🔐 HASH FUNCTIONS (FINAL FIX)
def hash_password(password):
    password = password.strip()
    password = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    plain = plain.strip()
    plain = hashlib.sha256(plain.encode()).hexdigest()
    return pwd_context.verify(plain, hashed)

# 🔥 HOME
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# 🔥 PDF UPLOAD
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

        return {"text": text}

    except Exception as e:
        print("UPLOAD ERROR:", e)
        return {"text": "", "error": str(e)}

# 🔥 SIGNUP (FULL FIX)
@app.post("/signup")
async def signup(email: str = Form(...), password: str = Form(...)):
    try:
        email = email.strip().lower()
        password = password.strip()

        # 🔥 CHECK USER
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return {"error": "User already exists ❌"}

        # 🔥 HASH
        hashed_password = hash_password(password)

        # 🔥 INSERT
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, hashed_password)
        )
        conn.commit()

        return {"message": "Signup successful ✅"}

    except Exception as e:
        print("SIGNUP ERROR:", e)
        return {"error": str(e)}   # 🔥 REAL ERROR SHOW

# 🔥 LOGIN
@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    try:
        email = email.strip().lower()
        password = password.strip()

        cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if not user:
            return {"error": "User not found ❌"}

        stored_password = user[0]

        if verify_password(password, stored_password):
            return {"message": "Login successful ✅"}
        else:
            return {"error": "Wrong password ❌"}

    except Exception as e:
        print("LOGIN ERROR:", e)
        return {"error": str(e)}
        #update
