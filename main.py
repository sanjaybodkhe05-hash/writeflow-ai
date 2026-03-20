from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pdfplumber
import pytesseract

# 🔥 Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = FastAPI()

# 🔥 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 STATIC FILES (IMPORTANT FIX)
app.mount("/static", StaticFiles(directory="."), name="static")


# 🔥 Serve HTML
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


# 🔥 Upload API
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    text = ""
    contains_diagram = False

    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"
            else:
                contains_diagram = True
                img = page.to_image(resolution=300)
                pil_img = img.original

                ocr_text = pytesseract.image_to_string(pil_img)
                text += ocr_text + "\n"

    if contains_diagram:
        text += "\n[!] Some pages used OCR (may include diagrams)."

    return {"text": text}
