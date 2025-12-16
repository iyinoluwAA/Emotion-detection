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

const HEALTH_CHECK_INTERVAL = 60000; // Check every 60 seconds (less aggressive)
const HEALTH_CHECK_TIMEOUT = 10000; // 10 second timeout (Render can be slow on free tier)
const MAX_CONSECUTIVE_FAILURES = 2; // Mark offline only after 2 consecutive failures

export function useBackendHealth(): BackendHealth & { checkHealth: () => Promise<void> } {
  const [status, setStatus] = useState<BackendStatus>("checking");
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [consecutiveFailures, setConsecutiveFailures] = useState(0);

  const checkHealth = useCallback(async () => {
    try {
      // Don't show "checking" on every poll - only on initial load
      if (status === "checking") {
        setStatus("checking");
      }
      setError(null);

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), HEALTH_CHECK_TIMEOUT);

      const response = await fetch(`${getApiBaseUrl()}/health`, {
        method: "GET",
        signal: controller.signal,
        headers: {
          "Content-Type": "application/json",
        },
        // Add cache control to prevent browser caching
        cache: "no-cache",
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        const data = await response.json();
        // Backend is online if health endpoint returns 200
        setStatus("online");
        setError(null);
        setConsecutiveFailures(0); // Reset failure counter
        setLastChecked(new Date());
      } else {
        // Backend responded but with error status
        const newFailures = consecutiveFailures + 1;
        setConsecutiveFailures(newFailures);
        
        // Only mark offline after multiple consecutive failures
        if (newFailures >= MAX_CONSECUTIVE_FAILURES) {
          setStatus("offline");
          setError(new Error(`Backend returned status ${response.status}`));
        }
        // Otherwise keep current status (don't flip to offline on single failure)
        setLastChecked(new Date());
      }
    } catch (err) {
      // Network error, CORS error, timeout, etc.
      const newFailures = consecutiveFailures + 1;
      setConsecutiveFailures(newFailures);
      
      // Only mark offline after multiple consecutive failures
      // This prevents false "offline" from temporary network issues
      if (newFailures >= MAX_CONSECUTIVE_FAILURES) {
        setStatus("offline");
        const error = err instanceof Error ? err : new Error("Unknown error");
        setError(error);
      }
      // Otherwise keep current status (resilient to temporary failures)
      setLastChecked(new Date());
    }
  }, [status, consecutiveFailures]);

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


