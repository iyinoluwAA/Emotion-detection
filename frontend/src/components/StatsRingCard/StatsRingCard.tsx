// src/components/StatsRingCard/StatsRingCard.tsx
import React from "react";
import { Card, Group, RingProgress, Text, useMantineTheme } from "@mantine/core";
import classes from "./StatsRingCard.module.css";

type Breakdown = { label: string; count: number };

type Props = {
  total?: number;
  completed?: number;
  breakdown?: Breakdown[];
};

export function StatsRingCard({ total = 0, completed = 0, breakdown = [] }: Props) {
  const theme = useMantineTheme();
  const pct = total > 0 ? (completed / total) * 100 : 0;
  const topTwo = breakdown.slice(0, 2);

  return (
    <Card withBorder p="xl" radius="md" className={classes.card}>
      <div className={classes.inner}>
        <div>
          <Text fz="xl" className={classes.label}>
            Output
          </Text>

          <div>
            <Text className={classes.lead} mt={30}>
              {completed} completed {completed === 1 ? "task" : "tasks"}
            </Text>
            <Text fz="xs" c="dimmed">
              Completed
            </Text>
          </div>

          <Group mt="lg">
            {topTwo.map((s) => (
              <div key={s.label}>
                <Text className={classes.label}>{s.count}</Text>
                <Text size="xs" c="dimmed">
                  {s.label}
                </Text>
              </div>
            ))}
          </Group>
        </div>

        <div className={classes.ring}>
          <RingProgress
            roundCaps
            thickness={6}
            size={150}
            sections={[{ value: pct, color: theme.primaryColor }]}
            label={
              <div>
                <Text ta="center" fz="lg" className={classes.label}>
                  {Math.round(pct)}%
                </Text>
                <Text ta="center" fz="xs" c="dimmed">
                  Completed
                </Text>
              </div>
            }
          />
        </div>
      </div>
    </Card>
  );
}
