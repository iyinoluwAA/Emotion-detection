// components/StatsGrid/StatsGrid.tsx
import { Group, Paper, SimpleGrid, Text } from '@mantine/core';
import classes from './StatsGrid.module.css';

type Item = { title: string; value: string; diff?: number };

export function StatsGrid({ items = [] as Item[] }: { items?: Item[] }) {
  const stats = items.map((stat) => {
    return (
      <Paper withBorder p="md" radius="md" key={stat.title}>
        <Group justify="space-between">
          <Text size="xs" c="dimmed" className={classes.title}>{stat.title}</Text>
        </Group>

        <Group align="flex-end" gap="xs" mt={25}>
          <Text className={classes.value}>{stat.value}</Text>
          {typeof stat.diff !== "undefined" && (
            <Text c={stat.diff > 0 ? 'teal' : 'red'} fz="sm" fw={500} className={classes.diff}>
              <span>{stat.diff}%</span>
            </Text>
          )}
        </Group>

        <Text fz="xs" c="dimmed" mt={7}>Compared to previous month</Text>
      </Paper>
    );
  });
  return (
    <div className={classes.root}>
      <SimpleGrid cols={{ base: 1, xs: 2, md: 4 }}>{stats}</SimpleGrid>
    </div>
  );
}
