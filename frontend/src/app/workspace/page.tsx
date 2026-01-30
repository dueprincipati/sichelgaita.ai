"use client";

import { useState } from "react";
import { FileUploader } from "@/components/workspace/FileUploader";
import { FileCard } from "@/components/workspace/FileCard";
import { ProjectSidebar } from "@/components/workspace/ProjectSidebar";
import { FileMetadata, Project } from "@/types";

export default function WorkspacePage() {
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<FileMetadata[]>([]);

  // Mock projects data - will be replaced with API call in future
  const [projects] = useState<Project[]>([
    {
      id: "1",
      name: "Progetto Demo",
      description: "Primo progetto di esempio",
      fileCount: 0,
      createdAt: new Date().toISOString(),
    },
  ]);

  const handleUploadComplete = (fileId: string) => {
    // In production, fetch the new file metadata from backend
    // For now, we'll add a placeholder
    const newFile: FileMetadata = {
      id: fileId,
      filename: "Nuovo file",
      fileType: "csv",
      fileSize: 0,
      status: "completed",
      aiSummary: null,
      metadata: {},
      createdAt: new Date().toISOString(),
    };
    setUploadedFiles((prev) => [newFile, ...prev]);
  };

  const handleProjectSelect = (projectId: string) => {
    setSelectedProjectId(projectId);
    // In production, fetch files for this project
  };

  const handleNewProject = () => {
    // TODO: Open dialog to create new project
    console.log("Create new project");
  };

  const selectedFile = uploadedFiles.find((file) => file.id === selectedFileId);

  return (
    <div className="flex h-screen bg-neutral-50">
      {/* Sidebar - Projects */}
      <div className="w-64 border-r border-neutral-200 bg-white">
        <ProjectSidebar
          projects={projects}
          selectedProjectId={selectedProjectId}
          onProjectSelect={handleProjectSelect}
          onNewProject={handleNewProject}
        />
      </div>

      {/* Main Canvas Area */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold text-neutral-900 mb-2">
              Data Workspace
            </h1>
            <p className="text-neutral-600">
              Carica e analizza i tuoi file con intelligenza artificiale
            </p>
          </div>

          {/* File Uploader */}
          <FileUploader
            projectId={selectedProjectId || undefined}
            onUploadComplete={handleUploadComplete}
          />

          {/* Files Grid */}
          {uploadedFiles.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold text-neutral-900 mb-4">
                File Caricati ({uploadedFiles.length})
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {uploadedFiles.map((file) => (
                  <FileCard
                    key={file.id}
                    file={file}
                    isSelected={file.id === selectedFileId}
                    onClick={() => setSelectedFileId(file.id)}
                  />
                ))}
              </div>
            </div>
          )}

          {uploadedFiles.length === 0 && (
            <div className="text-center py-12">
              <p className="text-neutral-500">
                Nessun file caricato. Inizia caricando il tuo primo file.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Details Panel */}
      <div className="w-80 border-l border-neutral-200 bg-white p-6">
        <h2 className="text-lg font-semibold text-neutral-900 mb-4">
          Dettagli File
        </h2>
        {selectedFile ? (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-neutral-700 mb-1">
                Nome File
              </h3>
              <p className="text-sm text-neutral-900">{selectedFile.filename}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-neutral-700 mb-1">Tipo</h3>
              <p className="text-sm text-neutral-900 capitalize">
                {selectedFile.fileType}
              </p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-neutral-700 mb-1">
                Stato
              </h3>
              <p className="text-sm text-neutral-900 capitalize">
                {selectedFile.status}
              </p>
            </div>
            {selectedFile.aiSummary && (
              <div>
                <h3 className="text-sm font-medium text-neutral-700 mb-1">
                  Riepilogo AI
                </h3>
                <p className="text-sm text-neutral-600">
                  {selectedFile.aiSummary}
                </p>
              </div>
            )}
            {selectedFile.metadata && Object.keys(selectedFile.metadata).length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-neutral-700 mb-2">
                  Metadata
                </h3>
                <div className="space-y-1">
                  {Object.entries(selectedFile.metadata).map(([key, value]) => (
                    <div key={key} className="text-sm">
                      <span className="text-neutral-600">{key}:</span>{" "}
                      <span className="text-neutral-900">
                        {typeof value === "object"
                          ? JSON.stringify(value)
                          : String(value)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-neutral-500">
            Seleziona un file per vedere i dettagli
          </p>
        )}
      </div>
    </div>
  );
}
