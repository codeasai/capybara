import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# โหลดค่าจาก .env file
load_dotenv()

# สร้าง FastAPI app
app = FastAPI()

# ตั้งค่า CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # หรือระบุ domain ที่อนุญาต
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# อ่านค่า config จาก .env
HOST = os.getenv("FASTAPI_HOST", "localhost")
PORT = int(os.getenv("FASTAPI_PORT", 8000))
RELOAD = os.getenv("FASTAPI_RELOAD", "True").lower() == "true"

@app.get("/")
async def root():
    return {"message": "FastAPI is running"}

@app.post("/api/upload-large-pdf")
async def upload_large_pdf(file: UploadFile = File(...)):
    try:
        # จัดการไฟล์ที่อัพโหลด
        content = await file.read()
        # เพิ่มโค้ดสำหรับประมวลผลไฟล์ PDF ตรงนี้
        return {"filename": file.filename, "status": "success"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(f"Starting FastAPI server on http://{HOST}:{PORT}")
    uvicorn.run(
        "fastapi-run:app",
        host=HOST,
        port=PORT,
        reload=RELOAD
    ) 