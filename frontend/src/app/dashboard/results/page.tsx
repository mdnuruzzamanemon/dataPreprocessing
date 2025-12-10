'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import DashboardLayout from '@/components/DashboardLayout';
import FileUpload from '@/components/FileUpload';
import DataSummary from '@/components/DataSummary';
import IssueList from '@/components/IssueList';
import ImbalancedDataModal from '@/components/ImbalancedDataModal';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import {
    FileInfo,
    AnalysisResponse,
    DataIssue,
    PreprocessAction,
} from '@/types';
import {
    analyzeFile,
    fixAllIssues,
    fixImbalancedData,
    preprocessFile,
    downloadFile,
} from '@/services/dataService';
import { Loader2, Download, Sparkles, RefreshCw, Upload } from 'lucide-react';

export default function ResultsPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const { user, loading: authLoading } = useAuth();
    const initialFileId = searchParams.get('fileId');

    const [fileInfo, setFileInfo] = useState<FileInfo | null>(null);
    const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
    const [analyzing, setAnalyzing] = useState(false);
    const [processing, setProcessing] = useState(false);
    const [selectedActions, setSelectedActions] = useState<PreprocessAction[]>([]);
    const [processedFileId, setProcessedFileId] = useState<string | null>(null);
    const [showImbalancedModal, setShowImbalancedModal] = useState(false);
    const [imbalancedColumns, setImbalancedColumns] = useState<string[]>([]);

    useEffect(() => {
        if (!authLoading && !user) {
            router.push('/login');
        }
    }, [user, authLoading, router]);

    useEffect(() => {
        if (initialFileId && user) {
            const fileInfoObj: FileInfo = {
                file_id: initialFileId,
                filename: 'Uploaded File',
                file_size: 0,
                file_type: 'csv',
            };
            setFileInfo(fileInfoObj);
            handleAnalyze(initialFileId);
        }
    }, [initialFileId, user]);

    const handleAnalyze = async (fileId: string) => {
        setAnalyzing(true);
        try {
            const analysisResult = await analyzeFile(fileId);
            setAnalysis(analysisResult);

            // Update fileInfo with data from analysis
            if (analysisResult.file_info) {
                setFileInfo(analysisResult.file_info);
            }
        } catch (error) {
            console.error('Analysis error:', error);
            alert('Failed to analyze file');
        } finally {
            setAnalyzing(false);
        }
    };

    const handleUploadSuccess = async (uploadedFileInfo: FileInfo) => {
        setFileInfo(uploadedFileInfo);
        setAnalysis(null);
        setSelectedActions([]);
        setProcessedFileId(null);
        router.push(`/dashboard/results?fileId=${uploadedFileInfo.file_id}`);
        await handleAnalyze(uploadedFileInfo.file_id);
    };

    const handleSelectAction = (issue: DataIssue, method: string) => {
        const action: PreprocessAction = {
            issue_type: issue.type,
            columns: issue.affected_columns,
            method: method.toLowerCase().replace(/\s+/g, '_'),
            parameters: {},
        };

        const existingIndex = selectedActions.findIndex(
            (a) => a.issue_type === issue.type
        );

        if (existingIndex >= 0) {
            const newActions = [...selectedActions];
            newActions[existingIndex] = action;
            setSelectedActions(newActions);
        } else {
            setSelectedActions([...selectedActions, action]);
        }
    };

    const handleFixAll = async () => {
        if (!fileInfo) return;

        setProcessing(true);
        try {
            const result = await fixAllIssues(fileInfo.file_id);
            setProcessedFileId(result.file_id);

            const newAnalysis = await analyzeFile(result.file_id);
            setAnalysis(newAnalysis);

            if (result.summary?.has_imbalanced_data && result.summary?.imbalanced_columns?.length > 0) {
                let columnsArray: string[] = result.summary.imbalanced_columns || [];
                if (columnsArray.length === 0 && newAnalysis) {
                    const uniqueColumns = new Set<string>();
                    newAnalysis.issues.forEach(issue => {
                        issue.affected_columns.forEach(col => uniqueColumns.add(col));
                    });
                    columnsArray = Array.from(uniqueColumns);
                }
                setImbalancedColumns(columnsArray);
                setShowImbalancedModal(true);
                alert(`Preprocessing complete! ${result.applied_actions.length} actions applied.`);
            } else {
                alert(`Successfully processed! ${result.applied_actions.length} actions applied. Remaining issues: ${newAnalysis.total_issues}`);
            }
        } catch (error: any) {
            console.error('Fix all error:', error);
            alert(error.response?.data?.detail || 'Failed to process file');
        } finally {
            setProcessing(false);
        }
    };

    const handleApplyImbalancedFix = async (targetColumn: string, method: string) => {
        if (!processedFileId) return;

        try {
            await fixImbalancedData(processedFileId, targetColumn, method);
            const newAnalysis = await analyzeFile(processedFileId);
            setAnalysis(newAnalysis);
            alert(`Imbalanced data fix applied successfully!`);
        } catch (error: any) {
            console.error('Imbalanced fix error:', error);
            alert(error.response?.data?.detail || 'Failed to apply imbalanced data fix');
            throw error;
        }
    };

    const handleSkipImbalancedFix = () => {
        setShowImbalancedModal(false);
    };

    const handleApplySelected = async () => {
        if (!fileInfo || selectedActions.length === 0) return;

        setProcessing(true);
        try {
            const result = await preprocessFile(fileInfo.file_id, {
                actions: selectedActions,
            });
            setProcessedFileId(result.file_id);

            if (result.analysis) {
                setAnalysis(result.analysis);
                alert(`Successfully processed! ${result.applied_actions.filter((a) => a.status === 'success').length} actions applied.`);
            } else {
                const newAnalysis = await analyzeFile(result.file_id);
                setAnalysis(newAnalysis);
                alert(`Successfully processed!`);
            }

            setSelectedActions([]);
        } catch (error: any) {
            console.error('Apply selected error:', error);
            alert(error.response?.data?.detail || 'Failed to process file');
        } finally {
            setProcessing(false);
        }
    };

    const handleDownload = () => {
        if (!processedFileId) return;
        window.location.href = downloadFile(processedFileId);
    };

    const handleNewFile = () => {
        router.push('/dashboard');
    };

    if (authLoading || !user) {
        return null;
    }

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto">
                <div className="mb-6">
                    <h1 className="text-3xl font-bold text-gray-900">Data Analysis & Preprocessing</h1>
                    <p className="mt-2 text-gray-600">Detect and fix data quality issues automatically</p>
                </div>

                {!fileInfo && (
                    <div className="max-w-2xl mx-auto">
                        <FileUpload onUploadSuccess={handleUploadSuccess} />
                    </div>
                )}

                {fileInfo && (
                    <div className="space-y-6">
                        <DataSummary fileInfo={fileInfo} analysis={analysis || undefined} />

                        {analyzing && (
                            <Card className="p-12 text-center bg-white">
                                <Loader2 className="mx-auto h-12 w-12 animate-spin text-indigo-600 mb-4" />
                                <p className="text-lg font-medium text-gray-900">Analyzing your dataset...</p>
                                <p className="text-sm text-gray-500">This may take a moment for large files</p>
                            </Card>
                        )}

                        {analysis && !analyzing && (
                            <>
                                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
                                    <h2 className="text-xl sm:text-2xl font-bold text-gray-900">Detected Issues</h2>
                                    <div className="flex flex-wrap gap-2">
                                        {analysis.total_issues > 0 && (
                                            <>
                                                <Button onClick={handleFixAll} disabled={processing} size="lg" className="flex-1 sm:flex-none">
                                                    {processing ? (
                                                        <>
                                                            <Loader2 className="mr-2 h-4 w-4 sm:h-5 sm:w-5 animate-spin" />
                                                            <span className="text-sm sm:text-base">Processing...</span>
                                                        </>
                                                    ) : (
                                                        <>
                                                            <Sparkles className="mr-2 h-4 w-4 sm:h-5 sm:w-5" />
                                                            <span className="text-sm sm:text-base">Fix All Issues</span>
                                                        </>
                                                    )}
                                                </Button>
                                                {selectedActions.length > 0 && (
                                                    <Button onClick={handleApplySelected} disabled={processing} variant="secondary" size="lg" className="flex-1 sm:flex-none">
                                                        <span className="text-sm sm:text-base">Apply {selectedActions.length} Selected</span>
                                                    </Button>
                                                )}
                                            </>
                                        )}
                                        <Button onClick={handleNewFile} variant="outline" size="lg" className="flex-1 sm:flex-none">
                                            <Upload className="mr-2 h-4 w-4 sm:h-5 sm:w-5" />
                                            <span className="text-sm sm:text-base">New File</span>
                                        </Button>
                                    </div>
                                </div>

                                <IssueList issues={analysis.issues} onSelectAction={handleSelectAction} />

                                {processedFileId && (
                                    <Card className="p-6 bg-green-50 border-green-200">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <h3 className="text-lg font-semibold text-green-900 mb-1">
                                                    Processing Complete!
                                                </h3>
                                                <p className="text-green-700">
                                                    Your cleaned dataset is ready to download
                                                </p>
                                            </div>
                                            <Button onClick={handleDownload} size="lg">
                                                <Download className="mr-2 h-5 w-5" />
                                                Download
                                            </Button>
                                        </div>
                                    </Card>
                                )}
                            </>
                        )}
                    </div>
                )}
            </div>

            {showImbalancedModal && processedFileId && (
                <ImbalancedDataModal
                    columns={imbalancedColumns}
                    fileId={processedFileId}
                    onClose={() => setShowImbalancedModal(false)}
                    onApply={handleApplyImbalancedFix}
                    onSkip={handleSkipImbalancedFix}
                />
            )}
        </DashboardLayout>
    );
}
