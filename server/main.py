# server/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
import json
import asyncio

app = FastAPI()
pdf_handler = LargePDFHandler()

@app.post("/api/upload-large-pdf")
async def upload_large_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        return {"error": "File must be a PDF"}
    
    # Save file temporarily
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    async def process_streaming():
        try:
            async for result in pdf_handler.process_large_pdf(file_path):
                yield json.dumps(result) + "\n"
        finally:
            # Cleanup
            import os
            if os.path.exists(file_path):
                os.remove(file_path)
    
    return StreamingResponse(
        process_streaming(),
        media_type="application/x-ndjson"
    )

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