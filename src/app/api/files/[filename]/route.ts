import { NextRequest, NextResponse } from 'next/server';
import path from 'path';
import fs from 'fs/promises';

export async function DELETE(
  request: NextRequest,
  context: { params: { filename: string } }
) {
  try {
    const params = await context.params;
    const decodedFilename = decodeURIComponent(params.filename);
    const filePath = path.join(process.cwd(), 'uploads', decodedFilename);

    console.log('Attempting to delete file:', {
      decodedFilename,
      filePath,
      cwd: process.cwd(),
      exists: await fs.access(filePath).then(() => true).catch(() => false)
    });

    try {
      const stats = await fs.stat(filePath);
      if (!stats.isFile()) {
        return NextResponse.json(
          { error: 'Path is not a file' },
          { status: 400 }
        );
      }
    } catch (err) {
      console.error('File not found:', filePath);
      return NextResponse.json(
        { error: 'File not found', path: filePath },
        { status: 404 }
      );
    }

    await fs.unlink(filePath);
    console.log('File successfully deleted:', filePath);
    return NextResponse.json({ 
      message: 'File deleted successfully',
      path: filePath
    });

  } catch (error) {
    console.error('General error:', error);
    return NextResponse.json(
      { error: 'Failed to process request', details: error.message },
      { status: 500 }
    );
  }
} 