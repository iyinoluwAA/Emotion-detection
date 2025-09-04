import React, { useEffect, useState, useCallback } from "react";
import { Grid, Container, Title, Space, Text } from "@mantine/core";
import logo from "@/assets/Emotion-detection logo.png";

import { CameraSpace } from "@/components/Camera/CameraSpace";
import { TableReviews } from "@/components/TableReviews/TableReviews";
import { StatsGrid } from "@/components/StatsGrid/StatsGrid";
import { StatsRingCard } from "@/components/StatsRingCard/StatsRingCard";
import { uploadImage } from "@/api/client";

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

export function HomePage() {
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
    }
  }, []);

  useEffect(() => {
    void fetchLogs(20);
    void fetchMetrics();
  }, [fetchLogs, fetchMetrics]);

  // robust submitFile (see next section snippet if you want only the function)
    const submitFile = useCallback(
    async (file: Blob | File, filename = "upload.jpg") => {
      try {
        const json = await uploadImage(API_URL, file, filename);
        return json;
      } finally {
        // ALWAYS refresh logs & metrics after attempt (success OR failure)
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
  }, []);

  const tableRows: TableRow[] = logs.map((l) => {
    const conf = typeof l.confidence === "number" ? Math.round((l.confidence ?? 0) * 100) : 0;
    return {
      image: l.filename ?? "upload",
      emotions: l.emotion ?? "-",
      timestap: l.ts ?? "-",
      reviews: { positive: conf, negative: Math.max(0, 100 - conf) },
    };
  });

  const statsItems =
    metrics && Object.keys(metrics.by_label || {}).length > 0
      ? Object.entries(metrics.by_label).map(([k, v]) => ({ title: k, value: String(v), diff: 0 }))
      : [
          { title: "Predictions", value: String(metrics?.total ?? logs.length), diff: 0 },
          { title: "Successful", value: String(Math.round((metrics?.total ?? logs.length) * 0.9)), diff: 3 },
          { title: "Failed", value: String(Math.round((metrics?.total ?? logs.length) * 0.1)), diff: -3 },
          { title: "Active", value: "1", diff: 0 },
        ];

  const ringBreakdown =
    metrics && metrics.by_label
      ? Object.entries(metrics.by_label).map(([label, count]) => ({ label, count: Number(count) }))
      : [{ label: "happy", count: 0 }, { label: "neutral", count: 0 }];

  return (
    <Container size="xl" py="xl">
      <div style={{ textAlign: "center" }}>
        <img src={logo} alt="Emotion Detection Logo" width={40} height={40} />
        <Title order={2}>Emotion Detection</Title>
      </div>
      <Space h="md" />

      {/* Grid with gutter for spacing */}
      <Grid gutter="lg">
        {/* Left: Camera and controls */}
        <Grid.Col span={12} >
          <CameraSpace submitFile={submitFile} onRefreshLogs={() => fetchLogs(8)} onClearLogs={() => clearLogs()} />
          <Space h="md" />
          <Text size="sm" color="dimmed">
            {error ? `Error: ${error}` : loadingLogs ? "Loading logs..." : `Recent predictions: ${logs.length}`}
          </Text>
        </Grid.Col>

        {/* Right: Stats (stacked) */}
        <Grid.Col span={12} >
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <StatsGrid items={statsItems} />
            <StatsRingCard total={metrics?.total ?? logs.length} completed={metrics?.by_label?.happy ?? 0} breakdown={ringBreakdown} />
          </div>
        </Grid.Col>

        {/* Below: Table (full width) */}
        <Grid.Col span={12}>
          <TableReviews rows={tableRows} />
        </Grid.Col>
      </Grid>
    </Container>
  );
}