import { useCallback, useRef } from "react";
import UploadProgress from "./UploadProgress";

interface Props {
  onUpload: (file: File) => void;
  uploading: boolean;
  progress: number;
}

export default function FileUploader({ onUpload, uploading, progress }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const file = e.dataTransfer.files[0];
      if (file) onUpload(file);
    },
    [onUpload]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) onUpload(file);
    },
    [onUpload]
  );

  return (
    <div
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      onClick={() => { if (!uploading) inputRef.current?.click(); }}
      className="group border-2 border-dashed border-gray-300 rounded-2xl p-12 text-center cursor-pointer hover:border-indigo-400 hover:bg-indigo-50/40 transition-all duration-300 hover:scale-[1.01] active:scale-[0.99]"
    >
      {uploading ? (
        <UploadProgress progress={progress} />
      ) : (
        <div className="space-y-3 animate-fade-in">
          {/* File icon — SVG replacing emoji */}
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-indigo-50 group-hover:bg-indigo-100 transition-colors duration-300">
            <svg className="w-8 h-8 text-indigo-500 group-hover:text-indigo-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 11v6m-3-3h6" />
            </svg>
          </div>
          <p className="text-gray-700 font-semibold text-base">点击或拖拽上传论文</p>
          <p className="text-gray-400 text-sm">支持 .docx / .pdf，最大 20MB</p>
        </div>
      )}
      <input ref={inputRef} type="file" accept=".docx,.pdf" onChange={handleChange} className="hidden" />
    </div>
  );
}
