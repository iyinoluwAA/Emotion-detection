import React from "react";
import { Button, Progress, } from "@mantine/core";
import classes from "./ButtonProgress.module.css";

export type Status = "idle" | "loading" | "success" | "error";

type Props = {
  progress: number; // 0 - 100
  status?: Status;
  label?: string;
  loadingLabel?: string;
  successLabel?: string;
  errorLabel?: string;
  onClick?: () => void;
  radius?: "sm" | "md" | "lg";
  minWidth?: number;
  disabled?: boolean;
  title?: string;
};

export function ButtonProgress({
  progress,
  status = "idle",
  label = "Upload",
  loadingLabel = "Uploading…",
  successLabel = "Done",
  errorLabel = "Failed",
  onClick,
  radius = "sm",
  minWidth = 160,
  disabled = false,
  title,
}: Props) {
  // const theme = useMantineTheme();
  const isLoading = status === "loading";
  const isSuccess = status === "success";
  const isError = status === "error";

  const bgColor = isSuccess ? "teal" : isError ? "red" : undefined;

  return (
    <Button
      style={{ minWidth }}
      className={classes.button}
      onClick={onClick}
      color={bgColor as any}
      radius={radius}
      disabled={isLoading || disabled}
      title={title}
    >
      <div className={classes.label}>
        {isLoading ? loadingLabel : isSuccess ? successLabel : isError ? errorLabel : label}
      </div>

      {isLoading && progress > 0 && (
        <Progress
          value={progress}
          className={classes.progress}
          radius="sm"
          style={{ position: "absolute", left: 0, right: 0, bottom: 0, top: 0, zIndex: 0 }}
        />
      )}
    </Button>
  );
}