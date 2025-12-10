'use client';

import React from 'react';
import { FileInfo, AnalysisResponse } from '@/types';
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card';
import { Badge } from './ui/Badge';
import { File, Database, Columns, AlertCircle } from 'lucide-react';
import { formatBytes, formatNumber } from '@/utils/helpers';

interface DataSummaryProps {
  fileInfo: FileInfo;
  analysis?: AnalysisResponse;
}

export default function DataSummary({ fileInfo, analysis }: DataSummaryProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card>
        <CardContent className="p-4 sm:p-6">
          <div className="flex items-center justify-between">
            <div className="flex-1 min-w-0 mr-3">
              <p className="text-sm text-gray-500 mb-1">File Name</p>
              <p className="font-semibold truncate" title={fileInfo.filename}>{fileInfo.filename}</p>
              <p className="text-xs text-gray-400 mt-1">{formatBytes(fileInfo.size)}</p>
            </div>
            <File className="h-6 w-6 sm:h-8 sm:w-8 text-primary flex-shrink-0" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-4 sm:p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 mb-1">Total Rows</p>
              <p className="text-xl sm:text-2xl font-bold">{formatNumber(fileInfo.rows)}</p>
            </div>
            <Database className="h-6 w-6 sm:h-8 sm:w-8 text-blue-500 flex-shrink-0" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 mb-1">Total Columns</p>
              <p className="text-2xl font-bold">{fileInfo.columns}</p>
            </div>
            <Columns className="h-8 w-8 text-green-500" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 mb-1">Issues Found</p>
              <p className="text-2xl font-bold">{analysis?.total_issues || 0}</p>
              {analysis && analysis.total_issues > 0 && (
                <div className="flex gap-1 mt-2">
                  {analysis.summary.critical > 0 && (
                    <Badge variant="destructive" className="text-xs">
                      {analysis.summary.critical} Critical
                    </Badge>
                  )}
                  {analysis.summary.high > 0 && (
                    <Badge variant="destructive" className="text-xs">
                      {analysis.summary.high} High
                    </Badge>
                  )}
                </div>
              )}
            </div>
            <AlertCircle
              className={`h-8 w-8 ${analysis && analysis.total_issues > 0 ? 'text-red-500' : 'text-gray-400'
                }`}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
