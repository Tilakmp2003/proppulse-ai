import { useState, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, File, X, Check } from "lucide-react";
import { cn } from "@/lib/utils";

interface UploadBoxProps {
  title: string;
  description: string;
  acceptedTypes: string[];
  onFileSelect: (file: File) => void;
  selectedFile?: File | null;
  disabled?: boolean;
}

export function UploadBox({
  title,
  description,
  acceptedTypes,
  onFileSelect,
  selectedFile,
  disabled = false,
}: UploadBoxProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) {
      setIsDragOver(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    if (disabled) return;

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const clearFile = () => {
    onFileSelect(null as any);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <Card
      className={cn(
        "transition-all duration-200",
        isDragOver && "border-primary bg-primary/5",
        disabled && "opacity-50 cursor-not-allowed"
      )}
    >
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
        <p className="text-sm text-gray-600">{description}</p>
      </CardHeader>
      <CardContent>
        <div
          className={cn(
            "border-2 border-dashed rounded-lg p-8 text-center transition-colors",
            isDragOver ? "border-primary bg-primary/5" : "border-gray-300",
            disabled
              ? "cursor-not-allowed"
              : "cursor-pointer hover:border-primary hover:bg-gray-50"
          )}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={!disabled ? handleBrowseClick : undefined}
        >
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept={acceptedTypes.join(",")}
            onChange={handleFileSelect}
            disabled={disabled}
          />

          {selectedFile ? (
            <div className="flex items-center justify-center space-x-3">
              <div className="flex items-center space-x-2">
                <File className="h-6 w-6 text-primary" />
                <span className="text-sm font-medium">{selectedFile.name}</span>
                <Check className="h-5 w-5 text-green-500" />
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  clearFile();
                }}
                disabled={disabled}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <Upload className="h-12 w-12 text-gray-400 mx-auto" />
              <div>
                <p className="text-sm font-medium text-gray-900">
                  Drop your file here, or{" "}
                  <span className="text-primary">browse</span>
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Supports: {acceptedTypes.join(", ")}
                </p>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
