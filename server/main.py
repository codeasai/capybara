# server/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import os
import time
from server.services.extraction import LargePDFHandler
from server.services.cache import (
    get_processing_status_from_cache, 
    cancel_processing_task, 
    set_processing_status, 
    ProcessingStatus
)
import uvicorn

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("FastAPI server is running!")
    print("Available endpoints:")
    print("  - GET  /api/health")
    print("  - POST /api/upload-large-pdf")
    print("  - GET  /api/processing-status/{file_id}")
    print("  - POST /api/cancel-processing/{file_id}")

# เพิ่ม CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # อนุญาต Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pdf_handler = LargePDFHandler()

@app.post("/api/upload-large-pdf")
async def upload_large_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        return {"error": "File must be a PDF"}
        
    # ตรวจสอบขนาดไฟล์ (จำกัดที่ 50MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        return {"error": "File size exceeds 50MB limit"}
    
    file_id = f"{file.filename}_{int(time.time())}"
    
    # เปลี่ยนเส้นทางไฟล์ไปยัง src/uploads/
    upload_dir = "src/uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_path = os.path.join(upload_dir, file.filename)
    
    try:
        await set_processing_status(file_id, ProcessingStatus.PROCESSING)
        
        # Save file to uploads directory
        try:
            with open(file_path, "wb") as buffer:
                buffer.write(content)
        except Exception as e:
            await set_processing_status(file_id, ProcessingStatus.ERROR)
            return {"error": f"Failed to save file: {str(e)}"}
            
        if not os.path.exists(file_path):
            await set_processing_status(file_id, ProcessingStatus.ERROR)
            return {"error": "Failed to save uploaded file"}
            
        async def process_streaming():
            try:
                async for result in pdf_handler.process_large_pdf(file_path):
                    if "error" in result:
                        await set_processing_status(file_id, ProcessingStatus.ERROR)
                        yield json.dumps({"error": result["error"]}) + "\n"
                        return
                    yield json.dumps(result) + "\n"
                await set_processing_status(file_id, ProcessingStatus.COMPLETED)
            except Exception as e:
                await set_processing_status(file_id, ProcessingStatus.ERROR)
                yield json.dumps({"error": str(e)}) + "\n"
            finally:
                # ไม่ลบไฟล์หลังจากประมวลผลเสร็จ เพราะต้องการเก็บไว้ใน uploads
                pass
        
        return StreamingResponse(
            process_streaming(),
            media_type="application/x-ndjson"
        )
        
    except Exception as e:
        await set_processing_status(file_id, ProcessingStatus.ERROR)
        return {"error": str(e)}

@app.get("/api/processing-status/{file_id}")
async def get_processing_status(file_id: str):
    # Get status from cache/database
    status = await get_processing_status_from_cache(file_id)
    return status

@app.post("/api/cancel-processing/{file_id}")
async def cancel_processing(file_id: str):
    # Cancel processing if needed
    await cancel_processing_task(file_id)
    return {"status": "cancelled"}

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("server.main:app", 
                host="127.0.0.1",    # เพิ่มการระบุ host
                port=8000,           # ระบุ port
                reload=True)