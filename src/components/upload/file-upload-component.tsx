"use client";

import { useState } from 'react';
import { Upload, FileText, Check, AlertCircle, X } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import FileManager from './file-manager';

interface FileUploadProps {
  isOpen: boolean;
  onClose: () => void;
}

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB in bytes

const FileUploadComponent = ({ isOpen, onClose }: FileUploadProps) => {
  const [file, setFile] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [status, setStatus] = useState({ type: '', message: '' });
  const [uploadPath, setUploadPath] = useState('');
  const [showFileManager, setShowFileManager] = useState(false);

  const handleFileUpload = async (event) => {
    const uploadedFile = event.target.files[0];
    if (!uploadedFile) return;
    
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain'
    ];
    
    if (!allowedTypes.includes(uploadedFile.type)) {
      setStatus({
        type: 'error',
        message: 'Invalid file type. Please upload PDF, DOC, DOCX, or TXT files only.'
      });
      return;
    }

    if (uploadedFile.size > MAX_FILE_SIZE) {
      setStatus({ 
        type: 'error', 
        message: 'File size exceeds 50MB limit' 
      });
      return;
    }
    
    setFile(uploadedFile);
    setProcessing(true);
    setStatus({ type: 'info', message: 'Processing file...' });

    const formData = new FormData();
    formData.append('file', uploadedFile);
    formData.append('filename', uploadedFile.name);

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');

      const result = await response.json();
      setUploadPath(result.path);
      setStatus({ 
        type: 'success', 
        message: `File uploaded successfully to: ${result.path}` 
      });
      
      // แสดง success message 2 วินาที แล้วเปิด FileManager
      setTimeout(() => {
        handleClose();
        setShowFileManager(true);
      }, 2000);

    } catch (error) {
      setStatus({ 
        type: 'error', 
        message: 'Error uploading file: ' + error.message 
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleClose = () => {
    // รีเซ็ตค่าทั้งหมดเมื่อปิด popup
    setFile(null);
    setStatus({ type: '', message: '' });
    setUploadPath('');
    setProcessing(false);
    onClose();
  };

  const handleFileManagerClose = () => {
    setShowFileManager(false);
  };

  return (
    <>
      <Dialog open={isOpen} onOpenChange={handleClose}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Upload Document</DialogTitle>
            <button
              onClick={handleClose}
              className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground"
            >
              <X className="h-4 w-4" />
              <span className="sr-only">Close</span>
            </button>
          </DialogHeader>

          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <input
              type="file"
              onChange={handleFileUpload}
              className="hidden"
              id="file-upload"
              accept=".pdf,.doc,.docx,.txt"
            />
            <label 
              htmlFor="file-upload"
              className="flex flex-col items-center cursor-pointer"
            >
              <Upload className="w-12 h-12 text-gray-400" />
              <span className="mt-2 text-sm text-gray-600">
                {file ? file.name : 'Upload your document'}
              </span>
            </label>

            {status.message && (
              <Alert className="mt-4" variant={status.type === 'error' ? 'destructive' : 'default'}>
                <AlertDescription className="flex items-center gap-2">
                  {status.type === 'success' && <Check className="w-4 h-4" />}
                  {status.type === 'error' && <AlertCircle className="w-4 h-4" />}
                  {status.message}
                </AlertDescription>
              </Alert>
            )}

            {processing && (
              <div className="mt-4 flex items-center justify-center">
                <FileText className="w-5 h-5 animate-pulse text-blue-500" />
                <span className="ml-2 text-sm text-gray-600">Processing...</span>
              </div>
            )}
          </div>

          <div className="mt-4 flex justify-end gap-3">
            <button
              onClick={handleClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              disabled={processing}
            >
              Cancel
            </button>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={showFileManager} onOpenChange={handleFileManagerClose}>
        <DialogContent className="sm:max-w-4xl">
          <DialogHeader>
            <DialogTitle>File Manager</DialogTitle>
            <button
              onClick={handleFileManagerClose}
              className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground"
            >
              <X className="h-4 w-4" />
              <span className="sr-only">Close</span>
            </button>
          </DialogHeader>
          
          <FileManager />
        </DialogContent>
      </Dialog>
    </>
  );
};

export default FileUploadComponent;
