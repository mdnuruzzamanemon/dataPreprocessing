'use client';

import React, { useState } from 'react';
import FileUpload from '@/components/FileUpload';
import DataSummary from '@/components/DataSummary';
import IssueList from '@/components/IssueList';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import {
  FileInfo,
  AnalysisResponse,
  DataIssue,
  PreprocessAction,
  IssueType,
} from '@/types';
import {
  analyzeFile,
  fixAllIssues,
  preprocessFile,
  downloadFile,
} from '@/services/dataService';
import { Loader2, Download, Sparkles, RefreshCw } from 'lucide-react';

export default function Home() {
  const [fileInfo, setFileInfo] = useState<FileInfo | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [selectedActions, setSelectedActions] = useState<PreprocessAction[]>([]);
  const [processedFileId, setProcessedFileId] = useState<string | null>(null);

  const handleUploadSuccess = async (uploadedFileInfo: FileInfo) => {
    setFileInfo(uploadedFileInfo);
    setAnalysis(null);
    setSelectedActions([]);
    setProcessedFileId(null);
    
    // Automatically analyze
    setAnalyzing(true);
    try {
      const analysisResult = await analyzeFile(uploadedFileInfo.file_id);
      setAnalysis(analysisResult);
    } catch (error) {
      console.error('Analysis error:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSelectAction = (issue: DataIssue, method: string) => {
    const action: PreprocessAction = {
      issue_type: issue.type,
      columns: issue.affected_columns,
      method: method.toLowerCase().replace(/\s+/g, '_'),
      parameters: {},
    };

    // Check if action already exists and replace it
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
      alert(`Successfully processed! ${result.applied_actions.length} actions applied.`);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to process file');
    } finally {
      setProcessing(false);
    }
  };

  const handleApplySelected = async () => {
    if (!fileInfo || selectedActions.length === 0) return;

    setProcessing(true);
    try {
      const result = await preprocessFile(fileInfo.file_id, {
        actions: selectedActions,
      });
      setProcessedFileId(result.file_id);
      alert(
        `Successfully processed! ${result.applied_actions.filter((a) => a.status === 'success').length} actions applied.`
      );
    } catch (error: any) {
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
    setFileInfo(null);
    setAnalysis(null);
    setSelectedActions([]);
    setProcessedFileId(null);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Data Preprocessing Platform
          </h1>
          <p className="text-lg text-gray-600">
            Automatically detect and fix data quality issues in your datasets
          </p>
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
            {/* Summary */}
            <DataSummary fileInfo={fileInfo} analysis={analysis} />

            {/* Loading State */}
            {analyzing && (
              <Card className="p-12 text-center">
                <Loader2 className="mx-auto h-12 w-12 animate-spin text-primary mb-4" />
                <p className="text-lg font-medium">Analyzing your dataset...</p>
                <p className="text-sm text-gray-500">
                  This may take a moment for large files
                </p>
              </Card>
            )}

            {/* Issues and Actions */}
            {analysis && !analyzing && (
              <>
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold">Detected Issues</h2>
                  <div className="flex gap-2">
                    {analysis.total_issues > 0 && (
                      <>
                        <Button
                          onClick={handleFixAll}
                          disabled={processing}
                          size="lg"
                        >
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
                          <Button
                            onClick={handleApplySelected}
                            disabled={processing}
                            variant="secondary"
                            size="lg"
                          >
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

                <IssueList
                  issues={analysis.issues}
                  onSelectAction={handleSelectAction}
                />

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
    </main>
  );
}
