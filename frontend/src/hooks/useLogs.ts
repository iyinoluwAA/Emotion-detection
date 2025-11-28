import { useCallback, useEffect, useState } from "react";
import { getApiUrl } from "@/api/config";
import { getCachedData, setCachedData } from "@/utils/cache";

export type LogRow = {
  id?: number;
  ts?: string;
  filename?: string;
  image_path?: string;  // Stored image filename from backend (e.g., "abc123_capture.jpg")
  emotion?: string;
  confidence?: number;
};

type CachedLogs = {
  logs: LogRow[];
  timestamp: number;
};

export function useLogs(limit = 20) {
  const [logs, setLogs] = useState<LogRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isCached, setIsCached] = useState(false);
  const [lastSynced, setLastSynced] = useState<Date | null>(null);

  // Load cached data on mount
  useEffect(() => {
    const cached = getCachedData<CachedLogs>(`logs_${limit}`);
    if (cached) {
      setLogs(cached.logs);
      setLastSynced(new Date(cached.timestamp));
      setIsCached(true);
    }
  }, [limit]);

  const fetchLogs = useCallback(async (logLimit = limit) => {
    setLoading(true);
    setError(null);
    setIsCached(false);
    
    try {
      const res = await fetch(`${getApiUrl("logs")}?limit=${logLimit}`);
      if (!res.ok) {
        throw new Error(`Status ${res.status}`);
      }
      const json = await res.json();
      const fetchedLogs = json.logs || [];
      
      setLogs(fetchedLogs);
      setLastSynced(new Date());
      setIsCached(false);
      
      // Cache successful response
      setCachedData<CachedLogs>(`logs_${logLimit}`, {
        logs: fetchedLogs,
        timestamp: Date.now(),
      });
    } catch (err) {
      console.error("fetchLogs", err);
      setError(err instanceof Error ? err.message : "Failed to fetch logs");
      
      // Fall back to cached data if available
      const cached = getCachedData<CachedLogs>(`logs_${logLimit}`);
      if (cached) {
        setLogs(cached.logs);
        setLastSynced(new Date(cached.timestamp));
        setIsCached(true);
        setError(null); // Don't show error if we have cached data
      }
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    void fetchLogs();
  }, [fetchLogs]);

  return { logs, loading, error, fetchLogs, isCached, lastSynced };
}

