// Type definitions for Sichelgaita.AI

// File type categories matching backend enum
export type FileType = "csv" | "excel" | "pdf" | "image";

// File extension to type category mapping
export const FILE_EXTENSION_MAP: Record<string, FileType> = {
  ".csv": "csv",
  ".xlsx": "excel",
  ".xls": "excel",
  ".pdf": "pdf",
  ".png": "image",
  ".jpg": "image",
  ".jpeg": "image",
};

export interface FileMetadata {
  id: string;
  filename: string;
  fileType: FileType;
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
