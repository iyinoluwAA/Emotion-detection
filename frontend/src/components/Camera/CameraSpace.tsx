import React, { useRef, useState } from "react";
import { Button, Group, Card, Text } from "@mantine/core";
import { ButtonProgress, Status } from "@/components/test/ButtonProgress";
import { ButtonMenu } from "@/components/test/ButtonMenu";

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
    <Card withBorder p="md" radius="md">
      <div style={{ display: "flex", gap: 20, alignItems: "flex-start", flexWrap: "wrap" }}>
        <div style={{ flex: "1 1 480px", minWidth: 280 }}>
          <div style={{ height: 440, background: "#111", borderRadius: 6, overflow: "hidden", position: "relative" }}>
            <video ref={videoRef} style={{ width: "100%", height: "100%", objectFit: "cover" }} muted />
            <canvas ref={canvasRef} style={{ display: "none" }} />
            {!streaming && (
              <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", color: "#fff" }}>
                <Text>Camera inactive</Text>
              </div>
            )}
          </div>

          <Group mt="md" grow>
            <ButtonProgress progress={progress} status={status} label="Capture" loadingLabel="Capturing…" onClick={handleCapture} />
            <div>
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
              <ButtonProgress progress={progress} status={status} label="Upload image" loadingLabel="Uploading…" onClick={() => fileInputRef.current?.click()} />
            </div>
          </Group>

          {selectedFileName && <Text size="sm" mt="xs">Selected: {selectedFileName}</Text>}
        </div>

        <div style={{ width: 180 }}>
          <ButtonMenu onStartCamera={startCamera} onRefreshLogs={onRefreshLogs} onClearLogs={onClearLogs} />
          <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 8 }}>
            <Button variant="default" onClick={streaming ? stopCamera : startCamera}>
              {streaming ? "Stop camera" : "Start camera"}
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );
}