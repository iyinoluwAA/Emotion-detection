import React from "react";
import { Box, Text, Stack } from "@mantine/core";
import { IconInbox } from "@tabler/icons-react";

type Props = {
  title?: string;
  message?: string;
  icon?: React.ReactNode;
};

export function EmptyState({ 
  title = "No data available", 
  message = "There are no predictions to display yet.",
  icon,
}: Props) {
  return (
    <Box
      style={{
        padding: "3rem 1rem",
        textAlign: "center",
        color: "var(--mantine-color-dimmed)",
      }}
    >
      <Stack align="center" gap="md">
        {icon || <IconInbox size={64} stroke={1.5} style={{ opacity: 0.5 }} />}
        <Stack gap={4} align="center">
          <Text fw={600} size="lg">
            {title}
          </Text>
          <Text size="sm" c="dimmed" maw={400}>
            {message}
          </Text>
        </Stack>
      </Stack>
    </Box>
  );
}

