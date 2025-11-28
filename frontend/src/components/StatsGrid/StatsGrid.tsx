// components/StatsGrid/StatsGrid.tsx
import { Group, Paper, SimpleGrid, Text } from '@mantine/core';
import classes from './StatsGrid.module.css';

type Item = { title: string; value: string; diff?: number };

export function StatsGrid({ items = [] as Item[] }: { items?: Item[] }) {
  const stats = items.map((stat) => {
    return (
      <Paper 
        withBorder 
        p="md" 
        radius="md" 
        key={stat.title} 
        style={{ 
          minWidth: 0, 
          overflow: "hidden",
          wordWrap: "break-word",
          overflowWrap: "break-word",
        }}
      >
        <Text 
          size="xs" 
          c="dimmed" 
          className={classes.title}
          style={{ wordBreak: "break-word", overflowWrap: "break-word" }}
        >
          {stat.title}
        </Text>

        <Group align="flex-end" gap="xs" mt={25} wrap="nowrap">
          <Text className={classes.value} style={{ wordBreak: "break-word" }}>
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
          style={{ wordBreak: "break-word", overflowWrap: "break-word" }}
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
