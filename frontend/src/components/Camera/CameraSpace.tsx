import React, { useRef, useState, useEffect } from "react";
import { Button, Group, Card, Text, Box, Title, Stack, Badge, Image, Select } from "@mantine/core";
import { IconCamera, IconUpload, IconVideo, IconVideoOff } from "@tabler/icons-react";
import { ButtonProgress, Status } from "@/components/Buttons/ButtonProgress";
import { ButtonMenu } from "@/components/Buttons/ButtonMenu";
import { CONSTANTS } from "@/constants";

type Props = {
  submitFile: (file: Blob, filename?: string, model?: "base" | "fine-tuned") => Promise<any>;
  onRefreshLogs?: () => void;
  onClearLogs?: () => void;
  disabled?: boolean; // Disable uploads when backend is offline
};

export function CameraSpace({ submitFile, onRefreshLogs, onClearLogs, disabled = false }: Props) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const [streaming, setStreaming] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<Status>("idle");
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);
  const [previewImageUrl, setPreviewImageUrl] = useState<string | null>(null); // Image preview during prediction
  const previewImageUrlRef = useRef<string | null>(null); // Ref to track current preview URL for cleanup
  const [selectedModel, setSelectedModel] = useState<"base" | "fine-tuned">("base");

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

  // Cleanup: Revoke object URLs when component unmounts
  useEffect(() => {
    return () => {
      if (previewImageUrlRef.current) {
        URL.revokeObjectURL(previewImageUrlRef.current);
        previewImageUrlRef.current = null;
      }
    };
  }, []);

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
      
      // Show captured image in preview
      const imageUrl = URL.createObjectURL(blob);
      setPreviewImageUrl(imageUrl);
      previewImageUrlRef.current = imageUrl;
      
      // Stop camera stream to show the captured image
      stopCamera();
      
      setProgress(20);
      await submitAndTrack(blob, "capture.jpg");
    } catch (err) {
      console.error(err);
      setStatus("error");
      setProgress(0);
      // Clear preview on error
      const currentUrl = previewImageUrlRef.current;
      if (currentUrl) {
        URL.revokeObjectURL(currentUrl);
        previewImageUrlRef.current = null;
        setPreviewImageUrl(null);
      }
      setTimeout(() => setStatus("idle"), 2000);
    }
  }

  async function handleUploadFile(file: File | null) {
    if (!file) {return};
    setSelectedFileName(file.name);
    setStatus("loading");
    setProgress(5);
    
    // Show uploaded image in preview
    const imageUrl = URL.createObjectURL(file);
    setPreviewImageUrl(imageUrl);
    previewImageUrlRef.current = imageUrl;
    
    // Stop camera stream if active to show the uploaded image
    if (streaming) {
      stopCamera();
    }
    
    try {
      await submitAndTrack(file, file.name);
    } catch (err) {
      console.error(err);
      setStatus("error");
      setProgress(0);
      setSelectedFileName(null); // Clear filename on error
      // Clear preview on error
      const currentUrl = previewImageUrlRef.current;
      if (currentUrl) {
        URL.revokeObjectURL(currentUrl);
        previewImageUrlRef.current = null;
        setPreviewImageUrl(null);
      }
      setTimeout(() => setStatus("idle"), 2000);
    } finally {
      // clear file input so same file can be re-selected
      if (fileInputRef.current) {fileInputRef.current.value = ""};
    }
  }

  async function submitAndTrack(file: Blob, filename = "upload.jpg") {
    try {
      setProgress(10);
      // Simulate progress during upload (Render can be slow on free tier)
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev < 80) return prev + 5; // Gradually increase to 80%
          return prev;
        });
      }, 500); // Update every 500ms
      
      await submitFile(file, filename, selectedModel);
      clearInterval(progressInterval);
      setProgress(90);
      await new Promise((r) => setTimeout(r, 200));
      setProgress(100);
      setStatus("success");
      onRefreshLogs && (await onRefreshLogs());
      
      // Clear preview image after successful prediction (with a short delay to show success)
      setTimeout(() => {
        const currentUrl = previewImageUrlRef.current;
        if (currentUrl) {
          URL.revokeObjectURL(currentUrl);
          previewImageUrlRef.current = null;
          setPreviewImageUrl(null);
        }
        setSelectedFileName(null);
      }, 1500); // Show success for 1.5 seconds, then clear
      
      setTimeout(() => {
        setProgress(0);
        setStatus("idle");
      }, 1200);
    } catch (err) {
      setStatus("error");
      setProgress(0);
      setSelectedFileName(null); // Clear filename on error to stop "loading silently"
      // Clear preview on error
      const currentUrl = previewImageUrlRef.current;
      if (currentUrl) {
        URL.revokeObjectURL(currentUrl);
        previewImageUrlRef.current = null;
        setPreviewImageUrl(null);
      }
      throw err; // Re-throw so handleUploadFile can catch it
    }
  }

  return (
    <Stack gap="md">
      <Group justify="space-between" align="center" wrap="wrap">
        <Title order={4}>
          Camera & Upload
        </Title>
        <Group gap="md" align="center">
          <Select
            label="Model"
            placeholder="Select model"
            value={selectedModel}
            onChange={(value) => setSelectedModel((value as "base" | "fine-tuned") || "base")}
            data={[
              { value: "base", label: "Base Model" },
              { value: "fine-tuned", label: "Asripa" },
            ]}
            size="sm"
            style={{ minWidth: 200 }}
            disabled={disabled || status === "loading"}
          />
          {streaming && (
            <Badge color="green" variant="light" leftSection={<IconVideo size={12} />} size="lg">
              Live
            </Badge>
          )}
        </Group>
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
            boxShadow: streaming ? "0 0 20px rgba(34, 139, 34, 0.3)" : previewImageUrl ? "0 0 20px rgba(59, 130, 246, 0.3)" : "0 2px 8px rgba(0,0,0,0.1)",
            transition: "box-shadow 0.3s ease",
          }}
        >
          {/* Show preview image if available (during prediction) */}
          {previewImageUrl && (
            <Image
              src={previewImageUrl}
              alt="Preview"
              style={{
                width: "100%",
                height: "100%",
                objectFit: "contain",
              }}
            />
          )}
          
          {/* Show video stream if no preview image and streaming */}
          <video
            ref={videoRef}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              display: streaming && !previewImageUrl ? "block" : "none",
            }}
            muted
          />
          <canvas ref={canvasRef} style={{ display: "none" }} />
          
          {/* Show placeholder if no preview, no video, and not loading */}
          {!streaming && !previewImageUrl && status === "idle" && (
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
          
          {/* Show loading overlay during prediction with progress */}
          {previewImageUrl && status === "loading" && (
            <Box
              style={{
                position: "absolute",
                inset: 0,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                background: "rgba(0, 0, 0, 0.8)",
                backdropFilter: "blur(2px)",
                gap: "1rem",
                zIndex: 10,
              }}
            >
              <Text size="lg" fw={600} c="white">
                Analyzing emotion...
              </Text>
              <Box style={{ width: "80%", maxWidth: "300px" }}>
                <Box
                  style={{
                    width: "100%",
                    height: "8px",
                    backgroundColor: "rgba(255, 255, 255, 0.2)",
                    borderRadius: "4px",
                    overflow: "hidden",
                  }}
                >
                  <Box
                    style={{
                      width: `${progress}%`,
                      height: "100%",
                      backgroundColor: "#4dabf7",
                      transition: "width 0.3s ease",
                    }}
                  />
                </Box>
                <Text c="white" size="sm" ta="center" mt="xs">
                  {progress < 30 ? "Uploading image..." : progress < 80 ? "Processing..." : "Almost done..."}
                </Text>
              </Box>
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
            disabled={!streaming || disabled}
            title={disabled ? "Backend is offline. Uploads are disabled." : undefined}
          />
          <Box>
            <input
              ref={fileInputRef}
              style={{ display: "none" }}
              type="file"
              accept="image/*"
              disabled={disabled}
              onChange={(e) => {
                if (!disabled) {
                  const f = e.target.files?.[0] ?? null;
                  void handleUploadFile(f);
                }
              }}
            />
            <ButtonProgress
              progress={progress}
              status={status}
              label="Upload image"
              loadingLabel="Uploading…"
              onClick={() => fileInputRef.current?.click()}
              disabled={disabled}
              title={disabled ? "Backend is offline. Uploads are disabled." : undefined}
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