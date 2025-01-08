# server/services/extraction.py
import asyncio
from typing import AsyncGenerator, Dict, Any, List
import fitz  # PyMuPDF
import re
import time
import os
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings
import chromadb

class LargePDFHandler:
    def __init__(self):
        # ใช้ all-MiniLM-L6-v2 model สำหรับสร้าง embeddings แบบ self-host
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # ตั้งค่า ChromaDB
        self.chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="db"
        ))
        
        # สร้างหรือเรียกใช้ collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="elliott_patterns",
            metadata={"description": "Collection for Elliott Wave patterns"}
        )

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """สร้าง embeddings จากข้อความโดยใช้ SentenceTransformer"""
        embeddings = self.model.encode(texts)
        return embeddings.tolist()  # แปลงเป็น list เพื่อให้ใช้กับ ChromaDB ได้

    def extract_patterns(self, text: str) -> List[Dict[str, str]]:
        patterns = []
        
        # ค้นหา patterns หลายรูปแบบ
        pattern_types = {
            r'Pattern:?\s*([^.]*?)(?=\.|$)': 'basic_pattern',
            r'Rule:?\s*([^.]*?)(?=\.|$)': 'rule',
            r'Condition:?\s*([^.]*?)(?=\.|$)': 'condition',
            r'Wave\s+(\d+|[A-C]):?\s*([^.]*?)(?=\.|$)': 'wave_detail'
        }
        
        for pattern_regex, pattern_type in pattern_types.items():
            matches = re.finditer(pattern_regex, text, re.IGNORECASE)
            for match in matches:
                if pattern_type == 'wave_detail':
                    wave_num = match.group(1)
                    pattern_text = match.group(2).strip()
                    if pattern_text:
                        patterns.append({
                            "text": pattern_text,
                            "type": pattern_type,
                            "wave_number": wave_num,
                            "source_text": text[:100]
                        })
                else:
                    pattern_text = match.group(1).strip()
                    if pattern_text:
                        patterns.append({
                            "text": pattern_text,
                            "type": pattern_type,
                            "source_text": text[:100]
                        })
        
        return patterns

    async def process_large_pdf(self, file_path: str) -> AsyncGenerator[Dict[str, Any], None]:
        try:
            doc = fitz.open(file_path)
            full_text = ""
            total_patterns = []
            
            # รวบรวมข้อความทั้งหมด
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                full_text += page_text
                
                yield {
                    "page": page_num + 1,
                    "total_pages": len(doc),
                    "status": "extracting_text",
                    "progress": (page_num + 1) / len(doc) * 30
                }

            # แบ่งข้อความเป็น chunks
            chunk_size = 1000
            chunks = [full_text[i:i + chunk_size] for i in range(0, len(full_text), chunk_size)]

            # ประมวลผลแต่ละ chunk
            for i, chunk in enumerate(chunks):
                patterns = self.extract_patterns(chunk)
                
                if patterns:
                    total_patterns.extend(patterns)
                    # สร้าง embeddings แบบ self-host
                    embeddings = self.create_embeddings([chunk])
                    
                    # เพิ่มข้อมูลลง Chroma
                    self.collection.add(
                        embeddings=embeddings,
                        documents=[chunk],
                        metadatas=[{
                            "patterns": str(patterns),
                            "pattern_count": len(patterns),
                            "pattern_types": [p["type"] for p in patterns],
                            "timestamp": time.time()
                        }],
                        ids=[f"chunk_{i}"]
                    )
                
                yield {
                    "chunk": i + 1,
                    "total_chunks": len(chunks),
                    "patterns_found": len(total_patterns),
                    "status": "processing_patterns",
                    "progress": 30 + ((i + 1) / len(chunks) * 70)
                }

            doc.close()
            self.chroma_client.persist()
            
            yield {
                "status": "completed",
                "progress": 100,
                "total_patterns_found": len(total_patterns),
                "pattern_types": list(set(p["type"] for p in total_patterns))
            }
            
        except Exception as e:
            yield {
                "error": f"Error processing PDF: {str(e)}"
            }

    async def search_similar_patterns(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """ค้นหา patterns ที่คล้ายกับ query"""
        query_embedding = self.create_embeddings([query_text])
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["documents", "metadatas"]
        )
        return results
