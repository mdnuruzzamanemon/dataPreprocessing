'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import DashboardLayout from '@/components/DashboardLayout';
import { apiClient } from '@/services/api';

interface FileItem {
    id: string;
    file_id: string;
    filename: string;
    file_size: number;
    file_type: string;
    status: string;
    uploaded_at: string;
}

export default function FilesPage() {
    const router = useRouter();
    const { user, loading } = useAuth();
    const [files, setFiles] = useState<FileItem[]>([]);
    const [loadingFiles, setLoadingFiles] = useState(true);

    useEffect(() => {
        if (!loading && !user) {
            router.push('/login');
        } else if (user) {
            fetchFiles();
        }
    }, [user, loading, router]);

    const fetchFiles = async () => {
        try {
            const response = await apiClient.get('/api/files/');
            setFiles(response.data);
        } catch (error) {
            console.error('Failed to fetch files:', error);
        } finally {
            setLoadingFiles(false);
        }
    };

    const formatFileSize = (bytes: number) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const handleView = (fileId: string) => {
        router.push(`/dashboard/results?fileId=${fileId}`);
    };

    const handleDownload = (fileId: string, filename: string) => {
        const token = localStorage.getItem('access_token');
        const downloadUrl = `http://localhost:8000/api/download/${fileId}?token=${encodeURIComponent(token || '')}`;
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const handleDelete = async (fileId: string, filename: string) => {
        if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
            return;
        }

        try {
            await apiClient.delete(`/api/files/${fileId}`);
            alert('File deleted successfully');
            fetchFiles();
        } catch (error) {
            console.error('Delete failed:', error);
            alert('Failed to delete file');
        }
    };

    if (loading || !user) {
        return null;
    }

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">My Files</h1>
                    <p className="mt-2 text-gray-600">View and manage your uploaded files</p>
                </div>

                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h2 className="text-lg font-semibold text-gray-900">Recent Uploads</h2>
                    </div>

                    <div className="p-6">
                        {loadingFiles ? (
                            <div className="text-center py-12">
                                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                                <p className="mt-4 text-gray-600">Loading files...</p>
                            </div>
                        ) : files.length === 0 ? (
                            <div className="text-center py-12">
                                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                <h3 className="mt-4 text-sm font-medium text-gray-900">No files yet</h3>
                                <p className="mt-2 text-sm text-gray-500">Upload your first file to get started</p>
                                <button onClick={() => router.push('/dashboard')} className="mt-4 inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
                                    Upload File
                                </button>
                            </div>
                        ) : (
                            <div className="overflow-x-auto">
                                <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                        <tr>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Filename</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Size</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Uploaded</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                        {files.map((file) => (
                                            <tr key={file.id} className="hover:bg-gray-50">
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <div className="flex items-center">
                                                        <div className="flex-shrink-0 h-10 w-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                                                            <svg className="h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                                            </svg>
                                                        </div>
                                                        <div className="ml-4 flex-1">
                                                            <div className="flex items-center gap-2">
                                                                <div className="text-sm font-medium text-gray-900">{file.filename}</div>
                                                                {file.status === 'processed' && (
                                                                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                                                                        <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                                                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                                                        </svg>
                                                                        Processed
                                                                    </span>
                                                                )}
                                                            </div>
                                                            <div className="text-sm text-gray-500">{file.file_type}</div>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatFileSize(file.file_size)}</td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${file.status === 'processed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                                                        }`}>
                                                        {file.status}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatDate(file.uploaded_at)}</td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-3">
                                                    <button onClick={() => handleView(file.file_id)} className="text-indigo-600 hover:text-indigo-900">View</button>
                                                    <button onClick={() => handleDownload(file.file_id, file.filename)} className="text-blue-600 hover:text-blue-900">Download</button>
                                                    <button onClick={() => handleDelete(file.file_id, file.filename)} className="text-red-600 hover:text-red-900">Delete</button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
