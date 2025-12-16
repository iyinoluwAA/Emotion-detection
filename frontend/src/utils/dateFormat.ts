/**
 * Date formatting utilities
 */

export function formatTimestamp(timestamp: string | number | undefined): string {
  if (!timestamp) return "-";
  
  try {
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) return String(timestamp);
    
    // Format: "Nov 28, 2024 10:15 AM"
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    }).format(date);
  } catch {
    return String(timestamp);
  }
}

export function formatRelativeTime(timestamp: string | number | undefined): string {
  if (!timestamp) return "-";
  
  try {
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) return String(timestamp);
    
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffSecs < 60) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return formatTimestamp(timestamp);
  } catch {
    return String(timestamp);
  }
}

