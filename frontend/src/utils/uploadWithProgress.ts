    export function uploadWithProgress(
    url: string,
    file: Blob | File,
    filename: string,
    onProgress?: (pct: number) => void
    ): Promise<any> {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        const fd = new FormData();
        fd.append("image", file, filename);

        xhr.open("POST", url, true);

        xhr.upload.onprogress = (ev) => {
        if (ev.lengthComputable && onProgress) {
            const pct = Math.round((ev.loaded / ev.total) * 100);
            onProgress(pct);
        }
        };

        xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
            try {
            const json = JSON.parse(xhr.responseText);
            resolve(json);
            } catch (e) {
            // if response isn't JSON, still resolve raw response
            resolve(xhr.responseText);
            }
        } else {
            reject(new Error(`Upload failed: ${xhr.status} ${xhr.statusText} - ${xhr.responseText}`));
        }
        };

        xhr.onerror = () => {
        reject(new Error("Network error during upload"));
        };

        xhr.send(fd);
    });
    }