import React from "react";
import { ActionIcon, Group, useMantineColorScheme, useComputedColorScheme } from "@mantine/core";
import { IconMoon, IconSun } from "@tabler/icons-react";
import cx from "clsx";
import styles from "./ActionToggle.module.css";

/**
 * ActionToggle visual matches what you had: both icons are present and
 * CSS controls which one is visible depending on computed color scheme.
 *
 * Note: App must be wrapped with Mantine's ColorSchemeProvider (see App.tsx below).
 */
export function ActionToggle() {
  const { setColorScheme } = useMantineColorScheme();
  const computedColorScheme = useComputedColorScheme("light", { getInitialValueInEffect: true });

  const handleClick = () => {
    setColorScheme(computedColorScheme === "light" ? "dark" : "light");
  };

  return (
    <Group gap="md" justify="left">
      <ActionIcon
        onClick={handleClick}
        variant="default"
        size="xl"
        radius="md"
        aria-label="Toggle color scheme"
        data-scheme={computedColorScheme} /* used by CSS selectors */
        className={styles.wrapper}
      >
        {/* both icons present; CSS toggles opacity/display */}
        <IconSun className={cx(styles.icon, styles.light)} stroke={1.5} />
        <IconMoon className={cx(styles.icon, styles.dark)} stroke={1.5} />
      </ActionIcon>
    </Group>
  );
}
