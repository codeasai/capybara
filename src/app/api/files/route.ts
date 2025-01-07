import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

const UPLOAD_DIR = path.join(process.cwd(), 'uploads');

// สร้าง directory
export async function POST(request: NextRequest) {
  try {
    const { name } = await request.json();
    const dirPath = path.join(UPLOAD_DIR, name);
    
    await fs.mkdir(dirPath, { recursive: true });
    
    return NextResponse.json({
      id: Date.now().toString(),
      name,
      path: dirPath,
      type: 'directory'
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to create directory' },
      { status: 500 }
    );
  }
}

// ลบไฟล์หรือ directory
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const filePath = searchParams.get('path');
    
    if (!filePath) {
      return NextResponse.json(
        { error: 'Path is required' },
        { status: 400 }
      );
    }

    await fs.rm(path.join(UPLOAD_DIR, filePath), { recursive: true });
    
    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to delete file' },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    // สร้างโฟลเดอร์ถ้ายังไม่มี
    await fs.mkdir(UPLOAD_DIR, { recursive: true });

    const files = await fs.readdir(UPLOAD_DIR);
    const fileDetails = await Promise.all(
      files.map(async (filename) => {
        const filePath = path.join(UPLOAD_DIR, filename);
        const stats = await fs.stat(filePath);
        
        return {
          id: filename,
          name: filename,
          size: stats.size,
          createdAt: stats.birthtime.toISOString(),
        };
      })
    );

    return NextResponse.json(fileDetails);
  } catch (error) {
    console.error('Error reading files:', error);
    return NextResponse.json(
      { error: 'Failed to read files' },
      { status: 500 }
    );
  }
} 