/**
 * Hook to check backend health and availability
 * Automatically detects if backend is online/offline
 */
import { useState, useEffect, useCallback } from "react";
import { getApiBaseUrl } from "@/api/config";

export type BackendStatus = "checking" | "online" | "offline";

interface BackendHealth {
  status: BackendStatus;
  isOnline: boolean;
  lastChecked: Date | null;
  error: Error | null;
}

const HEALTH_CHECK_INTERVAL = 30000; // Check every 30 seconds
const HEALTH_CHECK_TIMEOUT = 5000; // 5 second timeout

export function useBackendHealth(): BackendHealth & { checkHealth: () => Promise<void> } {
  const [status, setStatus] = useState<BackendStatus>("checking");
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [error, setError] = useState<Error | null>(null);

  const checkHealth = useCallback(async () => {
    try {
      setStatus("checking");
      setError(null);

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), HEALTH_CHECK_TIMEOUT);

      const response = await fetch(`${getApiBaseUrl()}/health`, {
        method: "GET",
        signal: controller.signal,
        headers: {
          "Content-Type": "application/json",
        },
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        const data = await response.json();
        // Backend is online if health endpoint returns 200
        setStatus("online");
        setError(null);
        setLastChecked(new Date());
      } else {
        // Backend responded but with error status
        setStatus("offline");
        setError(new Error(`Backend returned status ${response.status}`));
        setLastChecked(new Date());
      }
    } catch (err) {
      // Network error, CORS error, timeout, etc.
      setStatus("offline");
      const error = err instanceof Error ? err : new Error("Unknown error");
      setError(error);
      setLastChecked(new Date());
    }
  }, []);

  // Initial check on mount
  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  // Periodic health checks
  useEffect(() => {
    const interval = setInterval(() => {
      checkHealth();
    }, HEALTH_CHECK_INTERVAL);

    return () => clearInterval(interval);
  }, [checkHealth]);

  return {
    status,
    isOnline: status === "online",
    lastChecked,
    error,
    checkHealth,
  };
}

