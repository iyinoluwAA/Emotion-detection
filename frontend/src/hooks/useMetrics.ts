// src/hooks/useMetrics.ts
import { useCallback, useEffect, useRef, useState } from "react";
import { getApiUrl } from "@/api/config";
import { getCachedData, setCachedData } from "@/utils/cache";

export type Metrics = {
  by_label: Record<string, number>;
  total: number;
};

type CachedMetrics = {
  metrics: Metrics;
  timestamp: number;
};

export function useMetrics() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isCached, setIsCached] = useState(false);
  const [lastSynced, setLastSynced] = useState<Date | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  // Load cached data on mount
  useEffect(() => {
    const cached = getCachedData<CachedMetrics>("metrics");
    if (cached) {
      setMetrics(cached.metrics);
      setLastSynced(new Date(cached.timestamp));
      setIsCached(true);
    }
  }, []);

  const fetchMetrics = useCallback(async () => {
    setLoading(true);
    setError(null);
    setIsCached(false);
    abortRef.current?.abort();
    const ac = new AbortController();
    abortRef.current = ac;
    try {
      const res = await fetch(getApiUrl("metrics"), { signal: ac.signal });
      if (!res.ok) {
        throw new Error(`Status ${res.status}`);
      }
      const j = await res.json();
      const fetchedMetrics = j.metrics ?? { by_label: {}, total: 0 };
      
      setMetrics(fetchedMetrics);
      setLastSynced(new Date());
      setIsCached(false);
      
      // Cache successful response
      setCachedData<CachedMetrics>("metrics", {
        metrics: fetchedMetrics,
        timestamp: Date.now(),
      });
    } catch (err: any) {
      if (err?.name === "AbortError") {
        // aborted, ignore
        return;
      }
      
      // Fall back to cached data if available
      const cached = getCachedData<CachedMetrics>("metrics");
      if (cached) {
        setMetrics(cached.metrics);
        setLastSynced(new Date(cached.timestamp));
        setIsCached(true);
        setError(null); // Don't show error if we have cached data
      } else {
        setError(err?.message ?? String(err));
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchMetrics();
    const id = setInterval(() => {
      void fetchMetrics();
    }, 15000);
    return () => {
      clearInterval(id);
      abortRef.current?.abort();
    };
  }, [fetchMetrics]);

  return { metrics, loading, error, refresh: fetchMetrics, isCached, lastSynced };
}
