
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pdfplumber

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

# 🔥 HOME ROUTE
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# 🔥 UPLOAD API (FINAL FIX)
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    text = ""

    try:
        contents = await file.read()  # 🔥 IMPORTANT FIX
        import io

        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        return {"text": text}

    except Exception as e:
        print("ERROR:", e)  # 🔥 Debug log
        return {"text": "", "error": str(e)}
