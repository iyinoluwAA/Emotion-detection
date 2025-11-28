import React, { useCallback, useMemo } from "react";
import { Grid, Container, Title, Text, Box, Group, Stack, Paper, Badge, Divider, ActionIcon, Tooltip, Pagination, Select } from "@mantine/core";
import { IconRefresh, IconWifi, IconWifiOff, IconLoader } from "@tabler/icons-react";
import { notifications } from "@mantine/notifications";
import logo from "@/assets/Emotion-detection logo.png";

import { ActionToggle } from "@/components/ColorSchemeToggle/ActionToggle";
import { CameraSpace } from "@/components/Camera/CameraSpace";
import { TableReviews } from "@/components/TableReviews/TableReviews";
import { StatsGrid } from "@/components/StatsGrid/StatsGrid";
import { StatsRingCard } from "@/components/StatsRingCard/StatsRingCard";
import { TableControls } from "@/components/TableControls/TableControls";
import { EmotionCharts } from "@/components/EmotionCharts/EmotionCharts";
import { uploadImage } from "@/api/client";
import { getImageUrl } from "@/api/config";
import { useLogs } from "@/hooks/useLogs";
import { useMetrics, type Metrics } from "@/hooks/useMetrics";
import { useTableState } from "@/hooks/useTableState";
import { useBackendHealth } from "@/hooks/useBackendHealth";
import { CONSTANTS } from "@/constants";
import { MOCK_LOGS, MOCK_METRICS, getMockImageUrl } from "@/utils/mockData";
import { TableSkeleton, StatsSkeleton } from "@/components/LoadingSkeleton/LoadingSkeleton";
import { EmptyState } from "@/components/EmptyState/EmptyState";
import { ErrorState } from "@/components/ErrorState/ErrorState";
import { exportToCSV, exportToJSON } from "@/utils/export";

type TableRow = {
  image: string;
  imageUrl?: string;
  emotions?: string;
  timestamp?: number | string;
  reviews: { positive: number; negative: number };
};

export function HomePage() {
  // Check backend health to determine if we should use mock data
  const backendHealth = useBackendHealth();
  const realLogs = useLogs(CONSTANTS.DEFAULT_LOG_LIMIT);
  const realMetrics = useMetrics();
  
  // Use mock data if backend is offline OR if forced via env var
  const useMockData = CONSTANTS.FORCE_MOCK_DATA || !backendHealth.isOnline;
  
  // Use mock data if backend is offline, otherwise use real data
  const logs = useMockData ? MOCK_LOGS : realLogs.logs;
  const loadingLogs = useMockData ? false : realLogs.loading;
  const logsError = useMockData ? null : realLogs.error;
  const fetchLogs = useMockData ? () => Promise.resolve() : realLogs.fetchLogs;
  
  const metrics = useMockData ? MOCK_METRICS : realMetrics.metrics;
  const refreshMetrics = useMockData ? () => Promise.resolve() : realMetrics.refresh;

  const submitFile = useCallback(
    async (file: Blob | File, filename = "upload.jpg") => {
      try {
        const json = await uploadImage(file, filename);
        notifications.show({
          title: "Success",
          message: "Image uploaded and analyzed successfully",
          color: "teal",
        });
        return json;
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to upload image";
        notifications.show({
          title: "Upload Failed",
          message,
          color: "red",
        });
        throw err;
      } finally {
        // ALWAYS refresh logs & metrics after attempt (success OR failure)
        try {
          await fetchLogs(CONSTANTS.DEFAULT_LOG_LIMIT);
        } catch (err) {
          console.warn("Failed to refresh logs after submit:", err);
        }
        try {
          await refreshMetrics();
        } catch (err) {
          console.warn("Failed to refresh metrics after submit:", err);
        }
      }
    },
    [fetchLogs, refreshMetrics]
  );

  const clearLogs = useCallback(() => {
    // Note: This only clears local state. If you want to clear server data, add an API endpoint.
    notifications.show({
      title: "Logs Cleared",
      message: "Local logs cleared (server data unchanged)",
      color: "blue",
    });
  }, []);

  const tableRows: TableRow[] = useMemo(() => {
    return logs.map((l) => {
      const conf = typeof l.confidence === "number" ? Math.round((l.confidence ?? 0) * 100) : 0;
      const imageUrl = useMockData && l.filename
        ? getMockImageUrl(l.filename)
        : l.filename
        ? getImageUrl(l.filename)
        : undefined;
      return {
        image: l.filename ?? "upload",
        imageUrl,
        emotions: l.emotion ?? "-",
        timestamp: l.ts ?? "-",
        reviews: { positive: conf, negative: Math.max(0, 100 - conf) },
      };
    });
  }, [logs]);

  // Table state management (search, filter, pagination)
  const tableState = useTableState(tableRows, 10);

  // Export handlers
  const handleExportCSV = useCallback(() => {
    const exportData = tableState.filteredRows.map((row) => ({
      Filename: row.image,
      Emotion: row.emotions || "-",
      Timestamp: row.timestamp || "-",
      Confidence: `${row.reviews.positive}%`,
    }));
    exportToCSV(exportData, `emotion-detection-${new Date().toISOString().split("T")[0]}.csv`);
    notifications.show({
      title: "Export Successful",
      message: "Data exported to CSV",
      color: "teal",
    });
  }, [tableState.filteredRows]);

  const handleExportJSON = useCallback(() => {
    exportToJSON(tableState.filteredRows, `emotion-detection-${new Date().toISOString().split("T")[0]}.json`);
    notifications.show({
      title: "Export Successful",
      message: "Data exported to JSON",
      color: "teal",
    });
  }, [tableState.filteredRows]);

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
    <Box style={{ minHeight: "100vh", background: "var(--mantine-color-body)" }}>
      <Container size="xl" py={{ base: "md", sm: "xl" }} px={{ base: "sm", sm: "md" }}>
        {/* Header Section */}
        <Stack gap="md" mb={{ base: "lg", md: "xl" }} align="stretch">
          <Group gap="md" wrap="wrap" justify="space-between" align="center">
            <Group gap="md" wrap="wrap" style={{ flex: 1, minWidth: 0 }}>
              <Box
                style={{
                  width: 56,
                  height: 56,
                  borderRadius: 12,
                  overflow: "hidden",
                  boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                  flexShrink: 0,
                }}
              >
                <img
                  src={logo}
                  alt="Emotion Detection Logo"
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                />
              </Box>
              <Stack gap={4} style={{ minWidth: 0, flex: 1 }}>
                <Title 
                  order={1} 
                  fw={700} 
                  style={{ 
                    fontSize: "clamp(1.5rem, 4vw, 2.5rem)",
                    wordBreak: "break-word",
                    overflowWrap: "break-word",
                  }}
                >
                  Emotion Detection
                </Title>
                <Text 
                  size="md" 
                  c="dimmed" 
                  fw={500} 
                  visibleFrom="sm"
                  style={{ wordBreak: "break-word" }}
                >
                  AI-powered emotion analysis from images
                </Text>
                <Text 
                  size="sm" 
                  c="dimmed" 
                  fw={500} 
                  hiddenFrom="sm"
                  style={{ wordBreak: "break-word" }}
                >
                  AI-powered emotion analysis
                </Text>
              </Stack>
            </Group>
            {/* Backend Status Indicator */}
            <Group gap="xs" wrap="wrap" justify="flex-end">
              {backendHealth.status === "checking" && (
                <Badge
                  color="gray"
                  variant="light"
                  size="lg"
                  leftSection={<IconLoader size={14} style={{ animation: "spin 1s linear infinite" }} />}
                >
                  <Text span size="sm" style={{ whiteSpace: "nowrap" }}>
                    Checking...
                  </Text>
                </Badge>
              )}
              {backendHealth.status === "online" && (
                <Badge
                  color="green"
                  variant="light"
                  size="lg"
                  leftSection={<IconWifi size={14} />}
                >
                  <Text span size="sm" style={{ whiteSpace: "nowrap" }}>
                    <Text span visibleFrom="xs">Backend </Text>Online
                  </Text>
                </Badge>
              )}
              {backendHealth.status === "offline" && (
                <Tooltip
                  label={backendHealth.error?.message || "Backend is offline. Using mock data."}
                  withArrow
                >
                  <Badge
                    color="orange"
                    variant="light"
                    size="lg"
                    leftSection={<IconWifiOff size={14} />}
                  >
                    <Text span size="sm" style={{ whiteSpace: "nowrap" }}>
                      <Text span hiddenFrom="sm">Offline</Text>
                      <Text span visibleFrom="sm">Backend Offline</Text>
                    </Text>
                  </Badge>
                </Tooltip>
              )}
            </Group>
          </Group>
        </Stack>

        {/* Main Content - Responsive Grid */}
        <Grid gutter={{ base: "md", sm: "lg" }}>
          {/* Camera Section - Full width on mobile, 2/3 on tablet+, 1/2 on large screens */}
          <Grid.Col span={{ base: 12, md: 8, lg: 7 }}>
            <Paper withBorder p={{ base: "md", sm: "lg" }} radius="md" shadow="sm" style={{ height: "100%" }}>
              <CameraSpace
                submitFile={submitFile}
                onRefreshLogs={() => fetchLogs(CONSTANTS.REFRESH_LOG_LIMIT)}
                onClearLogs={() => clearLogs()}
              />
              <Divider my="md" />
              <Group justify="space-between" wrap="wrap">
                <Text size="sm" c="dimmed">
                  {logsError ? (
                    <Text span c="red" fw={500}>
                      Error: {logsError}
                    </Text>
                  ) : loadingLogs ? (
                    "Loading logs..."
                  ) : (
                    `${logs.length} ${logs.length === 1 ? "prediction" : "predictions"}`
                  )}
                </Text>
              </Group>
            </Paper>
          </Grid.Col>

          {/* Stats Section - Full width on mobile, 1/3 on tablet+, 1/2 on large screens */}
          <Grid.Col span={{ base: 12, md: 4, lg: 5 }}>
            <Stack gap="md">
              <Paper withBorder p={{ base: "md", sm: "lg" }} radius="md" shadow="sm">
                <Group justify="space-between" mb="md">
                  <Title order={4}>Statistics</Title>
                  <Tooltip label="Refresh metrics" withArrow>
                    <ActionIcon
                      variant="subtle"
                      onClick={() => refreshMetrics()}
                      loading={realMetrics.loading}
                    >
                      <IconRefresh size={18} />
                    </ActionIcon>
                  </Tooltip>
                </Group>
                {realMetrics.loading && !useMockData ? (
                  <StatsSkeleton />
                ) : (
                  <StatsGrid items={statsItems} />
                )}
              </Paper>
              <Paper withBorder p={{ base: "md", sm: "lg" }} radius="md" shadow="sm">
                <StatsRingCard
                  total={metrics?.total ?? logs.length}
                  completed={metrics?.by_label?.happy ?? 0}
                  breakdown={ringBreakdown}
                />
              </Paper>
            </Stack>
          </Grid.Col>

          {/* Charts Section */}
          {tableRows.length > 0 && (
            <Grid.Col span={12}>
              <EmotionCharts data={tableRows} />
            </Grid.Col>
          )}

          {/* Table Section - Full width always */}
          <Grid.Col span={12}>
            <Paper withBorder p={{ base: "md", sm: "lg" }} radius="md" shadow="sm">
              <Group justify="space-between" mb="md" wrap="wrap">
                <Title order={3}>Recent Predictions</Title>
                <Group gap="xs">
                  <Tooltip label="Refresh logs" withArrow>
                    <ActionIcon
                      variant="subtle"
                      onClick={() => fetchLogs(CONSTANTS.DEFAULT_LOG_LIMIT)}
                      loading={loadingLogs}
                    >
                      <IconRefresh size={18} />
                    </ActionIcon>
                  </Tooltip>
                </Group>
              </Group>

              {loadingLogs ? (
                <TableSkeleton rows={5} />
              ) : logsError ? (
                <ErrorState
                  title="Failed to load predictions"
                  message={logsError}
                  onRetry={() => fetchLogs(CONSTANTS.DEFAULT_LOG_LIMIT)}
                />
              ) : (
                <Stack gap="md">
                  <TableControls
                    searchValue={tableState.filters.search}
                    onSearchChange={tableState.updateSearch}
                    emotionFilter={tableState.filters.emotions}
                    onEmotionFilterChange={tableState.updateEmotionFilter}
                    confidenceRange={tableState.filters.confidenceRange}
                    onConfidenceRangeChange={tableState.updateConfidenceRange}
                    dateFrom={tableState.filters.dateFrom}
                    dateTo={tableState.filters.dateTo}
                    onDateFromChange={tableState.updateDateFrom}
                    onDateToChange={tableState.updateDateTo}
                    onExportCSV={handleExportCSV}
                    onExportJSON={handleExportJSON}
                    availableEmotions={tableState.availableEmotions}
                    totalResults={tableState.allRows.length}
                    filteredResults={tableState.filteredRows.length}
                  />

                  <TableReviews rows={tableState.paginatedRows} />

                  {tableState.totalPages > 1 && (
                    <Group justify="space-between" wrap="wrap">
                      <Group gap="xs" align="center">
                        <Text size="sm" c="dimmed">
                          Rows per page:
                        </Text>
                        <Select
                          value={String(tableState.pageSize)}
                          onChange={(value) => tableState.setPageSize(Number(value))}
                          data={["5", "10", "20", "50", "100"]}
                          style={{ width: 80 }}
                        />
                      </Group>
                      <Pagination
                        value={tableState.currentPage}
                        onChange={tableState.setCurrentPage}
                        total={tableState.totalPages}
                        size="sm"
                      />
                    </Group>
                  )}
                </Stack>
              )}
            </Paper>
          </Grid.Col>
        </Grid>

        <Box mt="xl" style={{ position: "fixed", bottom: 20, right: 20, zIndex: 1000 }}>
          <ActionToggle />
        </Box>
      </Container>
    </Box>
  );
}