"use client";

import { useState } from 'react';
import { Upload, FileText, ChevronRight, FolderOpen } from 'lucide-react';
import { useRouter } from 'next/navigation';
import FileUploadComponent from '@/components/upload/file-upload-component';

export default function Home() {
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const router = useRouter();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Text Extraction and Analysis Tool
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Extract, analyze, and process text from PDF documents using advanced chunking techniques
        </p>
        <div className="flex justify-center gap-4">
          <button 
            onClick={() => setIsUploadOpen(true)}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <Upload className="h-5 w-5 mr-2" />
            Start Processing
            <ChevronRight className="h-5 w-5 ml-2" />
          </button>
          <button 
            onClick={() => router.push('/files')}
            className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <FolderOpen className="h-5 w-5 mr-2" />
            View Files
          </button>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="bg-blue-100 rounded-full w-12 h-12 flex items-center justify-center mb-4">
            <Upload className="h-6 w-6 text-blue-600" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Large File Support
          </h3>
          <p className="text-gray-600">
            Process PDFs up to hundreds of pages with real-time progress tracking
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="bg-blue-100 rounded-full w-12 h-12 flex items-center justify-center mb-4">
            <FileText className="h-6 w-6 text-blue-600" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Smart Chunking
          </h3>
          <p className="text-gray-600">
            Intelligent text splitting with customizable chunk sizes and overlap
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="bg-blue-100 rounded-full w-12 h-12 flex items-center justify-center mb-4">
            <FileText className="h-6 w-6 text-blue-600" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Export & Analysis
          </h3>
          <p className="text-gray-600">
            Export processed chunks with metadata and detailed analysis options
          </p>
        </div>
      </div>

      {/* Upload Dialog */}
      <FileUploadComponent
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
      />
    </div>
  );
}