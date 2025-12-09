'use client';

import React, { useState } from 'react';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

interface ImbalancedDataModalProps {
  columns: string[];
  fileId: string;
  onClose: () => void;
  onApply: (targetColumn: string, method: string) => Promise<void>;
  onSkip: () => void;
}

export default function ImbalancedDataModal({
  columns,
  fileId,
  onClose,
  onApply,
  onSkip,
}: ImbalancedDataModalProps) {
  const [targetColumn, setTargetColumn] = useState<string>('');
  const [method, setMethod] = useState<string>('smote');
  const [processing, setProcessing] = useState(false);

  // Ensure columns is an array
  const columnList = Array.isArray(columns) ? columns : [];

  const handleApply = async () => {
    if (!targetColumn) {
      alert('Please select a target column');
      return;
    }

    setProcessing(true);
    try {
      await onApply(targetColumn, method);
      onClose();
    } catch (error) {
      console.error('Error applying imbalanced data fix:', error);
      alert('Failed to apply fix. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="max-w-lg w-full p-6 relative bg-white">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Header */}
        <h2 className="text-2xl font-bold mb-2">Fix Imbalanced Data</h2>
        <p className="text-gray-600 mb-6">
          Choose the target column and sampling method to balance your dataset
        </p>

        {/* Target Column Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target Column (Label/Class)
          </label>
          <select
            value={targetColumn}
            onChange={(e) => setTargetColumn(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">Select a column...</option>
            {columnList.map((col) => (
              <option key={col} value={col}>
                {col}
              </option>
            ))}
          </select>
          <p className="text-xs text-gray-500 mt-1">
            Select the column that contains the class labels
          </p>
        </div>

        {/* Method Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sampling Method
          </label>
          <div className="space-y-3">
            <label className="flex items-start p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
              <input
                type="radio"
                name="method"
                value="smote"
                checked={method === 'smote'}
                onChange={(e) => setMethod(e.target.value)}
                className="mt-1 mr-3"
              />
              <div>
                <div className="font-medium">SMOTE</div>
                <div className="text-sm text-gray-600">
                  Synthetic Minority Over-sampling Technique. Creates synthetic samples for minority class.
                </div>
              </div>
            </label>

            <label className="flex items-start p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
              <input
                type="radio"
                name="method"
                value="oversample"
                checked={method === 'oversample'}
                onChange={(e) => setMethod(e.target.value)}
                className="mt-1 mr-3"
              />
              <div>
                <div className="font-medium">Random Oversampling</div>
                <div className="text-sm text-gray-600">
                  Randomly duplicates samples from minority class until balanced.
                </div>
              </div>
            </label>

            <label className="flex items-start p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
              <input
                type="radio"
                name="method"
                value="undersample"
                checked={method === 'undersample'}
                onChange={(e) => setMethod(e.target.value)}
                className="mt-1 mr-3"
              />
              <div>
                <div className="font-medium">Random Undersampling</div>
                <div className="text-sm text-gray-600">
                  Randomly removes samples from majority class until balanced.
                </div>
              </div>
            </label>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <Button
            onClick={handleApply}
            disabled={processing || !targetColumn}
            className="flex-1"
          >
            {processing ? 'Applying...' : 'Apply Fix'}
          </Button>
          <Button 
            onClick={onSkip} 
            variant="outline" 
            disabled={processing}
            className="flex-1"
          >
            Skip for Now
          </Button>
          <Button onClick={onClose} variant="outline" disabled={processing}>
            Cancel
          </Button>
        </div>
      </Card>
    </div>
  );
}
