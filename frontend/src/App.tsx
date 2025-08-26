// src/App.tsx
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

const DEFAULT_API = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

export default function App(): JSX.Element {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [streaming, setStreaming] = useState(false);
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<LogRecord[]>([]);
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);

  // runtime-configurable backend base (editable in UI)
  const [apiBase, setApiBase] = useState<string>(DEFAULT_API);
  const [backendInput, setBackendInput] = useState<string>("");

  useEffect(() => {
    fetchLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function fetchLogs(limit = 8) {
    setError(null);
    try {
      const res = await fetch(`${apiBase}/logs?limit=${limit}`);
      if (!res.ok) throw new Error(`Status ${res.status}`);
      const json = await res.json();
      setLogs(json.logs || []);
    } catch (e: any) {
      console.warn("Failed fetching logs:", e);
      setError("Failed fetching logs (check backend URL).");
    }
  }

  async function startCamera() {
    setError(null);
    try {
      // small camera constraints (reduce resolution for performance)
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 480 }, height: { ideal: 360 }, facingMode: "user" },
        audio: false,
      });
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
    // use smaller capture size to reduce upload and processing time
    const w = Math.min(480, video.videoWidth || 480);
    const h = Math.min(360, video.videoHeight || 360);
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    if (!ctx) return null;
    ctx.drawImage(video, 0, 0, w, h);
    return new Promise<Blob | null>((resolve) => {
      canvas.toBlob((b) => resolve(b ?? null), "image/jpeg", 0.85);
    }) as unknown as Blob; // cast: we immediately return a blob in submitFile flow
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
        const txt = await res.text().catch(() => "");
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
    // captureFrame above returns a Blob via toBlob - if it's a Promise in your environment,
    // guard for that (older TS signatures). Let's cover both cases:
    try {
      const b = blob as unknown;
      if (b instanceof Blob) {
        await submitFile(b, "capture.jpg");
        return;
      }
      // If promise-like:
      const resolved = await (blob as unknown as Promise<Blob | null>);
      if (!resolved) {
        setError("Failed capturing frame");
        return;
      }
      await submitFile(resolved, "capture.jpg");
    } catch (ex) {
      console.error(ex);
      setError("Failed capturing frame.");
    }
  }

  function clearLogsView() {
    setLogs([]);
  }

  // use the backend input (applies as runtime override)
  function applyBackendUrl() {
    const trimmed = backendInput.trim();
    if (trimmed) {
      setApiBase(trimmed);
      setBackendInput("");
      setError(null);
      fetchLogs();
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 p-6">
      <div className="mx-auto max-w-3xl">
        <header className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-2xl font-semibold">Emotion Detector — Frontend (MVP)</h1>
          </div>

          <div className="flex items-center gap-2">
            <input
              aria-label="Backend URL"
              className="px-2 py-1 border rounded text-sm"
              placeholder="override backend URL (https://...)"
              value={backendInput}
              onChange={(e) => setBackendInput(e.target.value)}
            />
            <button className="btn" onClick={applyBackendUrl} disabled={!backendInput.trim()}>
              Apply
            </button>
          </div>
        </header>

        <main className="bg-white p-4 rounded-lg shadow">
          <div className="flex flex-col items-center gap-4">
            {/* centered small camera on top */}
            <div className="w-80 h-60 bg-black rounded overflow-hidden flex items-center justify-center">
              <video ref={videoRef} className="w-full h-full object-cover" muted />
              <canvas ref={canvasRef} className="hidden" />
              {!streaming && <div className="text-sm text-white">Camera inactive</div>}
            </div>

            {/* buttons under the camera */}
            <div className="flex gap-2">
              {!streaming ? (
                <button className="btn" onClick={startCamera}>
                  Start camera
                </button>
              ) : (
                <button className="btn" onClick={stopCamera}>
                  Stop camera
                </button>
              )}

              <button className="btn" onClick={onCaptureClick} disabled={!streaming || loading}>
                {loading ? "Predicting…" : "Capture & Predict"}
              </button>

              <label className="btn cursor-pointer">
                Upload image
                <input type="file" accept="image/*" className="hidden" onChange={onUpload} />
              </label>

              <button className="btn" onClick={clearLogsView}>
                Clear logs
              </button>
            </div>

            {selectedFileName && <div className="text-sm text-slate-600">Selected: {selectedFileName}</div>}

            {error && <div className="mt-1 text-red-600">{error}</div>}

            {prediction && (
              <div className="mt-2 p-3 rounded-md bg-green-50 border border-green-100 w-full text-center">
                <div className="text-lg font-semibold">{prediction.emotion}</div>
                <div className="text-sm text-slate-600">
                  Confidence: {(prediction.confidence * 100).toFixed(1)}%
                </div>
              </div>
            )}

            {/* logs under everything */}
            <section className="w-full mt-4">
              <h3 className="font-medium mb-2">Recent predictions</h3>
              <div className="max-h-64 overflow-auto border rounded p-2 space-y-2 bg-slate-50">
                {logs.length === 0 && <div className="text-sm text-slate-500">No recent logs</div>}
                {logs.map((r, idx) => (
                  <div key={idx} className="text-sm bg-white p-2 rounded shadow-sm">
                    <div className="flex justify-between">
                      <div className="text-slate-700">{r.emotion}</div>
                      <div className="text-slate-500">
                        {r.confidence ? (r.confidence * 100).toFixed(1) + "%" : "-"}
                      </div>
                    </div>
                    <div className="text-xs text-slate-400">
                      {r.ts ? new Date(r.ts).toLocaleString() : ""}
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-3 flex gap-2">
                <button className="btn" onClick={() => fetchLogs(8)}>
                  Refresh
                </button>
                <button className="btn" onClick={() => fetchLogs(20)}>
                  Load 20
                </button>
              </div>
            </section>
          </div>
        </main>
      </div>

      <style>{`
        .btn{ @apply inline-flex items-center gap-2 px-3 py-2 rounded bg-sky-600 text-white hover:bg-sky-700; }
      `}</style>
    </div>
  );
}
