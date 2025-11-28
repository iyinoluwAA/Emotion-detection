import React, { useRef, useState } from "react";
import { Button, Group, Card, Text, Box, Title, Stack, Badge } from "@mantine/core";
import { IconCamera, IconUpload, IconVideo, IconVideoOff } from "@tabler/icons-react";
import { ButtonProgress, Status } from "@/components/Buttons/ButtonProgress";
import { ButtonMenu } from "@/components/Buttons/ButtonMenu";
import { CONSTANTS } from "@/constants";

type Props = {
  submitFile: (file: Blob, filename?: string) => Promise<any>;
  onRefreshLogs?: () => void;
  onClearLogs?: () => void;
};

export function CameraSpace({ submitFile, onRefreshLogs, onClearLogs }: Props) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const [streaming, setStreaming] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<Status>("idle");
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);

  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: false });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        setStreaming(true);
      }
    } catch (e) {
      console.error("startCamera:", e);
      // don't use alert() in production; you can show Mantine notifications instead
    }
  }

  function stopCamera() {
    const v = videoRef.current;
    if (v && v.srcObject) {
      (v.srcObject as MediaStream).getTracks().forEach((t) => t.stop());
      v.srcObject = null;
    }
    setStreaming(false);
  }

  function captureFrameBlob(): Promise<Blob | null> {
    const video = videoRef.current;
    if (!video) {return Promise.resolve(null)};
    const canvas = canvasRef.current ?? document.createElement("canvas");
    const w = Math.min(480, video.videoWidth || 480);
    const h = Math.min(360, video.videoHeight || 360);
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    if (!ctx) {return Promise.resolve(null)};
    ctx.drawImage(video, 0, 0, w, h);
    return new Promise((resolve) => {
      canvas.toBlob((b) => resolve(b ?? null), "image/jpeg", 0.85);
    });
  }

  async function handleCapture() {
    setStatus("loading");
    setProgress(5);
    try {
      const blob = await captureFrameBlob();
      if (!blob) {throw new Error("No capture available")};
      setProgress(20);
      await submitAndTrack(blob, "capture.jpg");
    } catch (err) {
      console.error(err);
      setStatus("error");
      setProgress(0);
      setTimeout(() => setStatus("idle"), 2000);
    }
  }

  async function handleUploadFile(file: File | null) {
    if (!file) {return};
    setSelectedFileName(file.name);
    setStatus("loading");
    setProgress(5);
    try {
      await submitAndTrack(file, file.name);
    } catch (err) {
      console.error(err);
      setStatus("error");
      setProgress(0);
      setTimeout(() => setStatus("idle"), 2000);
    } finally {
      // clear file input so same file can be re-selected
      if (fileInputRef.current) {fileInputRef.current.value = ""};
    }
  }

  async function submitAndTrack(file: Blob, filename = "upload.jpg") {
    try {
      setProgress(20);
      await submitFile(file, filename);
      setProgress(60);
      await new Promise((r) => setTimeout(r, 300));
      setProgress(100);
      setStatus("success");
      onRefreshLogs && (await onRefreshLogs());
      setTimeout(() => setSelectedFileName(null), 5000);
      setTimeout(() => {
        setProgress(0);
        setStatus("idle");
      }, 1200);
    } catch (err) {
      setStatus("error");
      setProgress(0);
      throw err;
    }
  }

  return (
    <Stack gap="md">
      <Group justify="space-between" align="center" wrap="wrap">
        <Title order={4}>
          Camera & Upload
        </Title>
        {streaming && (
          <Badge color="green" variant="light" leftSection={<IconVideo size={12} />} size="lg">
            Live
          </Badge>
        )}
      </Group>

      {/* Responsive Layout: Stack on mobile, side-by-side on larger screens */}
      <Stack gap="md">
        {/* Camera Preview */}
        <Box
          style={{
            width: "100%",
            aspectRatio: "16/9",
            maxHeight: "400px",
            background: "var(--mantine-color-dark-8)",
            borderRadius: 12,
            overflow: "hidden",
            position: "relative",
            border: "2px solid var(--mantine-color-gray-3)",
            boxShadow: streaming ? "0 0 20px rgba(34, 139, 34, 0.3)" : "0 2px 8px rgba(0,0,0,0.1)",
            transition: "box-shadow 0.3s ease",
          }}
        >
          <video
            ref={videoRef}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              display: streaming ? "block" : "none",
            }}
            muted
          />
          <canvas ref={canvasRef} style={{ display: "none" }} />
          {!streaming && (
            <Box
              style={{
                position: "absolute",
                inset: 0,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                color: "var(--mantine-color-gray-5)",
                gap: 12,
              }}
            >
              <IconCamera size={48} stroke={1.5} />
              <Text size="sm" fw={500}>
                Camera inactive
              </Text>
              <Text size="xs" c="dimmed">
                Click "Start camera" to begin
              </Text>
            </Box>
          )}
        </Box>

        {/* Action Buttons - Responsive Grid */}
        <Group grow gap="md">
          <ButtonProgress
            progress={progress}
            status={status}
            label="Capture"
            loadingLabel="Capturing…"
            onClick={handleCapture}
          />
          <Box>
            <input
              ref={fileInputRef}
              style={{ display: "none" }}
              type="file"
              accept="image/*"
              onChange={(e) => {
                const f = e.target.files?.[0] ?? null;
                void handleUploadFile(f);
              }}
            />
            <ButtonProgress
              progress={progress}
              status={status}
              label="Upload image"
              loadingLabel="Uploading…"
              onClick={() => fileInputRef.current?.click()}
            />
          </Box>
        </Group>

        {selectedFileName && (
          <Group gap="xs">
            <IconUpload size={16} />
            <Text size="sm" c="dimmed" truncate>
              Selected: <Text span fw={500}>{selectedFileName}</Text>
            </Text>
          </Group>
        )}

        {/* Controls - Responsive: Stack on mobile, row on larger */}
        <Group gap="md" grow>
          <ButtonMenu onStartCamera={startCamera} onRefreshLogs={onRefreshLogs} onClearLogs={onClearLogs} />
          <Button
            variant={streaming ? "filled" : "default"}
            color={streaming ? "red" : "blue"}
            leftSection={streaming ? <IconVideoOff size={18} /> : <IconVideo size={18} />}
            onClick={streaming ? stopCamera : startCamera}
            fullWidth
          >
            {streaming ? "Stop camera" : "Start camera"}
          </Button>
        </Group>
      </Stack>
    </Stack>
  );
}