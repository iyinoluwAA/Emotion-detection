import React, { useRef, useState } from "react";
import { Button, Group, Card, Text, Stack } from "@mantine/core";
import { ButtonProgress, Status } from "@/components/Buttons/ButtonProgress";
import { ButtonMenu } from "@/components/Buttons/ButtonMenu";
import { showNotification } from "@mantine/notifications";

type Props = {
  submitFile: (file: Blob, filename?: string) => Promise<any>;
  onRefreshLogs?: () => void;
  onClearLogs?: () => void;
};

export function CameraSpace({ submitFile, onRefreshLogs, onClearLogs }: Props) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

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
      // Prefer notifications – if you use Mantine notifications provider
      try {
        showNotification({ title: "Camera", message: "Unable to access camera. Check permissions.", color: "red" });
      } catch {
        // fallback
    }
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

  // Animate progress smoothly from current value down to 0
  function animateToZero(duration = 600) {
    const start = performance.now();
    const from = progress > 0 ? progress : 100;
    function frame(now: number) {
      const t = Math.min(1, (now - start) / duration);
      const val = Math.round(from * (1 - t));
      setProgress(val);
      if (t < 1) {
        requestAnimationFrame(frame);
      } else {
        setProgress(0);
      }
    }
    requestAnimationFrame(frame);
  }

  async function submitAndTrack(file: Blob, filename = "upload.jpg") {
    // optimistic progress simulation (since upload/predict can be fast)
    try {
      setStatus("loading");
      setProgress(5);

      // send file to parent (which will refresh logs/metrics in finally)
      await submitFile(file, filename);

      // gradually animate to success
      setProgress(60);
      await new Promise((r) => setTimeout(r, 250)); // small pause
      setProgress(100);
      setStatus("success");

      // refresh logs/metrics (parent may already do this; keep safe)
      if (onRefreshLogs) {
        try {
          await onRefreshLogs();
        } catch (err) {
          console.warn("onRefreshLogs failed", err);
        }
      }

      // keep success visible briefly, then animate back to zero
      await new Promise((r) => setTimeout(r, 600));
      animateToZero(600);
      setTimeout(() => setStatus("idle"), 900);
      // clear selected filename after 5s
      setTimeout(() => setSelectedFileName(null), 5000);
    } catch (err) {
      console.error("submitAndTrack error:", err);
      // show visual failure: fill to 100 (red), then animate back to zero and show error
      setProgress(100);
      setStatus("error");
      try {
        showNotification({ title: "Prediction failed", message: String(err), color: "red" });
      } catch {
        // fallback
        console.warn("notification failed");
      }
      // wait a bit then animate to zero and reset status to idle
      await new Promise((r) => setTimeout(r, 900));
      animateToZero(700);
      setTimeout(() => setStatus("idle"), 900);
      // still rethrow so parent code may handle if needed
      throw err;
    }
  }

  async function handleCapture() {
    try {
      setStatus("loading");
      setProgress(5);
      const blob = await captureFrameBlob();
      if (!blob) {throw new Error("No capture available");}
      setProgress(20);
      await submitAndTrack(blob, "capture.jpg");
    } catch (err) {
      console.error(err);
      // errors already handled inside submitAndTrack
    }
  }

  async function handleUploadFile(file: File | null) {
    if (!file) {return};
    try {
      setStatus("loading");
      setProgress(5);
      setSelectedFileName(file.name);
      await submitAndTrack(file, file.name);
    } catch (err) {
      console.error(err);
      // handled above
    }
  }

  return (
    <Card withBorder p="md" radius="md">
      <div style={{ display: "flex", gap: 12, alignItems: "flex-start", flexWrap: "wrap" }}>
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
            <label>
              <input
                style={{ display: "none" }}
                type="file"
                accept="image/*"
                onChange={(e) => {
                  const f = e.target.files?.[0] ?? null;
                  if (f) {
                    setSelectedFileName(f.name);
                    void handleUploadFile(f);
                  }
                }}
              />
              <ButtonProgress
                progress={progress}
                status={status}
                label="Upload image"
                loadingLabel="Uploading…"
                onClick={() => document.querySelector<HTMLInputElement>('input[type="file"]')?.click()}
              />
            </label>
          </Group>

          {selectedFileName && <Text size="sm" mt="xs">Selected: {selectedFileName}</Text>}
        </div>

        <div style={{ width: 160 }}>
          <ButtonMenu onStartCamera={startCamera} onRefreshLogs={onRefreshLogs} onClearLogs={onClearLogs} />
          <Stack gap="md" mt="md">
            <Button variant="default" onClick={streaming ? stopCamera : startCamera}>
              {streaming ? "Stop camera" : "Start camera"}
            </Button>
          </Stack>
        </div>
      </div>
    </Card>
  );
}