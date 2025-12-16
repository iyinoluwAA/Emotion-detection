/**
 * Centralized API configuration
 * All API endpoints and base URL configuration should be defined here
 */

// Determine API URL based on environment
// In development (localhost), use local backend
// In production, use Render backend
const getBaseUrl = (): string => {
  // If VITE_API_URL is explicitly set, use it (but ensure it has https://)
  if (import.meta.env.VITE_API_URL) {
    const url = import.meta.env.VITE_API_URL.trim();
    // Ensure URL has protocol
    if (url && !url.startsWith('http://') && !url.startsWith('https://')) {
      console.warn('[API] VITE_API_URL missing protocol, adding https://');
      return `https://${url}`;
    }
    return url;
  }
  
  // In development (localhost), use local backend
  if (import.meta.env.DEV || import.meta.env.MODE === 'development') {
    return "http://localhost:5000";
  }
  
  // Production default: Render backend
  return "https://emotion-detection-1-8avi.onrender.com";
};

export const API_CONFIG = {
  baseUrl: getBaseUrl(),
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

