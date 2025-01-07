# server/services/extraction.py
from typing import List, Dict, Generator
import pypdf
from tqdm import tqdm
import asyncio
from concurrent.futures import ThreadPoolExecutor

class LargePDFHandler:
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def extract_text_with_progress(self, file_path: str) -> Generator[Dict, None, None]:
        def process_page(page) -> str:
            try:
                return page.extract_text()
            except Exception as e:
                return f"Error extracting page: {str(e)}"

        with open(file_path, "rb") as file:
            pdf = pypdf.PdfReader(file)
            total_pages = len(pdf.pages)

            # Process pages in batches
            batch_size = 10
            for start_idx in range(0, total_pages, batch_size):
                end_idx = min(start_idx + batch_size, total_pages)
                batch_pages = pdf.pages[start_idx:end_idx]
                
                # Process batch of pages concurrently
                tasks = [
                    self.executor.submit(process_page, page)
                    for page in batch_pages
                ]
                
                # Collect results
                for i, future in enumerate(tasks):
                    page_num = start_idx + i + 1
                    text = future.result()
                    
                    yield {
                        "page": page_num,
                        "text": text,
                        "progress": (page_num / total_pages) * 100
                    }

    async def process_large_pdf(self, file_path: str) -> List[Dict]:
        chunks = []
        current_chunk = ""
        current_metadata = {"pages": []}

        async for page_data in self.extract_text_with_progress(file_path):
            text = page_data["text"]
            page_num = page_data["page"]
            
            # Split text into chunks
            words = text.split()
            for word in words:
                current_chunk += word + " "
                if len(current_chunk) >= self.chunk_size:
                    chunks.append({
                        "text": current_chunk.strip(),
                        "metadata": {
                            "pages": current_metadata["pages"],
                            "start_page": min(current_metadata["pages"]),
                            "end_page": max(current_metadata["pages"])
                        }
                    })
                    current_chunk = ""
                    current_metadata = {"pages": []}
            
            current_metadata["pages"].append(page_num)
            
            # Yield progress
            yield {
                "status": "processing",
                "progress": page_data["progress"],
                "current_page": page_num,
                "chunks_created": len(chunks)
            }

        # Add final chunk if any
        if current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "metadata": {
                    "pages": current_metadata["pages"],
                    "start_page": min(current_metadata["pages"]),
                    "end_page": max(current_metadata["pages"])
                }
            })

        yield {
            "status": "complete",
            "chunks": chunks,
            "total_chunks": len(chunks)
        }
