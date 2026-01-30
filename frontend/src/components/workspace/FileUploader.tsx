"use client";

import { useState, useRef, DragEvent, ChangeEvent } from "react";
import { Upload, X } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { uploadFile } from "@/lib/api";
import { UploadProgress } from "@/types";
import { cn, formatFileSize } from "@/lib/utils";

interface FileUploaderProps {
  projectId?: string;
  onUploadComplete?: (fileId: string) => void;
}

const ALLOWED_EXTENSIONS = [".csv", ".xlsx", ".xls", ".pdf", ".png", ".jpg", ".jpeg"];
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50 MB

export function FileUploader({ projectId, onUploadComplete }: FileUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadQueue, setUploadQueue] = useState<UploadProgress[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    const fileExt = `.${file.name.split(".").pop()?.toLowerCase()}`;
    
    if (!ALLOWED_EXTENSIONS.includes(fileExt)) {
      return `File type not supported. Allowed: ${ALLOWED_EXTENSIONS.join(", ")}`;
    }
    
    if (file.size > MAX_FILE_SIZE) {
      return `File too large. Maximum size: ${formatFileSize(MAX_FILE_SIZE)}`;
    }
    
    return null;
  };

  const handleFiles = async (files: FileList | null) => {
    if (!files) return;

    const validFiles: File[] = [];
    const newQueue: UploadProgress[] = [];

    Array.from(files).forEach((file) => {
      const error = validateFile(file);
      if (error) {
        newQueue.push({
          file,
          progress: 0,
          status: "error",
          error,
        });
      } else {
        validFiles.push(file);
        newQueue.push({
          file,
          progress: 0,
          status: "pending",
          error: null,
        });
      }
    });

    setUploadQueue((prev) => [...prev, ...newQueue]);

    // Upload valid files
    for (let i = 0; i < validFiles.length; i++) {
      const file = validFiles[i];
      const queueIndex = uploadQueue.length + i;

      try {
        // Update status to uploading
        setUploadQueue((prev) =>
          prev.map((item, idx) =>
            idx === queueIndex ? { ...item, status: "uploading", progress: 50 } : item
          )
        );

        const response = await uploadFile(file, projectId);

        // Update status to processing
        setUploadQueue((prev) =>
          prev.map((item, idx) =>
            idx === queueIndex ? { ...item, status: "processing", progress: 75 } : item
          )
        );

        // Simulate processing completion (in production, poll backend for status)
        setTimeout(() => {
          setUploadQueue((prev) =>
            prev.map((item, idx) =>
              idx === queueIndex ? { ...item, status: "completed", progress: 100 } : item
            )
          );

          if (onUploadComplete) {
            onUploadComplete(response.fileId);
          }
        }, 1000);
      } catch (error) {
        setUploadQueue((prev) =>
          prev.map((item, idx) =>
            idx === queueIndex
              ? {
                  ...item,
                  status: "error",
                  progress: 0,
                  error: error instanceof Error ? error.message : "Upload failed",
                }
              : item
          )
        );
      }
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const removeFromQueue = (index: number) => {
    setUploadQueue((prev) => prev.filter((_, idx) => idx !== index));
  };

  return (
    <div className="space-y-4">
      <Card
        className={cn(
          "border-2 border-dashed border-neutral-300 p-8 text-center cursor-pointer transition-all hover:border-neutral-400",
          isDragging && "border-primary bg-primary/5"
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <div className="flex flex-col items-center justify-center space-y-4">
          <div
            className={cn(
              "rounded-full bg-neutral-100 p-4 transition-colors",
              isDragging && "bg-primary/10"
            )}
          >
            <Upload
              className={cn(
                "h-8 w-8 text-neutral-400",
                isDragging && "text-primary"
              )}
            />
          </div>
          <div>
            <p className="text-lg font-medium text-neutral-900">
              Trascina file qui o clicca per selezionare
            </p>
            <p className="text-sm text-neutral-500 mt-1">
              Supportati: CSV, Excel, PDF, Immagini (max {formatFileSize(MAX_FILE_SIZE)})
            </p>
          </div>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={ALLOWED_EXTENSIONS.join(",")}
          onChange={handleFileInputChange}
          className="hidden"
          aria-label="File upload input"
        />
      </Card>

      {uploadQueue.length > 0 && (
        <div className="space-y-2">
          {uploadQueue.map((item, index) => (
            <Card key={index} className="p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-neutral-900 truncate">
                    {item.file.name}
                  </p>
                  <p className="text-xs text-neutral-500">
                    {formatFileSize(item.file.size)}
                  </p>
                </div>
                <div className="flex items-center space-x-2 ml-4">
                  <span
                    className={cn(
                      "text-xs font-medium px-2 py-1 rounded",
                      item.status === "completed" && "bg-green-100 text-green-700",
                      item.status === "uploading" && "bg-blue-100 text-blue-700",
                      item.status === "processing" && "bg-yellow-100 text-yellow-700",
                      item.status === "error" && "bg-red-100 text-red-700",
                      item.status === "pending" && "bg-neutral-100 text-neutral-700"
                    )}
                  >
                    {item.status === "completed" && "✓ Completato"}
                    {item.status === "uploading" && "⟳ Caricamento..."}
                    {item.status === "processing" && "⚙ Elaborazione..."}
                    {item.status === "error" && "✗ Errore"}
                    {item.status === "pending" && "In attesa..."}
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFromQueue(index)}
                    className="h-6 w-6 p-0"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              {item.status !== "error" && (
                <Progress value={item.progress} className="h-1" />
              )}
              {item.error && (
                <p className="text-xs text-red-600 mt-2">{item.error}</p>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
