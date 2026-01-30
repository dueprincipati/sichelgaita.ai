// Type definitions for Sichelgaita.AI

export interface FileMetadata {
  id: string;
  filename: string;
  fileType: "csv" | "excel" | "pdf" | "image";
  fileSize: number;
  status: "uploading" | "processing" | "completed" | "failed";
  aiSummary: string | null;
  metadata: Record<string, any>;
  createdAt: string;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  fileCount: number;
  createdAt: string;
}

export interface FileUploadResponse {
  fileId: string;
  storageUrl: string;
  status: string;
  message: string;
}

export interface UploadProgress {
  file: File;
  progress: number;
  status: "pending" | "uploading" | "processing" | "completed" | "error";
  error: string | null;
}
