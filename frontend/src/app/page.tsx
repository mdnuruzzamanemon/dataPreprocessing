'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
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
import { Loader2, Download, Sparkles, RefreshCw, Home } from 'lucide-react';

export default function PreprocessingPage() {
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

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  // Load file if fileId is provided
  useEffect(() => {
    if (initialFileId && user) {
      // Create a minimal FileInfo object and analyze
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

    // Update URL with fileId
    router.push(`/?fileId=${uploadedFileInfo.file_id}`);

    // Automatically analyze
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
        alert(`Preprocessing complete! ${result.applied_actions.length} actions applied. Imbalanced data detected - please choose a sampling method or skip.`);
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
      alert(`Imbalanced data fix applied successfully! Remaining issues: ${newAnalysis.total_issues}`);
    } catch (error: any) {
      console.error('Imbalanced fix error:', error);
      alert(error.response?.data?.detail || 'Failed to apply imbalanced data fix');
      throw error;
    }
  };

  const handleSkipImbalancedFix = () => {
    setShowImbalancedModal(false);
    alert('Skipped imbalanced data fix. You can download the file with other fixes applied.');
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
        alert(`Successfully processed! ${result.applied_actions.filter((a) => a.status === 'success').length} actions applied. Remaining issues: ${result.analysis.total_issues}`);
      } else {
        const newAnalysis = await analyzeFile(result.file_id);
        setAnalysis(newAnalysis);
        alert(`Successfully processed! ${result.applied_actions.filter((a) => a.status === 'success').length} actions applied. Remaining issues: ${newAnalysis.total_issues}`);
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

  const handleReset = () => {
    router.push('/dashboard');
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <Loader2 className="h-12 w-12 animate-spin text-indigo-600" />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-between mb-4">
            <Button onClick={() => router.push('/dashboard')} variant="outline">
              <Home className="mr-2 h-4 w-4" />
              Dashboard
            </Button>
            <div className="flex-1 text-center">
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                Data Preprocessing Platform
              </h1>
              <p className="text-lg text-gray-600">
                Automatically detect and fix data quality issues in your datasets
              </p>
            </div>
            <div className="w-32"></div>
          </div>
        </div>

        {/* Upload Section */}
        {!fileInfo && (
          <div className="max-w-2xl mx-auto">
            <FileUpload onUploadSuccess={handleUploadSuccess} />
          </div>
        )}

        {/* Analysis Section */}
        {fileInfo && (
          <div className="space-y-6">
            <DataSummary fileInfo={fileInfo} analysis={analysis || undefined} />

            {analyzing && (
              <Card className="p-12 text-center">
                <Loader2 className="mx-auto h-12 w-12 animate-spin text-primary mb-4" />
                <p className="text-lg font-medium">Analyzing your dataset...</p>
                <p className="text-sm text-gray-500">This may take a moment for large files</p>
              </Card>
            )}

            {analysis && !analyzing && (
              <>
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold">Detected Issues</h2>
                  <div className="flex gap-2">
                    {analysis.total_issues > 0 && (
                      <>
                        <Button onClick={handleFixAll} disabled={processing} size="lg">
                          {processing ? (
                            <>
                              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                              Processing...
                            </>
                          ) : (
                            <>
                              <Sparkles className="mr-2 h-5 w-5" />
                              Fix All Issues
                            </>
                          )}
                        </Button>
                        {selectedActions.length > 0 && (
                          <Button onClick={handleApplySelected} disabled={processing} variant="secondary" size="lg">
                            Apply {selectedActions.length} Selected
                          </Button>
                        )}
                      </>
                    )}
                    <Button onClick={handleReset} variant="outline" size="lg">
                      <RefreshCw className="mr-2 h-5 w-5" />
                      New File
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
    </main>
  );
}
