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
    await fs.mkdir(UPLOAD_DIR, { recursive: true });

    const files = await fs.readdir(UPLOAD_DIR);
    const fileDetails = await Promise.all(
      files.map(async (filename) => {
        const filePath = path.join(UPLOAD_DIR, filename);
        const stats = await fs.stat(filePath);
        
        const fileId = generateFileId(filename, stats.birthtime);
        
        return {
          id: fileId,
          name: filename,
          size: stats.size,
          createdAt: stats.birthtime.toISOString(),
          mimeType: getMimeType(filename),
          path: filePath,
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

// Utility functions
function generateFileId(filename: string, createdAt: Date): string {
  const timestamp = createdAt.getTime();
  const hash = require('crypto')
    .createHash('md5')
    .update(`${filename}-${timestamp}`)
    .digest('hex');
  return hash;
}

function getMimeType(filename: string): string {
  const ext = path.extname(filename).toLowerCase();
  const mimeTypes = {
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.txt': 'text/plain'
  };
  return mimeTypes[ext] || 'application/octet-stream';
} 