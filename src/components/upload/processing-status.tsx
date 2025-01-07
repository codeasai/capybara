import React from 'react';
import { Progress } from '@/components/ui/progress';
import { FileText, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

const ProcessingStatus = ({ status }) => {
  const { progress, current_page, total_pages, chunks_created, error } = status;

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="w-full space-y-4 p-4 bg-white rounded-lg shadow">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Processing PDF</h3>
        <span className="text-sm text-gray-500">{progress.toFixed(1)}%</span>
      </div>

      <Progress value={progress} className="w-full" />

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-gray-500">Current Page:</span>
          <span className="ml-2 font-medium">{current_page} / {total_pages}</span>
        </div>
        <div>
          <span className="text-gray-500">Chunks Created:</span>
          <span className="ml-2 font-medium">{chunks_created}</span>
        </div>
      </div>

      {progress < 100 && (
        <div className="flex items-center justify-center gap-2 text-blue-500">
          <FileText className="h-4 w-4 animate-pulse" />
          <span className="text-sm">Processing page {current_page}...</span>
        </div>
      )}
    </div>
  );
};

export default ProcessingStatus;