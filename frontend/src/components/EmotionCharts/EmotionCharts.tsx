import React, { useMemo } from "react";
import { Paper, Title, Stack, Tabs, Text, Box } from "@mantine/core";
import { PieChart, BarChart, LineChart } from "@mantine/charts";
import { IconChartPie, IconChartBar, IconChartLine } from "@tabler/icons-react";
import { getEmotionColor } from "@/utils/emotionColors";

type EmotionData = {
  emotion: string;
  count: number;
};

type Props = {
  data: Array<{
    emotions?: string;
    timestamp?: string | number;
    reviews: { positive: number };
  }>;
};

export function EmotionCharts({ data }: Props) {
  // Process data for charts
  const emotionDistribution = useMemo(() => {
    const emotionMap = new Map<string, number>();
    
    data.forEach((item) => {
      if (item.emotions) {
        emotionMap.set(item.emotions, (emotionMap.get(item.emotions) || 0) + 1);
      }
    });

    return Array.from(emotionMap.entries())
      .map(([emotion, count]) => ({
        name: emotion,
        value: count,
        color: getEmotionColor(emotion),
      }))
      .sort((a, b) => b.value - a.value);
  }, [data]);

  const timeSeriesData = useMemo(() => {
    // Group by date and count emotions per day
    const dateMap = new Map<string, Record<string, number>>();
    
    data.forEach((item) => {
      if (!item.timestamp || !item.emotions) return;
      
      const date = new Date(item.timestamp);
      const dateKey = date.toISOString().split("T")[0];
      
      if (!dateMap.has(dateKey)) {
        dateMap.set(dateKey, {});
      }
      
      const dayData = dateMap.get(dateKey)!;
      dayData[item.emotions] = (dayData[item.emotions] || 0) + 1;
    });

    return Array.from(dateMap.entries())
      .map(([date, emotions]) => ({
        date,
        ...emotions,
      }))
      .sort((a, b) => a.date.localeCompare(b.date))
      .slice(-7); // Last 7 days
  }, [data]);

  const confidenceDistribution = useMemo(() => {
    const ranges = [
      { range: "0-20%", min: 0, max: 20, count: 0 },
      { range: "21-40%", min: 21, max: 40, count: 0 },
      { range: "41-60%", min: 41, max: 60, count: 0 },
      { range: "61-80%", min: 61, max: 80, count: 0 },
      { range: "81-100%", min: 81, max: 100, count: 0 },
    ];

    data.forEach((item) => {
      const confidence = item.reviews.positive;
      ranges.forEach((range) => {
        if (confidence >= range.min && confidence <= range.max) {
          range.count++;
        }
      });
    });

    return ranges;
  }, [data]);

  if (emotionDistribution.length === 0) {
    return null;
  }

  return (
    <Paper withBorder p="lg" radius="md" shadow="sm">
      <Title order={4} mb="md">
        Analytics & Visualizations
      </Title>
      
      <Tabs defaultValue="distribution">
        <Tabs.List>
          <Tabs.Tab value="distribution" leftSection={<IconChartPie size={16} />}>
            Distribution
          </Tabs.Tab>
          <Tabs.Tab value="trends" leftSection={<IconChartLine size={16} />}>
            Trends
          </Tabs.Tab>
          <Tabs.Tab value="confidence" leftSection={<IconChartBar size={16} />}>
            Confidence
          </Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="distribution" pt="md">
          <Box style={{ width: "100%", height: 400, minHeight: 400 }}>
            <PieChart
              data={emotionDistribution}
              withTooltip
              withLabels
              size={300}
              labelsPosition="outside"
              labelsType="percent"
            />
          </Box>
        </Tabs.Panel>

        <Tabs.Panel value="trends" pt="md">
          {timeSeriesData.length > 0 ? (
            <Box style={{ width: "100%", height: 400, minHeight: 400 }}>
              <LineChart
                h={300}
                w="100%"
                data={timeSeriesData}
                dataKey="date"
                series={emotionDistribution.slice(0, 5).map((item) => ({
                  name: item.name,
                  color: item.color,
                }))}
                curveType="natural"
                withTooltip
                withDots
              />
            </Box>
          ) : (
            <Stack align="center" gap="md" py="xl">
              <Text c="dimmed">Not enough time series data to display trends</Text>
            </Stack>
          )}
        </Tabs.Panel>

        <Tabs.Panel value="confidence" pt="md">
          <Box style={{ width: "100%", height: 400, minHeight: 400 }}>
            <BarChart
              h={300}
              w="100%"
              data={confidenceDistribution}
              dataKey="range"
              series={[{ name: "count", color: "blue" }]}
              withTooltip
              tickLine="y"
            />
          </Box>
        </Tabs.Panel>
      </Tabs>
    </Paper>
  );
}

