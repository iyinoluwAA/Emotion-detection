import { getApiUrl } from "./config";

export async function uploadImage(file: Blob | File, filename = "upload.jpg") {
  const fd = new FormData();
  fd.append("image", file, filename);

  const res = await fetch(getApiUrl("detect"), {
    method: "POST",
    body: fd,
  });

  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`Server ${res.status}: ${txt}`);
  }
  return res.json();
}