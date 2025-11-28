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
  
  // Mock data flag - set to true to use mock data for testing
  USE_MOCK_DATA: import.meta.env.VITE_USE_MOCK_DATA === "true" || import.meta.env.DEV,
} as const;

