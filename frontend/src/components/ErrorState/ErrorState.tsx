import React from "react";
import { Box, Text, Stack, Button } from "@mantine/core";
import { IconAlertCircle } from "@tabler/icons-react";

type Props = {
  title?: string;
  message?: string;
  onRetry?: () => void;
  retryLabel?: string;
};

export function ErrorState({
  title = "Something went wrong",
  message = "An error occurred while loading data.",
  onRetry,
  retryLabel = "Try again",
}: Props) {
  return (
    <Box
      style={{
        padding: "2rem 1rem",
        textAlign: "center",
      }}
    >
      <Stack align="center" gap="md">
        <IconAlertCircle size={48} color="var(--mantine-color-red-6)" />
        <Stack gap={4} align="center">
          <Text fw={600} size="lg" c="red">
            {title}
          </Text>
          <Text size="sm" c="dimmed" maw={400}>
            {message}
          </Text>
        </Stack>
        {onRetry && (
          <Button variant="light" color="red" onClick={onRetry} mt="sm">
            {retryLabel}
          </Button>
        )}
      </Stack>
    </Box>
  );
}

