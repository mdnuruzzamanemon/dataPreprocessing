import React from 'react';
import {
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    BarChart,
    Bar,
    LineChart,
    Line,
    Cell,
    PieChart,
    Pie,
    AreaChart,
    Area,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    Radar
} from 'recharts';

interface MiningResultsVisualizationProps {
    analyticsType: string;
    results: any;
    columnsUsed: string[];
}

const COLORS = ['#6366f1', '#ec4899', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#84cc16'];

export default function MiningResultsVisualization({
    analyticsType,
    results,
    columnsUsed
}: MiningResultsVisualizationProps) {

    // Correlation Analysis
    if (analyticsType === 'correlation') {
        return (
            <div className="space-y-6">
                {/* Metrics */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                        <p className="text-sm text-indigo-600 font-medium">Pearson Correlation</p>
                        <p className="text-3xl font-bold text-indigo-900 mt-2">
                            {results.pearson_correlation?.toFixed(3)}
                        </p>
                        <p className="text-xs text-indigo-600 mt-1">
                            p-value: {results.pearson_p_value?.toExponential(3)}
                        </p>
                    </div>
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                        <p className="text-sm text-purple-600 font-medium">Spearman Correlation</p>
                        <p className="text-3xl font-bold text-purple-900 mt-2">
                            {results.spearman_correlation?.toFixed(3)}
                        </p>
                        <p className="text-xs text-purple-600 mt-1">
                            p-value: {results.spearman_p_value?.toExponential(3)}
                        </p>
                    </div>
                </div>

                {/* Scatter Plot with Trend Line */}
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Correlation Scatter Plot</h3>
                    <ResponsiveContainer width="100%" height={400}>
                        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis type="number" dataKey="x" name={columnsUsed[0]} />
                            <YAxis type="number" dataKey="y" name={columnsUsed[1]} />
                            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                            <Legend />
                            <Scatter name={`${columnsUsed[0]} vs ${columnsUsed[1]}`} data={results.scatter_data} fill="#6366f1" />
                        </ScatterChart>
                    </ResponsiveContainer>
                </div>
            </div>
        );
    }

    // Clustering Analysis
    if (analyticsType === 'clustering') {
        const clusterSizes = Object.entries(results.cluster_sizes || {}).map(([cluster, size]) => ({
            cluster: `Cluster ${cluster}`,
            size: size as number
        }));

        return (
            <div className="space-y-6">
                {/* Metrics */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                        <p className="text-sm text-indigo-600 font-medium">Number of Clusters</p>
                        <p className="text-3xl font-bold text-indigo-900 mt-2">{results.n_clusters}</p>
                    </div>
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                        <p className="text-sm text-green-600 font-medium">Silhouette Score</p>
                        <p className="text-3xl font-bold text-green-900 mt-2">
                            {results.silhouette_score?.toFixed(3)}
                        </p>
                        <p className="text-xs text-green-600 mt-1">
                            {results.silhouette_score > 0.5 ? 'Good' : results.silhouette_score > 0.25 ? 'Fair' : 'Poor'} clustering
                        </p>
                    </div>
                </div>

                {/* Pie Chart for Cluster Distribution */}
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Cluster Distribution</h3>
                    <ResponsiveContainer width="100%" height={350}>
                        <PieChart>
                            <Pie
                                data={clusterSizes}
                                cx="50%"
                                cy="50%"
                                labelLine={true}
                                label={({ cluster, size }) => `${cluster}: ${size}`}
                                outerRadius={120}
                                fill="#8884d8"
                                dataKey="size"
                            >
                                {clusterSizes.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                {/* Scatter Plot (if 2D data available) */}
                {results.scatter_data && results.scatter_data.length > 0 && (
                    <div className="bg-white border border-gray-200 rounded-lg p-4">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Cluster Visualization</h3>
                        <ResponsiveContainer width="100%" height={400}>
                            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis type="number" dataKey="x" name={columnsUsed[0]} />
                                <YAxis type="number" dataKey="y" name={columnsUsed[1]} />
                                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                                <Legend />
                                {[...Array(results.n_clusters)].map((_, i) => (
                                    <Scatter
                                        key={i}
                                        name={`Cluster ${i}`}
                                        data={results.scatter_data.filter((d: any) => d.cluster === i)}
                                        fill={COLORS[i % COLORS.length]}
                                    />
                                ))}
                            </ScatterChart>
                        </ResponsiveContainer>
                    </div>
                )}
            </div>
        );
    }

    // Classification Analysis
    if (analyticsType === 'classification') {
        const featureImportance = Object.entries(results.feature_importance || {}).map(([feature, importance]) => ({
            feature,
            importance: importance as number
        }));

        return (
            <div className="space-y-6">
                {/* Accuracy Metric */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
                    <p className="text-sm text-green-600 font-medium">Model Accuracy</p>
                    <p className="text-5xl font-bold text-green-900 mt-2">
                        {(results.accuracy * 100).toFixed(1)}%
                    </p>
                    <p className="text-sm text-green-600 mt-2">Test Size: {results.test_size} samples</p>
                </div>

                {/* Confusion Matrix */}
                {results.confusion_matrix && (
                    <div className="bg-white border border-gray-200 rounded-lg p-4">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Confusion Matrix</h3>
                        <div className="overflow-x-auto">
                            <table className="min-w-full">
                                <thead>
                                    <tr>
                                        <th className="px-4 py-2 bg-gray-50"></th>
                                        {results.class_labels?.map((label: string, i: number) => (
                                            <th key={i} className="px-4 py-2 bg-gray-50 text-sm font-medium text-gray-700">
                                                Predicted {label}
                                            </th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {results.confusion_matrix.map((row: number[], i: number) => (
                                        <tr key={i}>
                                            <td className="px-4 py-2 bg-gray-50 text-sm font-medium text-gray-700">
                                                Actual {results.class_labels[i]}
                                            </td>
                                            {row.map((value: number, j: number) => (
                                                <td
                                                    key={j}
                                                    className="px-4 py-2 text-center"
                                                    style={{
                                                        backgroundColor: i === j ? '#dcfce7' : value > 0 ? '#fee2e2' : '#f9fafb'
                                                    }}
                                                >
                                                    <span className="text-lg font-semibold">{value}</span>
                                                </td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {/* Feature Importance - Horizontal Bar Chart */}
                {featureImportance.length > 0 && (
                    <div className="bg-white border border-gray-200 rounded-lg p-4">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Feature Importance</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={featureImportance} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis type="number" />
                                <YAxis dataKey="feature" type="category" width={100} />
                                <Tooltip />
                                <Bar dataKey="importance" fill="#6366f1" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                )}
            </div>
        );
    }

    // Regression Analysis
    if (analyticsType === 'regression') {
        const coefficients = Object.entries(results.coefficients || {}).map(([feature, coef]) => ({
            feature,
            coefficient: coef as number
        }));

        return (
            <div className="space-y-6">
                {/* R² Score */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
                    <p className="text-sm text-blue-600 font-medium">R² Score</p>
                    <p className="text-5xl font-bold text-blue-900 mt-2">
                        {results.r2_score?.toFixed(3)}
                    </p>
                    <p className="text-sm text-blue-600 mt-2">
                        {results.r2_score > 0.7 ? 'Good' : results.r2_score > 0.4 ? 'Moderate' : 'Poor'} fit
                    </p>
                </div>

                {/* Actual vs Predicted - Scatter with Line */}
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Actual vs Predicted Values</h3>
                    <ResponsiveContainer width="100%" height={400}>
                        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis type="number" dataKey="actual" name="Actual" />
                            <YAxis type="number" dataKey="predicted" name="Predicted" />
                            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                            <Legend />
                            <Scatter name="Predictions" data={results.scatter_data} fill="#6366f1" />
                        </ScatterChart>
                    </ResponsiveContainer>
                </div>

                {/* Coefficients - Bar Chart with Colors */}
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Coefficients</h3>
                    <div className="mb-4 p-3 bg-gray-50 rounded">
                        <p className="text-sm text-gray-600">Intercept</p>
                        <p className="text-xl font-bold text-gray-900">{results.intercept?.toFixed(4)}</p>
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={coefficients} layout="vertical">
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis type="number" />
                            <YAxis dataKey="feature" type="category" width={100} />
                            <Tooltip />
                            <Bar dataKey="coefficient">
                                {coefficients.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.coefficient >= 0 ? '#10b981' : '#ef4444'} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        );
    }

    // Descriptive Statistics
    if (analyticsType === 'descriptive') {
        return (
            <div className="space-y-6">
                {Object.entries(results).map(([column, stats]: [string, any]) => (
                    <div key={column} className="bg-white border border-gray-200 rounded-lg p-4">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">{column}</h3>

                        {stats.type === 'numeric' ? (
                            <>
                                {/* Numeric Stats */}
                                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                                    <div className="bg-gray-50 p-3 rounded">
                                        <p className="text-xs text-gray-600">Mean</p>
                                        <p className="text-lg font-bold text-gray-900">{stats.mean?.toFixed(2)}</p>
                                    </div>
                                    <div className="bg-gray-50 p-3 rounded">
                                        <p className="text-xs text-gray-600">Median</p>
                                        <p className="text-lg font-bold text-gray-900">{stats.median?.toFixed(2)}</p>
                                    </div>
                                    <div className="bg-gray-50 p-3 rounded">
                                        <p className="text-xs text-gray-600">Std Dev</p>
                                        <p className="text-lg font-bold text-gray-900">{stats.std?.toFixed(2)}</p>
                                    </div>
                                    <div className="bg-gray-50 p-3 rounded">
                                        <p className="text-xs text-gray-600">Count</p>
                                        <p className="text-lg font-bold text-gray-900">{stats.count}</p>
                                    </div>
                                </div>

                                {/* Area Chart for Distribution */}
                                {stats.histogram && (
                                    <ResponsiveContainer width="100%" height={300}>
                                        <AreaChart data={stats.histogram}>
                                            <CartesianGrid strokeDasharray="3 3" />
                                            <XAxis
                                                dataKey="bin_start"
                                                tickFormatter={(value) => value.toFixed(1)}
                                            />
                                            <YAxis />
                                            <Tooltip
                                                labelFormatter={(value) => `Range: ${value.toFixed(1)}`}
                                            />
                                            <Area type="monotone" dataKey="count" stroke="#6366f1" fill="#6366f1" fillOpacity={0.6} />
                                        </AreaChart>
                                    </ResponsiveContainer>
                                )}
                            </>
                        ) : (
                            <>
                                {/* Categorical Stats */}
                                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-6">
                                    <div className="bg-gray-50 p-3 rounded">
                                        <p className="text-xs text-gray-600">Count</p>
                                        <p className="text-lg font-bold text-gray-900">{stats.count}</p>
                                    </div>
                                    <div className="bg-gray-50 p-3 rounded">
                                        <p className="text-xs text-gray-600">Unique</p>
                                        <p className="text-lg font-bold text-gray-900">{stats.unique}</p>
                                    </div>
                                    <div className="bg-gray-50 p-3 rounded">
                                        <p className="text-xs text-gray-600">Top Value</p>
                                        <p className="text-lg font-bold text-gray-900 truncate" title={stats.top}>
                                            {stats.top}
                                        </p>
                                    </div>
                                </div>

                                {/* Pie Chart for Categorical Distribution */}
                                {stats.distribution && (
                                    <ResponsiveContainer width="100%" height={350}>
                                        <PieChart>
                                            <Pie
                                                data={Object.entries(stats.distribution).map(([key, value]) => ({
                                                    name: key,
                                                    value: value as number
                                                }))}
                                                cx="50%"
                                                cy="50%"
                                                labelLine={true}
                                                label={({ name, value }) => `${name}: ${value}`}
                                                outerRadius={120}
                                                fill="#8884d8"
                                                dataKey="value"
                                            >
                                                {Object.keys(stats.distribution).map((key, index) => (
                                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                ))}
                                            </Pie>
                                            <Tooltip />
                                            <Legend />
                                        </PieChart>
                                    </ResponsiveContainer>
                                )}
                            </>
                        )}
                    </div>
                ))}
            </div>
        );
    }

    // Association Rules
    if (analyticsType === 'association') {
        return (
            <div className="space-y-6">
                {/* Summary */}
                <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                    <p className="text-sm text-indigo-600 font-medium">Total Transactions</p>
                    <p className="text-3xl font-bold text-indigo-900 mt-2">{results.total_transactions}</p>
                </div>

                {/* Association Rules Table */}
                {results.rules && results.rules.length > 0 && (
                    <div className="bg-white border border-gray-200 rounded-lg p-4 overflow-x-auto">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Association Rules</h3>
                        <table className="min-w-full text-sm">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-4 py-2 text-left">If (Antecedent)</th>
                                    <th className="px-4 py-2 text-left">Then (Consequent)</th>
                                    <th className="px-4 py-2 text-center">Support</th>
                                    <th className="px-4 py-2 text-center">Confidence</th>
                                    <th className="px-4 py-2 text-center">Lift</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {results.rules.slice(0, 10).map((rule: any, i: number) => (
                                    <tr key={i} className="hover:bg-gray-50">
                                        <td className="px-4 py-2">{rule.antecedent.join(', ')}</td>
                                        <td className="px-4 py-2">{rule.consequent.join(', ')}</td>
                                        <td className="px-4 py-2 text-center">{rule.support.toFixed(3)}</td>
                                        <td className="px-4 py-2 text-center">{rule.confidence.toFixed(3)}</td>
                                        <td className="px-4 py-2 text-center font-semibold text-indigo-600">
                                            {rule.lift.toFixed(2)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        );
    }

    // Fallback
    return (
        <div className="bg-gray-50 rounded-lg p-4">
            <pre className="text-sm text-gray-800 whitespace-pre-wrap">
                {JSON.stringify(results, null, 2)}
            </pre>
        </div>
    );
}
