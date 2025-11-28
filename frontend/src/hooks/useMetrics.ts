// src/hooks/useMetrics.ts
import { useCallback, useEffect, useRef, useState } from "react";
import { getApiUrl } from "@/api/config";

export type Metrics = {
  by_label: Record<string, number>;
  total: number;
};

export function useMetrics() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const fetchMetrics = useCallback(async () => {
    setLoading(true);
    setError(null);
    abortRef.current?.abort();
    const ac = new AbortController();
    abortRef.current = ac;
    try {
      const res = await fetch(getApiUrl("metrics"), { signal: ac.signal });
      if (!res.ok) {
        throw new Error(`Status ${res.status}`);
      }
      const j = await res.json();
      setMetrics(j.metrics ?? { by_label: {}, total: 0 });
    } catch (err: any) {
      if (err?.name === "AbortError") {
        // aborted, ignore
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

  return { metrics, loading, error, refresh: fetchMetrics };
}
