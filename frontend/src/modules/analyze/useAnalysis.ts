import { useState, useCallback } from "react";
import { api } from "../../services/api";

export function useAnalysis() {
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = useCallback(async (jobId: string) => {
    setAnalyzing(true);
    setError(null);
    try {
      return await api.analyze(jobId);
    } catch (e: any) {
      setError(e.message);
      return null;
    } finally {
      setAnalyzing(false);
    }
  }, []);

  return { analyzing, error, analyze };
}
