'use client';

import React from 'react';
import { DataIssue, IssueSeverity, IssueType } from '@/types';
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card';
import { Badge } from './ui/Badge';
import { Button } from './ui/Button';
import {
  AlertTriangle,
  CheckCircle,
  XCircle,
  AlertCircle,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

interface IssueListProps {
  issues: DataIssue[];
  onSelectAction: (issue: DataIssue, method: string) => void;
}

const severityConfig = {
  [IssueSeverity.LOW]: {
    badge: 'secondary' as const,
    icon: CheckCircle,
    color: 'text-blue-600',
  },
  [IssueSeverity.MEDIUM]: {
    badge: 'warning' as const,
    icon: AlertCircle,
    color: 'text-yellow-600',
  },
  [IssueSeverity.HIGH]: {
    badge: 'destructive' as const,
    icon: AlertTriangle,
    color: 'text-orange-600',
  },
  [IssueSeverity.CRITICAL]: {
    badge: 'destructive' as const,
    icon: XCircle,
    color: 'text-red-600',
  },
};

const issueTypeLabels: Record<IssueType, string> = {
  [IssueType.MISSING_VALUES]: 'Missing Values',
  [IssueType.DUPLICATES]: 'Duplicate Rows',
  [IssueType.OUTLIERS]: 'Outliers',
  [IssueType.IMBALANCED_DATA]: 'Imbalanced Data',
  [IssueType.INCONSISTENT_TYPES]: 'Inconsistent Types',
  [IssueType.CATEGORICAL_INCONSISTENCIES]: 'Categorical Issues',
  [IssueType.INVALID_RANGES]: 'Invalid Ranges',
  [IssueType.SKEWNESS]: 'Skewed Distribution',
  [IssueType.HIGH_CARDINALITY]: 'High Cardinality',
  [IssueType.CONSTANT_VALUES]: 'Constant Values',
  [IssueType.CORRELATED_FEATURES]: 'Correlated Features',
  [IssueType.WRONG_DATE_FORMAT]: 'Date Format Issues',
  [IssueType.ENCODING_ISSUES]: 'Encoding Issues',
  [IssueType.MIXED_UNITS]: 'Mixed Units',
  [IssueType.NOISY_TEXT]: 'Noisy Text',
};

export default function IssueList({ issues, onSelectAction }: IssueListProps) {
  const [expandedIssues, setExpandedIssues] = React.useState<Set<number>>(new Set());

  const toggleIssue = (index: number) => {
    const newExpanded = new Set(expandedIssues);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedIssues(newExpanded);
  };

  if (issues.length === 0) {
    return (
      <Card>
        <CardContent className="p-12 text-center">
          <CheckCircle className="mx-auto h-16 w-16 text-green-500 mb-4" />
          <h3 className="text-xl font-semibold mb-2">No Issues Found!</h3>
          <p className="text-gray-500">Your dataset looks clean and ready to use.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {issues.map((issue, index) => {
        const config = severityConfig[issue.severity];
        const Icon = config.icon;
        const isExpanded = expandedIssues.has(index);

        return (
          <Card key={index} className="overflow-hidden">
            <div
              className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => toggleIssue(index)}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <Icon className={`h-6 w-6 mt-0.5 ${config.color}`} />
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h3 className="font-semibold text-lg">
                        {issueTypeLabels[issue.type]}
                      </h3>
                      <Badge variant={config.badge}>
                        {issue.severity.toUpperCase()}
                      </Badge>
                    </div>
                    <p className="text-gray-600 mb-2">{issue.description}</p>
                    <div className="flex flex-wrap gap-2">
                      {issue.percentage !== undefined && issue.percentage !== null && (
                        <span className="text-sm text-gray-500">
                          {issue.percentage.toFixed(2)}% affected
                        </span>
                      )}
                      {issue.affected_columns.length > 0 && (
                        <span className="text-sm text-gray-500">
                          • {issue.affected_columns.length} column(s)
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                {isExpanded ? (
                  <ChevronUp className="h-5 w-5 text-gray-400" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-gray-400" />
                )}
              </div>
            </div>

            {isExpanded && (
              <div className="border-t bg-gray-50 p-4 space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Affected Columns:</h4>
                  <div className="flex flex-wrap gap-2">
                    {issue.affected_columns.map((col) => (
                      <Badge key={col} variant="outline">
                        {col}
                      </Badge>
                    ))}
                  </div>
                </div>

                {Object.keys(issue.details).length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">Details:</h4>
                    <div className="bg-white rounded p-3 text-sm font-mono max-h-48 overflow-auto">
                      <pre>{JSON.stringify(issue.details, null, 2)}</pre>
                    </div>
                  </div>
                )}

                {issue.recommended_actions.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">Available Actions:</h4>
                    <div className="flex flex-wrap gap-2">
                      {issue.recommended_actions.map((action) => (
                        <Button
                          key={action}
                          variant="outline"
                          size="sm"
                          onClick={() => onSelectAction(issue, action)}
                        >
                          {action}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </Card>
        );
      })}
    </div>
  );
}
