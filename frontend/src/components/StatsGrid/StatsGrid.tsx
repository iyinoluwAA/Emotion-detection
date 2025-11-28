// components/StatsGrid/StatsGrid.tsx
import { Group, Paper, SimpleGrid, Text } from '@mantine/core';
import classes from './StatsGrid.module.css';

type Item = { title: string; value: string; diff?: number };

export function StatsGrid({ items = [] as Item[] }: { items?: Item[] }) {
  const stats = items.map((stat) => {
    return (
      <Paper withBorder p="md" radius="md" key={stat.title} style={{ minWidth: 0, overflow: "hidden" }}>
        <Group justify="space-between" wrap="nowrap" gap="xs">
          <Text 
            size="xs" 
            c="dimmed" 
            className={classes.title}
            style={{ 
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
              flex: 1,
              minWidth: 0,
            }}
          >
            {stat.title}
          </Text>
        </Group>

        <Group align="flex-end" gap="xs" mt={25} wrap="nowrap">
          <Text 
            className={classes.value}
            style={{ 
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
              minWidth: 0,
            }}
          >
            {stat.value}
          </Text>
          {typeof stat.diff !== "undefined" && (
            <Text 
              c={stat.diff > 0 ? 'teal' : 'red'} 
              fz="sm" 
              fw={500} 
              className={classes.diff}
              style={{ whiteSpace: "nowrap", flexShrink: 0 }}
            >
              <span>{stat.diff > 0 ? '+' : ''}{stat.diff}%</span>
            </Text>
          )}
        </Group>

        <Text 
          fz="xs" 
          c="dimmed" 
          mt={7}
          style={{ 
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}
        >
          Compared to previous month
        </Text>
      </Paper>
    );
  });
  return (
    <div className={classes.root}>
      <SimpleGrid cols={{ base: 1, xs: 2, md: 4 }} spacing={{ base: "sm", md: "md" }}>
        {stats}
      </SimpleGrid>
    </div>
  );
}
