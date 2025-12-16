import { getApiUrl } from "./config";

export async function uploadImage(file: Blob | File, filename = "upload.jpg", model: "base" | "fine-tuned" = "base") {
  const fd = new FormData();
  fd.append("image", file, filename);

  // Add model selection as query parameter
  const url = new URL(getApiUrl("detect"));
  url.searchParams.set("model", model);

  const res = await fetch(url.toString(), {
    method: "POST",
    body: fd,
  });

  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`Server ${res.status}: ${txt}`);
  }
  return res.json();
}