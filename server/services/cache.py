from typing import Dict
import asyncio

# ใพิ่มสถานะที่เป็นไปได้ทั้งหมด
class ProcessingStatus:
    NOT_FOUND = "not_found"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"

# ใช้ dict ง่ายๆ เป็น in-memory cache
processing_status: Dict[str, str] = {}

async def set_processing_status(file_id: str, status: str) -> None:
    processing_status[file_id] = status

async def get_processing_status_from_cache(file_id: str) -> dict:
    return {
        "file_id": file_id,
        "status": processing_status.get(file_id, ProcessingStatus.NOT_FOUND)
    }

async def cancel_processing_task(file_id: str) -> None:
    if file_id in processing_status:
        processing_status[file_id] = ProcessingStatus.CANCELLED 