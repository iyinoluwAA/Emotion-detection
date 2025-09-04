import React, { useEffect, useState, useCallback } from "react";
import { Grid, Container, Title, Space, Text } from "@mantine/core";

import { CameraSpace } from "@/components/Camera/CameraSpace";
import { TableReviews } from "@/components/TableReviews/TableReviews";
import { StatsGrid } from "@/components/StatsGrid/StatsGrid";
import { StatsRingCard } from "@/components/StatsRingCard/StatsRingCard";
import { ActionToggle } from "@/components/ColorSchemeToggle/ActionToggle";

type LogRowBackend = {
  id?: number;
  ts?: string;
  filename?: string;
  emotion?: string;
  confidence?: number;
};

type TableRow = {
  image: string;
  emotions?: string;
  timestap?: number | string;
  reviews: { positive: number; negative: number };
};

const API_URL = import.meta.env.VITE_API_URL || "https://emotion-detection-1-8avi.onrender.com";

export function TestPage() {
  const [logs, setLogs] = useState<LogRowBackend[]>([]);
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<any>(null);

  const fetchLogs = useCallback(async (limit = 20) => {
    setLoadingLogs(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/logs?limit=${limit}`);
      if (!res.ok) {throw new Error(`Status ${res.status}`)};
      const json = await res.json();
      setLogs(json.logs || []);
    } catch (err) {
      console.error("fetchLogs", err);
      setError("Failed to fetch logs");
    } finally {
      setLoadingLogs(false);
    }
  }, []);

  const fetchMetrics = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/metrics`);
      if (!res.ok) {throw new Error(`Status ${res.status}`)};
      const json = await res.json();
      setMetrics(json.metrics ?? null);
    } catch (err) {
      console.warn("fetchMetrics failed", err);
      // non-fatal — keep whatever metrics state we had
    }
  }, []);

  useEffect(() => {
    void fetchLogs(20);
    void fetchMetrics();
  }, [fetchLogs, fetchMetrics]);

  // submitFile: send form-data to backend /detect
  const submitFile = useCallback(
    async (file: Blob | File, filename = "upload.jpg") => {
      const fd = new FormData();
      fd.append("image", file, filename);

      try {
        const res = await fetch(`${API_URL}/detect`, {
          method: "POST",
          body: fd,
        });
        if (!res.ok) {
          const txt = await res.text().catch(() => "");
          throw new Error(`Server ${res.status}: ${txt}`);
        }
        const json = await res.json();
        return json;
      } finally {
        // ALWAYS refresh logs and metrics after any attempt (success or failure).
        // This ensures failed/low-confidence predictions appear immediately.
        try {
          await fetchLogs(20);
        } catch (err) {
          console.warn("Failed to refresh logs after submit:", err);
        }
        try {
          await fetchMetrics();
        } catch (err) {
          console.warn("Failed to refresh metrics after submit:", err);
        }
      }
    },
    [fetchLogs, fetchMetrics]
  );

  const clearLogs = useCallback(() => {
    setLogs([]);
    // optionally call backend endpoint to clear DB if you have one
  }, []);

  // Map backend logs to TableReviews rows (simple mapping)
  const tableRows: TableRow[] = logs.map((l) => {
    const conf = typeof l.confidence === "number" ? Math.round((l.confidence ?? 0) * 100) : 0;
    return {
      image: l.filename ?? "upload",
      emotions: l.emotion ?? "-",
      timestap: l.ts ?? "-",
      reviews: { positive: conf, negative: Math.max(0, 100 - conf) },
    };
  });

  // basic statsItems example from metrics (or fallback static)
  const statsItems =
    metrics && Object.keys(metrics.by_label || {}).length > 0
      ? Object.entries(metrics.by_label).map(([k, v]) => ({ title: k, value: String(v), diff: 0 }))
      : [
          { title: "Predictions", value: String(metrics?.total ?? logs.length), diff: 0 },
          { title: "Successful", value: String(Math.round((metrics?.total ?? logs.length) * 0.9)), diff: 3 },
          { title: "Failed", value: String(Math.round((metrics?.total ?? logs.length) * 0.1)), diff: -3 },
          { title: "Active", value: "1", diff: 0 },
        ];

  // ring breakdown example
  const ringBreakdown =
    metrics && metrics.by_label
      ? Object.entries(metrics.by_label).map(([label, count]) => ({ label, count: Number(count) }))
      : [{ label: "happy", count: 0 }, { label: "neutral", count: 0 }];

  return (
    <Container size="xl" py="xl">
      <div style={{ textAlign: "center" }}>
        <Title order={2}>Emotion Detection</Title>
      </div>
      <Space h="md" />

      <Grid gutter="md">
        {/* Left: Camera and controls */}
        <Grid.Col span={12} md={7}>
          <CameraSpace
            submitFile={submitFile}
            onRefreshLogs={() => fetchLogs(8)}
            onClearLogs={() => clearLogs()}
          />
          <Space h="md" />
          <Text size="sm" color="dimmed">
            {error ? `Error: ${error}` : loadingLogs ? "Loading logs..." : `Recent predictions: ${logs.length}`}
          </Text>
        </Grid.Col>

        {/* Right: Stats */}
        <Grid.Col span={12} md={5}>
          <StatsGrid items={statsItems} />
          <Space h="md" />
          <StatsRingCard
            total={metrics?.total ?? logs.length}
            completed={metrics?.by_label?.happy ?? 0}
            breakdown={ringBreakdown}
          />
        </Grid.Col>

        {/* Below: Table (only visible when tableRows.length > 0) */}
        <Grid.Col span={12}>
          <TableReviews rows={tableRows} />
        </Grid.Col>
      </Grid>
      <ActionToggle />
    </Container>
  );
}