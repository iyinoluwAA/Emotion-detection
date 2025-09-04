import React from "react";
import { IconChevronDown, IconRefresh, IconTrash, IconCamera } from "@tabler/icons-react";
import { Button, Menu, Text, useMantineTheme } from "@mantine/core";

type Props = {
  onStartCamera?: () => void;
  onRefreshLogs?: () => void;
  onClearLogs?: () => void;
};

export function ButtonMenu({ onStartCamera, onRefreshLogs, onClearLogs }: Props) {
  const theme = useMantineTheme();
  return (
    <Menu
      transitionProps={{ transition: "pop-top-right" }}
      position="top-end"
      width={220}
      withinPortal
      radius="md"
    >
      <Menu.Target>
        <Button rightSection={<IconChevronDown size={18} stroke={1.5} />} pr={12} radius="md">
          Actions
        </Button>
      </Menu.Target>
      <Menu.Dropdown>
        <Menu.Item
          leftSection={<IconCamera size={16} color={theme.colors.blue[6]} stroke={1.5} />}
          onClick={() => onStartCamera && onStartCamera()}
        >
          Start camera
        </Menu.Item>

        <Menu.Item
          leftSection={<IconRefresh size={16} color={theme.colors.teal[6]} stroke={1.5} />}
          onClick={() => onRefreshLogs && onRefreshLogs()}
        >
          Refresh logs
        </Menu.Item>

        <Menu.Item
          color="red"
          leftSection={<IconTrash size={16} color={theme.colors.red[6]} stroke={1.5} />}
          onClick={() => onClearLogs && onClearLogs()}
        >
          Clear logs
        </Menu.Item>

        <Menu.Divider />

        <Text size="xs" color="dimmed" style={{ padding: 8 }}>
          Shortcuts listed on items (if configured)
        </Text>
      </Menu.Dropdown>
    </Menu>
  );
}