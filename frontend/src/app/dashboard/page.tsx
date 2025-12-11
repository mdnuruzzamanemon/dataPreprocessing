'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import DashboardLayout from '@/components/DashboardLayout';
import { uploadFile } from '@/services/dataService';
import { apiClient } from '@/services/api';
import { Upload, FileText, CheckCircle, Database } from 'lucide-react';

export default function DashboardPage() {
    const router = useRouter();
    const { user, loading } = useAuth();
    const [uploading, setUploading] = useState(false);
    const [dragActive, setDragActive] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [stats, setStats] = useState({
        totalFiles: 0,
        processedFiles: 0,
        storageUsed: 0
    });

    useEffect(() => {
        if (!loading && !user) {
            router.push('/login');
        } else if (user) {
            fetchStats();
        }
    }, [user, loading, router]);

    const fetchStats = async () => {
        try {
            const response = await apiClient.get('/api/files/');
            const files = response.data;

            const totalFiles = files.length;
            const processedFiles = files.filter((f: any) => f.status === 'processed').length;
            const storageUsed = files.reduce((sum: number, f: any) => sum + (f.file_size || 0), 0);

            setStats({
                totalFiles,
                processedFiles,
                storageUsed
            });
        } catch (error) {
            console.error('Failed to fetch stats:', error);
        }
    };

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = async (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            await handleFileUpload(e.dataTransfer.files[0]);
        }
    };

    const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            await handleFileUpload(e.target.files[0]);
        }
    };

    const handleFileUpload = async (file: File) => {
        try {
            setUploading(true);
            const result = await uploadFile(file);
            router.push(`/dashboard/results?fileId=${result.file_id}`);
            fetchStats(); // Refresh stats after upload
        } catch (error: any) {
            alert(error.message || 'Upload failed');
        } finally {
            setUploading(false);
        }
    };

    const onButtonClick = () => {
        fileInputRef.current?.click();
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading...</p>
                </div>
            </div>
        );
    }

    if (!user) {
        return null;
    }

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Welcome back, {user.username}!</h1>
                    <p className="mt-2 text-gray-600">Upload and preprocess your data files</p>
                </div>

                {/* Upload Section */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Data File</h2>
                    <p className="text-gray-600 mb-6">
                        Upload your CSV or Excel file to start preprocessing
                    </p>

                    <div
                        className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer ${dragActive
                            ? 'border-indigo-500 bg-indigo-50'
                            : 'border-gray-300 hover:border-indigo-400'
                            } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                        onClick={onButtonClick}
                    >
                        <input
                            ref={fileInputRef}
                            type="file"
                            className="hidden"
                            accept=".csv,.xlsx,.xls"
                            onChange={handleChange}
                            disabled={uploading}
                        />

                        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                        <p className="text-lg font-medium text-gray-900 mb-2">
                            {uploading ? 'Uploading...' : 'Drop your file here or click to browse'}
                        </p>
                        <p className="text-sm text-gray-500">
                            Supports CSV, XLSX, and XLS files
                        </p>
                    </div>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 mt-8">
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Total Files</p>
                                <p className="text-2xl sm:text-3xl font-bold text-gray-900 mt-1">{stats.totalFiles}</p>
                            </div>
                            <div className="bg-indigo-100 p-3 rounded-lg">
                                <FileText className="h-6 w-6 sm:h-8 sm:w-8 text-indigo-600" />
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Processed</p>
                                <p className="text-2xl sm:text-3xl font-bold text-gray-900 mt-1">{stats.processedFiles}</p>
                            </div>
                            <div className="bg-green-100 p-3 rounded-lg">
                                <CheckCircle className="h-6 w-6 sm:h-8 sm:w-8 text-green-600" />
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Storage Used</p>
                                <p className="text-2xl sm:text-3xl font-bold text-gray-900 mt-1">
                                    {(stats.storageUsed / (1024 * 1024)).toFixed(1)} MB
                                </p>
                            </div>
                            <div className="bg-blue-100 p-3 rounded-lg">
                                <Database className="h-6 w-6 sm:h-8 sm:w-8 text-blue-600" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
