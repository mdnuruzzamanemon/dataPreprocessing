import { apiClient } from './api';
import {
  FileInfo,
  AnalysisResponse,
  PreprocessRequest,
  PreprocessResponse,
  DataPreview
} from '@/types';

export const uploadFile = async (file: File): Promise<FileInfo> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<FileInfo>('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const analyzeFile = async (fileId: string): Promise<AnalysisResponse> => {
  const response = await apiClient.get<AnalysisResponse>(`/api/analyze/${fileId}`);
  return response.data;
};

export const getDataPreview = async (fileId: string, rows: number = 10): Promise<DataPreview> => {
  const response = await apiClient.get<DataPreview>(`/api/analyze/${fileId}/preview`, {
    params: { rows }
  });
  return response.data;
};

export const preprocessFile = async (
  fileId: string,
  request: PreprocessRequest
): Promise<PreprocessResponse> => {
  const response = await apiClient.post<PreprocessResponse>(
    `/api/preprocess/${fileId}`,
    request
  );
  return response.data;
};

export const fixAllIssues = async (fileId: string): Promise<PreprocessResponse> => {
  const response = await apiClient.post<PreprocessResponse>(
    `/api/preprocess/${fileId}/fix-all`
  );
  return response.data;
};

export const fixImbalancedData = async (
  fileId: string,
  targetColumn: string,
  method: string
): Promise<any> => {
  const response = await apiClient.post(
    `/api/preprocess/${fileId}/fix-imbalanced`,
    { target_column: targetColumn, method }
  );
  return response.data;
};

export const downloadFile = (fileId: string): string => {
  return `${apiClient.defaults.baseURL}/api/download/${fileId}`;
};

export const deleteFile = async (fileId: string): Promise<void> => {
  await apiClient.delete(`/api/upload/${fileId}`);
};
