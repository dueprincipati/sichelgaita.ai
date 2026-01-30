"use client";

import { FolderKanban, Folder, Plus, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Project } from "@/types";
import { cn } from "@/lib/utils";

interface ProjectSidebarProps {
  projects: Project[];
  selectedProjectId: string | null;
  onProjectSelect: (projectId: string) => void;
  onNewProject: () => void;
}

export function ProjectSidebar({
  projects,
  selectedProjectId,
  onProjectSelect,
  onNewProject,
}: ProjectSidebarProps) {
  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-neutral-200">
        <div className="flex items-center space-x-2 mb-4">
          <FolderKanban className="h-6 w-6 text-primary" />
          <h2 className="text-lg font-semibold text-neutral-900">Workspace</h2>
        </div>
        <Button
          onClick={onNewProject}
          className="w-full justify-start"
          variant="default"
          size="sm"
        >
          <Plus className="h-4 w-4 mr-2" />
          Nuovo Progetto
        </Button>
      </div>

      {/* Projects List */}
      <ScrollArea className="flex-1 px-2 py-2">
        <div className="space-y-1">
          {projects.map((project) => (
            <Button
              key={project.id}
              variant={selectedProjectId === project.id ? "secondary" : "ghost"}
              className="w-full justify-start text-left"
              onClick={() => onProjectSelect(project.id)}
            >
              <Folder
                className={cn(
                  "h-4 w-4 mr-2 flex-shrink-0",
                  selectedProjectId === project.id
                    ? "text-primary"
                    : "text-neutral-500"
                )}
              />
              <div className="flex-1 min-w-0">
                <div className="truncate font-medium">{project.name}</div>
                {project.description && (
                  <div className="text-xs text-neutral-500 truncate">
                    {project.description}
                  </div>
                )}
              </div>
              {project.fileCount > 0 && (
                <span className="ml-2 inline-flex items-center justify-center h-5 min-w-[20px] px-1.5 text-xs font-medium rounded-full bg-neutral-200 text-neutral-700">
                  {project.fileCount}
                </span>
              )}
            </Button>
          ))}
          {projects.length === 0 && (
            <div className="text-center py-8 px-4">
              <p className="text-sm text-neutral-500">
                Nessun progetto. Crea il tuo primo progetto per iniziare.
              </p>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="p-4 border-t border-neutral-200">
        <Button variant="ghost" className="w-full justify-start" size="sm">
          <User className="h-4 w-4 mr-2" />
          Account
        </Button>
      </div>
    </div>
  );
}
