from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

import pdfplumber
import sqlite3
import io
import hashlib  # 🔥 ADD THIS
from passlib.context import CryptContext

app = FastAPI()

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

# 🔥 DATABASE SETUP
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

# 🔐 HASH FUNCTIONS (🔥 FIXED)
def hash_password(password):
    # 🔥 FIX: convert to fixed length before bcrypt
    password = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    plain = hashlib.sha256(plain.encode()).hexdigest()
    return pwd_context.verify(plain, hashed)

# 🔥 HOME ROUTE
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# 🔥 UPLOAD API
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

# 🔥 SIGNUP API
@app.post("/signup")
async def signup(email: str = Form(...), password: str = Form(...)):
    try:
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return {"error": "User already exists ❌"}

        hashed_password = hash_password(password)

        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, hashed_password)
        )
        conn.commit()

        return {"message": "Signup successful ✅"}

    except Exception as e:
        print("SIGNUP ERROR:", e)
        return {"error": str(e)}

# 🔥 LOGIN API
@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    try:
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
