import { useCallback, useEffect, useState } from "react";
import { getApiUrl } from "@/api/config";

export type LogRow = {
  id?: number;
  ts?: string;
  filename?: string;
  emotion?: string;
  confidence?: number;
};

export function useLogs(limit = 20) {
  const [logs, setLogs] = useState<LogRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchLogs = useCallback(async (logLimit = limit) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${getApiUrl("logs")}?limit=${logLimit}`);
      if (!res.ok) {
        throw new Error(`Status ${res.status}`);
      }
      const json = await res.json();
      setLogs(json.logs || []);
    } catch (err) {
      console.error("fetchLogs", err);
      setError(err instanceof Error ? err.message : "Failed to fetch logs");
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    void fetchLogs();
  }, [fetchLogs]);

  return { logs, loading, error, fetchLogs };
}

