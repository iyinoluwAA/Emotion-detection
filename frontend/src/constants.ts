/**
 * Application constants
 * Centralized configuration values
 */

export const CONSTANTS = {
  // API limits
  DEFAULT_LOG_LIMIT: 20,
  REFRESH_LOG_LIMIT: 8,
  
  // Image settings
  THUMBNAIL_SIZE: 80,
  IMAGE_PREVIEW_SIZE: 400,
  
  // UI settings
  GRID_GUTTER: "lg",
  CARD_PADDING: "md",
  CARD_RADIUS: "md",
  
  // Force mock data (only for development/testing)
  // This should be false in production - backend health check will determine mock usage
  FORCE_MOCK_DATA: import.meta.env.VITE_FORCE_MOCK_DATA === "true",
} as const;

