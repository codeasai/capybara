"use client";

import { useState, useEffect } from 'react';
import { File, Trash2, Loader2, Home, Upload } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { formatDistanceToNow } from 'date-fns';
import { useRouter } from 'next/navigation';

interface FileItem {
  id: string;
  name: string;
  size: number;
  createdAt: string;
}

const FileManager = () => {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const fetchFiles = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/files');
      if (!response.ok) throw new Error('Failed to fetch files');
      const data = await response.json();
      setFiles(data);
      setError('');
    } catch (err) {
      setError('Failed to load files');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const deleteFile = async (filename: string) => {
    if (!confirm('Are you sure you want to delete this file?')) return;

    try {
      const response = await fetch(`/api/files/${filename}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to delete file');
      }

      // รีเฟรชรายการไฟล์หลังลบสำเร็จ
      await fetchFiles();
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete file');
      console.error(err);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
        <span className="ml-2">Loading files...</span>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Navigation Bar */}
      <div className="flex justify-between items-center mb-8">
        <button
          onClick={() => router.push('/')}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50"
        >
          <Home className="h-5 w-5 mr-2" />
          Back to Home
        </button>
        <button
          onClick={() => router.push('/?upload=true')}
          className="inline-flex items-center px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700"
        >
          <Upload className="h-5 w-5 mr-2" />
          Upload New File
        </button>
      </div>

      <div className="bg-white rounded-lg shadow">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800">Uploaded Files</h2>
        </div>

        {/* File List */}
        <div className="divide-y divide-gray-200">
          {files.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              No files uploaded yet
            </div>
          ) : (
            files.map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-6 hover:bg-gray-50"
              >
                <div className="flex items-center space-x-4">
                  <File className="w-6 h-6 text-blue-500" />
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">
                      {file.name}
                    </h3>
                    <div className="flex space-x-4 text-sm text-gray-500">
                      <span>{formatFileSize(file.size)}</span>
                      <span>•</span>
                      <span>
                        Uploaded {formatDistanceToNow(new Date(file.createdAt))} ago
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => deleteFile(file.id)}
                    className="p-2 text-gray-400 hover:text-red-500 rounded-full hover:bg-gray-100"
                    title="Delete file"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Error Message */}
        {error && (
          <Alert variant="destructive" className="m-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
      </div>
    </div>
  );
};

export default FileManager; 