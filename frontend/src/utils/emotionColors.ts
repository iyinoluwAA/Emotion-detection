/**
 * Emotion color mapping - semantic colors for each emotion
 */

export function getEmotionColor(emotion: string | undefined | null): string {
  if (!emotion) return "gray";
  
  const emotionLower = emotion.toLowerCase().trim();
  
  // Positive emotions - warm, bright colors
  if (emotionLower === "happy" || emotionLower === "joy" || emotionLower === "happiness") {
    return "yellow"; // Bright, cheerful
  }
  
  if (emotionLower === "surprised" || emotionLower === "surprise" || emotionLower === "shocked") {
    return "orange"; // Vibrant, attention-grabbing
  }
  
  // Neutral emotions - cool, calm colors
  if (emotionLower === "neutral" || emotionLower === "calm" || emotionLower === "indifferent") {
    return "gray"; // Neutral, balanced
  }
  
  // Negative emotions - cool, darker colors
  if (emotionLower === "sad" || emotionLower === "sadness" || emotionLower === "sorrow") {
    return "blue"; // Cool, melancholic
  }
  
  if (emotionLower === "angry" || emotionLower === "anger" || emotionLower === "rage") {
    return "red"; // Intense, warning
  }
  
  if (emotionLower === "fear" || emotionLower === "afraid" || emotionLower === "scared") {
    return "violet"; // Dark, mysterious
  }
  
  if (emotionLower === "disgust" || emotionLower === "disgusted") {
    return "grape"; // Dark purple, unpleasant
  }
  
  // Default fallback
  return "cyan";
}

/**
 * Get all emotion colors as a map for charts
 */
export function getEmotionColorMap(): Record<string, string> {
  return {
    happy: "yellow",
    surprised: "orange",
    neutral: "gray",
    sad: "blue",
    angry: "red",
    fear: "violet",
    disgust: "grape",
  };
}

