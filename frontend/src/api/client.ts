export async function uploadImage(apiUrl: string, file: Blob | File, filename = "upload.jpg") {
  const fd = new FormData();
  fd.append("image", file, filename);

  const res = await fetch(`${apiUrl}/detect`, {
    method: "POST",
    body: fd,
  });

  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`Server ${res.status}: ${txt}`);
  }
  return res.json();
}