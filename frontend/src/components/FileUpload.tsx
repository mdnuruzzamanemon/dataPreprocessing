'use client';

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, AlertCircle } from 'lucide-react';
import { uploadFile } from '@/services/dataService';
import { FileInfo } from '@/types';
import { Button } from './ui/Button';
import { Card } from './ui/Card';
import { formatBytes } from '@/utils/helpers';

interface FileUploadProps {
  onUploadSuccess: (fileInfo: FileInfo) => void;
}

export default function FileUpload({ onUploadSuccess }: FileUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    multiple: false,
    maxSize: 100 * 1024 * 1024, // 100MB
  });

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setError(null);

    try {
      const fileInfo = await uploadFile(selectedFile);
      onUploadSuccess(fileInfo);
      setSelectedFile(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload file. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    setError(null);
  };

  return (
    <Card className="p-6">
      <div className="space-y-4">
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
            transition-colors duration-200
            ${isDragActive ? 'border-primary bg-primary/5' : 'border-gray-300 hover:border-primary'}
            ${selectedFile ? 'bg-gray-50' : ''}
          `}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <p className="text-lg font-medium mb-2">
            {isDragActive ? 'Drop your file here' : 'Drag & drop your dataset'}
          </p>
          <p className="text-sm text-gray-500 mb-4">
            or click to browse
          </p>
          <p className="text-xs text-gray-400">
            Supports CSV, XLS, XLSX (Max 100MB)
          </p>
        </div>

        {selectedFile && (
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <File className="h-8 w-8 text-primary" />
              <div>
                <p className="font-medium">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">{formatBytes(selectedFile.size)}</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={removeFile}
              disabled={uploading}
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
        )}

        {error && (
          <div className="flex items-start space-x-2 p-4 bg-red-50 border border-red-200 rounded-lg">
            <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {selectedFile && (
          <Button
            onClick={handleUpload}
            disabled={uploading}
            className="w-full"
            size="lg"
          >
            {uploading ? 'Uploading...' : 'Upload and Analyze'}
          </Button>
        )}
      </div>
    </Card>
  );
}
