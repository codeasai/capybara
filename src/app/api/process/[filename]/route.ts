import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

const UPLOAD_DIR = path.join(process.cwd(), 'uploads');

export async function POST(
  request: NextRequest,
  { params }: { params: { filename: string } }
) {
  try {
    const filename = params.filename;
    const filePath = path.join(UPLOAD_DIR, filename);

    // ตรวจสอบว่าไฟล์มีอยู่จริง
    try {
      await fs.access(filePath);
    } catch {
      return NextResponse.json(
        { error: 'File not found' },
        { status: 404 }
      );
    }

    // สร้าง FormData สำหรับส่งไปที่ FastAPI
    const formData = new FormData();
    const fileBuffer = await fs.readFile(filePath);
    const file = new File([fileBuffer], filename, { type: 'application/pdf' });
    formData.append('file', file);

    // ส่งไฟล์ไปที่ FastAPI server
    const response = await fetch('http://localhost:8000/api/upload-large-pdf', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`FastAPI Error: ${errorData}`);
    }

    return NextResponse.json({ success: true });

  } catch (error) {
    console.error('Processing error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
} 