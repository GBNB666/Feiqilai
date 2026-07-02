import { useState, useCallback } from "react";
import { uploadFile } from "../../services/api";
import type { JobResponse } from "../../types";

export function useFileUpload() {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [job, setJob] = useState<JobResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const upload = useCallback(async (file: File) => {
    setUploading(true);
    setProgress(0);
    setError(null);
    try {
      const result = await uploadFile(file, (pct) => setProgress(pct));
      setJob(result);
      return result;
    } catch (e: any) {
      setError(e.message);
      return null;
    } finally {
      setUploading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setJob(null);
    setProgress(0);
    setError(null);
  }, []);

  return { uploading, progress, job, error, upload, reset };
}
