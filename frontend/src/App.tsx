import React, { useEffect, useRef, useState } from "react";

type Prediction = {
  emotion: string;
  confidence: number;
};

type LogRecord = {
  id?: number;
  ts?: string;
  filename?: string;
  emotion?: string;
  confidence?: number;
};

const DEFAULT_API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

export default function App(): JSX.Element {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [streaming, setStreaming] = useState(false);
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<LogRecord[]>([]);
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);
  const [apiBase, setApiBase] = useState<string>(() => {
    return localStorage.getItem("VITE_API_URL") || DEFAULT_API_BASE;
  });
  const [backendInput, setBackendInput] = useState<string>(apiBase);

  useEffect(() => {
    // fetch recent logs on mount
    fetchLogs();
    // attempt to stop camera when unmounting
    return () => {
      stopCamera();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function fetchLogs(limit = 8) {
    try {
      const res = await fetch(`${apiBase}/logs?limit=${limit}`);
      if (!res.ok) throw new Error(`Status ${res.status}`);
      const json = await res.json();
      setLogs(json.logs || []);
    } catch (e) {
      // non-fatal
      console.warn("Failed fetching logs:", e);
    }
  }

  async function startCamera() {
    setError(null);
    try {
      // smaller constraints to reduce camera "pop up" size and CPU usage
      const constraints: MediaStreamConstraints = {
        video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" },
        audio: false,
      };
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        setStreaming(true);
      }
    } catch (e) {
      console.error(e);
      setError("Unable to access camera. Check permissions or use file upload.");
    }
  }

  function stopCamera() {
    setStreaming(false);
    const video = videoRef.current;
    if (video && video.srcObject) {
      const tracks = (video.srcObject as MediaStream).getTracks();
      tracks.forEach((t) => t.stop());
      video.srcObject = null;
    }
  }

  function captureFrame(): Blob | null {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return null;

    // smaller capture size for performance (scale down)
    const targetWidth = 320;
    const aspect = video.videoHeight / video.videoWidth || 0.75;
    const targetHeight = Math.round(targetWidth * aspect || 240);

    canvas.width = targetWidth;
    canvas.height = targetHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) return null;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const dataUrl = canvas.toDataURL("image/jpeg", 0.9);
    const binary = atob(dataUrl.split(",")[1]);
    const array = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) array[i] = binary.charCodeAt(i);
    return new Blob([array.buffer], { type: "image/jpeg" });
  }

  async function submitFile(file: Blob, filename = "capture.jpg") {
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const form = new FormData();
      form.append("image", file, filename);

      const res = await fetch(`${apiBase}/detect`, {
        method: "POST",
        body: form,
      });

      if (!res.ok) {
        const txt = await res.text();
        setError(`Server error ${res.status}: ${txt}`);
        return;
      }

      const data = await res.json();
      setPrediction({ emotion: data.emotion, confidence: data.confidence });

      // refresh logs
      fetchLogs();
    } catch (e) {
      console.error(e);
      setError("Network error while contacting backend.");
    } finally {
      setLoading(false);
    }
  }

  async function onUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    setSelectedFileName(file.name);
    await submitFile(file, file.name);
  }

  async function onCaptureClick() {
    const blob = captureFrame();
    if (!blob) {
      setError("Failed capturing frame");
      return;
    }
    await submitFile(blob, "capture.jpg");
  }

  function clearLogsUI() {
    setLogs([]);
  }

  function applyBackendUrl() {
    const trimmed = backendInput.trim();
    if (!trimmed) return;
    setApiBase(trimmed);
    localStorage.setItem("VITE_API_URL", trimmed);
    // refresh logs from new backend
    setTimeout(() => fetchLogs(), 250);
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 p-6">
      <div className="mx-auto max-w-3xl">
        <header className="flex items-center justify- mb-6">
          <h1 className="text-2xl font-semibold">Emotion Detection</h1>

        </header>

        <main className="bg-white p-6 rounded-lg shadow">
          {/* CAMERA (centered top) */}
          <div className="flex flex-col items-center gap-4">
            <div className="rounded-lg bg-black overflow-hidden w-[360px] h-[270px] flex items-center justify-center">
              {/* compact video */}
              <video
                ref={videoRef}
                className="w-full h-full object-cover"
                muted
                playsInline
                aria-label="Camera preview"
              />
            </div>

            {/* Buttons under camera — centered */}
            <div className="flex flex-wrap items-center justify-center gap-3">
              {!streaming ? (
                <button className="btn" onClick={startCamera} aria-label="Start camera">
                  Start camera
                </button>
              ) : (
                <button className="btn-outline" onClick={stopCamera} aria-label="Stop camera">
                  Stop camera
                </button>
              )}

              <button
                className="btn"
                onClick={onCaptureClick}
                disabled={!streaming || loading}
                aria-disabled={!streaming || loading}
                title={!streaming ? "Start camera first" : "Capture current frame and predict"}
              >
                {loading ? "Predicting…" : "Capture & Predict"}
              </button>

              <label className="btn cursor-pointer">
                Upload image
                <input type="file" accept="image/*" className="hidden" onChange={onUpload} />
              </label>

              <button className="btn-ghost" onClick={() => fetchLogs(8)}>
                Refresh logs
              </button>

              <button className="btn-danger" onClick={clearLogsUI}>
                Clear logs
              </button>
            </div>

            {/* small helper row: selected file / errors / prediction */}
            <div className="w-full text-center">
              {selectedFileName && <div className="text-sm text-slate-600">Selected: {selectedFileName}</div>}
              {error && <div className="mt-2 text-red-600">{error}</div>}
              {prediction && (
                <div className="mt-3 inline-block p-3 rounded-md bg-green-50 border border-green-100 text-left">
                  <div className="text-lg font-semibold">{prediction.emotion}</div>
                  <div className="text-sm text-slate-600">
                    Confidence: {(prediction.confidence * 100).toFixed(1)}%
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Backend URL and logs area */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left: logs */}
            <section className="bg-slate-50 p-4 rounded border">
              <h3 className="font-medium mb-3">Recent predictions</h3>
              <div className="space-y-2 max-h-64 overflow-auto pr-2">
                {logs.length === 0 && <div className="text-sm text-slate-500">No recent logs</div>}
                {logs.map((r, idx) => (
                  <div key={idx} className="text-sm border-b pb-2">
                    <div className="flex justify-between">
                      <div className="text-slate-700 font-medium">{r.emotion}</div>
                      <div className="text-slate-500">
                        {r.confidence ? (r.confidence * 100).toFixed(1) + "%" : "-"}
                      </div>
                    </div>
                    <div className="text-xs text-slate-400">
                      {r.ts ? new Date(r.ts).toLocaleString() : r.filename}
                    </div>
                  </div>
                ))}
              </div>
            </section>

          </div>
        </main>
      </div>

      {/* hidden canvas used for capture */}
      <canvas ref={canvasRef} className="hidden" />

      <style>{`
        /* tiny utility styles using Tailwind @apply not available here, so use classes mostly */
        .btn{ @apply inline-flex items-center gap-2 px-3 py-2 rounded bg-sky-600 text-white hover:bg-sky-700 disabled:opacity-60; }
        .btn-outline{ @apply inline-flex items-center gap-2 px-3 py-2 rounded border border-slate-300 text-slate-700 bg-white hover:bg-slate-50; }
        .btn-ghost{ @apply inline-flex items-center gap-2 px-3 py-2 rounded text-slate-600 hover:text-slate-800; }
        .btn-danger{ @apply inline-flex items-center gap-2 px-3 py-2 rounded bg-red-600 text-white hover:bg-red-700; }
        .input{ @apply w-full rounded border px-3 py-2 bg-white border-slate-300 }
      `}</style>
    </div>
  );
}
