import React from "react";
import { Skeleton, Stack, Group, Box } from "@mantine/core";

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <Stack gap="md">
      {Array.from({ length: rows }).map((_, i) => (
        <Group key={i} gap="md" wrap="nowrap">
          <Skeleton height={80} width={80} radius="md" />
          <Skeleton height={16} width={140} />
          <Skeleton height={16} width={100} />
          <Skeleton height={16} width={80} />
          <Skeleton height={16} width={180} />
        </Group>
      ))}
    </Stack>
  );
}

export function StatsSkeleton() {
  return (
    <Group gap="md" grow>
      {Array.from({ length: 4 }).map((_, i) => (
        <Box key={i}>
          <Skeleton height={16} width={100} mb="xs" />
          <Skeleton height={32} width={60} />
        </Box>
      ))}
    </Group>
  );
}

