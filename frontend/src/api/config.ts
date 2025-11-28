/**
 * Centralized API configuration
 * All API endpoints and base URL configuration should be defined here
 */

export const API_CONFIG = {
  baseUrl: import.meta.env.VITE_API_URL || "https://emotion-detection-1-8avi.onrender.com",
  endpoints: {
    detect: "/detect",
    logs: "/logs",
    metrics: "/metrics",
    health: "/health", // Backend health check endpoint
    images: "/images", // Image serving endpoint
  },
} as const;

/**
 * Get full API URL for an endpoint
 */
export function getApiUrl(endpoint: keyof typeof API_CONFIG.endpoints): string {
  return `${API_CONFIG.baseUrl}${API_CONFIG.endpoints[endpoint]}`;
}

/**
 * Get base API URL
 */
export function getApiBaseUrl(): string {
  return API_CONFIG.baseUrl;
}

/**
 * Get image URL from filename
 * Assumes images are served from /images/{filename} endpoint
 */
export function getImageUrl(filename: string): string {
  if (!filename || filename === "upload") {
    return "";
  }
  return `${API_CONFIG.baseUrl}/images/${filename}`;
}

