"use client";

import { MoreVertical } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileMetadata } from "@/types";
import { cn, formatFileSize, formatRelativeTime, getFileIcon } from "@/lib/utils";

interface FileCardProps {
  file: FileMetadata;
  isSelected: boolean;
  onClick: () => void;
}

export function FileCard({ file, isSelected, onClick }: FileCardProps) {
  const FileIcon = getFileIcon(file.fileType);

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      completed: { label: "Completato", className: "bg-green-100 text-green-700" },
      processing: { label: "Elaborazione", className: "bg-yellow-100 text-yellow-700" },
      failed: { label: "Errore", className: "bg-red-100 text-red-700" },
      uploading: { label: "Caricamento", className: "bg-blue-100 text-blue-700" },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || {
      label: status,
      className: "bg-neutral-100 text-neutral-700",
    };

    return (
      <span
        className={cn(
          "text-xs font-medium px-2 py-1 rounded",
          config.className
        )}
      >
        {config.label}
      </span>
    );
  };

  return (
    <Card
      className={cn(
        "cursor-pointer transition-all hover:shadow-md",
        isSelected && "ring-2 ring-primary"
      )}
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3 flex-1 min-w-0">
            <div className="rounded-lg bg-primary/10 p-2">
              <FileIcon className="h-5 w-5 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <CardTitle className="text-base truncate" title={file.filename}>
                {file.filename}
              </CardTitle>
              <CardDescription className="text-xs">
                {formatFileSize(file.fileSize)}
              </CardDescription>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0 -mt-1"
            onClick={(e) => {
              e.stopPropagation();
              // TODO: Open context menu
            }}
          >
            <MoreVertical className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center justify-between">
          {getStatusBadge(file.status)}
          <span className="text-xs text-neutral-500">
            {formatRelativeTime(file.createdAt)}
          </span>
        </div>
        {file.aiSummary && (
          <div className="pt-2 border-t border-neutral-100">
            <p className="text-xs text-neutral-600 line-clamp-2">
              {file.aiSummary.substring(0, 100)}
              {file.aiSummary.length > 100 && "..."}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
