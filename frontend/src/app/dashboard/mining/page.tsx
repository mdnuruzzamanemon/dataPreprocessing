'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import DashboardLayout from '@/components/DashboardLayout';
import MiningResultsVisualization from '@/components/MiningResultsVisualization';
import { apiClient } from '@/services/api';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Loader2, Download, BarChart3, TrendingUp, GitBranch } from 'lucide-react';

interface FileItem {
    id: string;
    file_id: string;
    filename: string;
}

interface ColumnsInfo {
    all_columns: string[];
    numeric_columns: string[];
    categorical_columns: string[];
    total_rows: number;
}

const ANALYTICS_TYPES = [
    {
        id: 'correlation',
        name: 'Correlation Analysis',
        description: 'Find relationships between 2 numeric columns',
        icon: TrendingUp,
        minColumns: 2,
        maxColumns: 2,
        columnType: 'numeric'
    },
    {
        id: 'clustering',
        name: 'K-Means Clustering',
        description: 'Group similar data points',
        icon: GitBranch,
        minColumns: 2,
        maxColumns: null,
        columnType: 'numeric'
    },
    {
        id: 'classification',
        name: 'Classification',
        description: 'Predict categories (target + features)',
        icon: BarChart3,
        minColumns: 2,
        maxColumns: null,
        columnType: 'any'
    },
    {
        id: 'regression',
        name: 'Linear Regression',
        description: 'Predict numeric values (target + features)',
        icon: TrendingUp,
        minColumns: 2,
        maxColumns: null,
        columnType: 'numeric'
    },
    {
        id: 'descriptive',
        name: 'Descriptive Statistics',
        description: 'Summary statistics for columns',
        icon: BarChart3,
        minColumns: 1,
        maxColumns: null,
        columnType: 'any'
    }
];

export default function MiningPage() {
    const router = useRouter();
    const { user, loading: authLoading } = useAuth();

    const [files, setFiles] = useState<FileItem[]>([]);
    const [selectedFile, setSelectedFile] = useState<string>('');
    const [columnsInfo, setColumnsInfo] = useState<ColumnsInfo | null>(null);
    const [selectedAnalytics, setSelectedAnalytics] = useState<string>('');
    const [selectedColumns, setSelectedColumns] = useState<string[]>([]);
    const [parameters, setParameters] = useState<any>({});
    const [results, setResults] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [loadingColumns, setLoadingColumns] = useState(false);

    useEffect(() => {
        if (!authLoading && !user) {
            router.push('/login');
        } else if (user) {
            fetchFiles();
        }
    }, [user, authLoading, router]);

    const fetchFiles = async () => {
        try {
            const response = await apiClient.get('/api/files/');
            setFiles(response.data);
        } catch (error) {
            console.error('Failed to fetch files:', error);
        }
    };

    const handleFileSelect = async (fileId: string) => {
        setSelectedFile(fileId);
        setSelectedAnalytics('');
        setSelectedColumns([]);
        setResults(null);
        setLoadingColumns(true);

        try {
            const response = await apiClient.get(`/api/mining/columns/${fileId}`);
            setColumnsInfo(response.data);
        } catch (error) {
            console.error('Failed to fetch columns:', error);
            alert('Failed to load file columns');
        } finally {
            setLoadingColumns(false);
        }
    };

    const handleAnalyticsSelect = (analyticsId: string) => {
        setSelectedAnalytics(analyticsId);
        setSelectedColumns([]);
        setResults(null);

        // Set default parameters
        if (analyticsId === 'clustering') {
            setParameters({ n_clusters: 3 });
        } else if (analyticsId === 'classification' || analyticsId === 'regression') {
            setParameters({ test_size: 0.2 });
        } else {
            setParameters({});
        }
    };

    const handleColumnToggle = (column: string) => {
        const analytics = ANALYTICS_TYPES.find(a => a.id === selectedAnalytics);
        if (!analytics) return;

        if (selectedColumns.includes(column)) {
            setSelectedColumns(selectedColumns.filter(c => c !== column));
        } else {
            if (analytics.maxColumns && selectedColumns.length >= analytics.maxColumns) {
                alert(`Maximum ${analytics.maxColumns} columns allowed for this analytics type`);
                return;
            }
            setSelectedColumns([...selectedColumns, column]);
        }
    };

    const handleAnalyze = async () => {
        const analytics = ANALYTICS_TYPES.find(a => a.id === selectedAnalytics);
        if (!analytics) return;

        if (selectedColumns.length < analytics.minColumns) {
            alert(`Please select at least ${analytics.minColumns} column(s)`);
            return;
        }

        setLoading(true);
        try {
            const response = await apiClient.post('/api/mining/analyze', {
                file_id: selectedFile,
                analytics_type: selectedAnalytics,
                columns: selectedColumns,
                parameters
            });
            setResults(response.data);
        } catch (error: any) {
            console.error('Analysis failed:', error);
            alert(error.response?.data?.detail || 'Analysis failed');
        } finally {
            setLoading(false);
        }
    };

    const handleExport = async () => {
        if (!results) return;

        try {
            // Dynamic import to avoid SSR issues
            const html2canvas = (await import('html2canvas')).default;
            const jsPDF = (await import('jspdf')).default;

            const element = document.getElementById('mining-results');
            if (!element) return;

            // Capture the visualization as canvas
            const canvas = await html2canvas(element, {
                scale: 2,
                backgroundColor: '#ffffff',
                logging: false
            });

            const imgData = canvas.toDataURL('image/png');
            const pdf = new jsPDF({
                orientation: 'portrait',
                unit: 'mm',
                format: 'a4'
            });

            const imgWidth = 190;
            const imgHeight = (canvas.height * imgWidth) / canvas.width;

            // Add title
            pdf.setFontSize(16);
            pdf.text(`Data Mining Results - ${selectedAnalytics}`, 10, 10);

            // Add interpretation if available
            if (results.results.interpretation) {
                pdf.setFontSize(10);
                pdf.text(results.results.interpretation, 10, 20, { maxWidth: 190 });
            }

            // Add image
            pdf.addImage(imgData, 'PNG', 10, 30, imgWidth, imgHeight);

            // Save PDF
            pdf.save(`mining_results_${selectedAnalytics}_${Date.now()}.pdf`);
        } catch (error) {
            console.error('PDF export failed:', error);
            alert('Failed to export PDF. Exporting as JSON instead.');

            // Fallback to JSON export
            const dataStr = JSON.stringify(results, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `mining_results_${selectedAnalytics}_${Date.now()}.json`;
            link.click();
            URL.revokeObjectURL(url);
        }
    };

    const getAvailableColumns = () => {
        if (!columnsInfo) return [];
        const analytics = ANALYTICS_TYPES.find(a => a.id === selectedAnalytics);
        if (!analytics) return [];

        if (analytics.columnType === 'numeric') {
            return columnsInfo.numeric_columns;
        } else if (analytics.columnType === 'categorical') {
            return columnsInfo.categorical_columns;
        } else {
            return columnsInfo.all_columns;
        }
    };

    if (authLoading || !user) {
        return null;
    }

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto">
                <div className="mb-6">
                    <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Data Mining & Analytics</h1>
                    <p className="mt-2 text-sm sm:text-base text-gray-600">Discover insights and patterns in your data</p>
                </div>

                {/* Step 1: Select File */}
                <Card className="p-4 sm:p-6 mb-6">
                    <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-4">Step 1: Select File</h2>
                    <select
                        value={selectedFile}
                        onChange={(e) => handleFileSelect(e.target.value)}
                        className="w-full px-4 py-2 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    >
                        <option value="">Choose a file...</option>
                        {files.map((file) => (
                            <option key={file.id} value={file.file_id}>
                                {file.filename}
                            </option>
                        ))}
                    </select>
                    {loadingColumns && (
                        <div className="mt-4 flex items-center text-sm text-gray-600">
                            <Loader2 className="h-4 w-4 animate-spin mr-2" />
                            Loading columns...
                        </div>
                    )}
                </Card>

                {/* Step 2: Select Analytics Type */}
                {columnsInfo && (
                    <Card className="p-4 sm:p-6 mb-6">
                        <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-4">Step 2: Select Analytics Type</h2>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                            {ANALYTICS_TYPES.map((analytics) => {
                                const Icon = analytics.icon;
                                const isSelected = selectedAnalytics === analytics.id;
                                return (
                                    <button
                                        key={analytics.id}
                                        onClick={() => handleAnalyticsSelect(analytics.id)}
                                        className={`p-4 border-2 rounded-lg text-left transition-all ${isSelected
                                            ? 'border-indigo-600 bg-indigo-50'
                                            : 'border-gray-200 hover:border-indigo-300'
                                            }`}
                                    >
                                        <Icon className={`h-6 w-6 mb-2 ${isSelected ? 'text-indigo-600' : 'text-gray-600'}`} />
                                        <h3 className="font-semibold text-gray-900 text-sm sm:text-base">{analytics.name}</h3>
                                        <p className="text-xs sm:text-sm text-gray-600 mt-1">{analytics.description}</p>
                                    </button>
                                );
                            })}
                        </div>
                    </Card>
                )}

                {/* Step 3: Select Columns */}
                {selectedAnalytics && (
                    <Card className="p-4 sm:p-6 mb-6">
                        <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-4">Step 3: Select Columns</h2>
                        <p className="text-sm text-gray-600 mb-4">
                            Select {ANALYTICS_TYPES.find(a => a.id === selectedAnalytics)?.minColumns} to{' '}
                            {ANALYTICS_TYPES.find(a => a.id === selectedAnalytics)?.maxColumns || 'multiple'} column(s)
                        </p>
                        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2 sm:gap-3">
                            {getAvailableColumns().map((column) => (
                                <button
                                    key={column}
                                    onClick={() => handleColumnToggle(column)}
                                    className={`px-3 py-2 text-sm rounded-lg border-2 transition-all ${selectedColumns.includes(column)
                                        ? 'border-indigo-600 bg-indigo-50 text-indigo-700'
                                        : 'border-gray-200 hover:border-indigo-300 text-gray-700'
                                        }`}
                                >
                                    {column}
                                </button>
                            ))}
                        </div>

                        {/* Parameters */}
                        {selectedAnalytics === 'clustering' && (
                            <div className="mt-6">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Number of Clusters
                                </label>
                                <input
                                    type="number"
                                    min="2"
                                    max="10"
                                    value={parameters.n_clusters || 3}
                                    onChange={(e) => setParameters({ ...parameters, n_clusters: parseInt(e.target.value) })}
                                    className="w-32 px-3 py-2 border border-gray-300 rounded-lg"
                                />
                            </div>
                        )}

                        <div className="mt-6">
                            <Button
                                onClick={handleAnalyze}
                                disabled={loading || selectedColumns.length < (ANALYTICS_TYPES.find(a => a.id === selectedAnalytics)?.minColumns || 1)}
                                size="lg"
                                className="w-full sm:w-auto"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                                        Analyzing...
                                    </>
                                ) : (
                                    <>
                                        <BarChart3 className="mr-2 h-5 w-5" />
                                        Analyze Data
                                    </>
                                )}
                            </Button>
                        </div>
                    </Card>
                )}

                {/* Results */}
                {results && (
                    <Card className="p-4 sm:p-6">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
                            <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-3 sm:mb-0">Results</h2>
                            <Button onClick={handleExport} variant="outline">
                                <Download className="mr-2 h-4 w-4" />
                                Export as PDF
                            </Button>
                        </div>

                        {/* Interpretation */}
                        {results.results.interpretation && (
                            <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4 mb-6">
                                <p className="text-indigo-900 font-medium">{results.results.interpretation}</p>
                            </div>
                        )}

                        {/* Visualizations */}
                        <div id="mining-results">
                            <MiningResultsVisualization
                                analyticsType={results.analytics_type}
                                results={results.results}
                                columnsUsed={results.columns_used}
                            />
                        </div>
                    </Card>
                )}
            </div>
        </DashboardLayout>
    );
}
