# server/services/extraction.py
import asyncio
from typing import AsyncGenerator, Dict, Any
import fitz  # PyMuPDF

class LargePDFHandler:
    async def process_large_pdf(self, file_path: str) -> AsyncGenerator[Dict[str, Any], None]:
        try:
            doc = fitz.open(file_path)
            
            for page_num in range(len(doc)):
                # จำลองการประมวลผลที่ใช้เวลานาน
                await asyncio.sleep(0.5)  
                
                page = doc[page_num]
                text = page.get_text()
                
                yield {
                    "page": page_num + 1,
                    "total_pages": len(doc),
                    "content": text[:200] + "..." if len(text) > 200 else text,
                    "progress": (page_num + 1) / len(doc) * 100
                }
                
            doc.close()
            
        except Exception as e:
            yield {
                "error": f"Error processing PDF: {str(e)}"
            }
