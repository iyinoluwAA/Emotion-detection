/**
 * Mock data for development and testing
 */

export const MOCK_LOGS = [
  {
    id: 1,
    ts: "2024-11-28T10:15:30Z",
    filename: "happy_face_001.jpg",
    emotion: "happy",
    confidence: 0.95,
  },
  {
    id: 2,
    ts: "2024-11-28T10:14:22Z",
    filename: "neutral_face_002.jpg",
    emotion: "neutral",
    confidence: 0.87,
  },
  {
    id: 3,
    ts: "2024-11-28T10:13:15Z",
    filename: "sad_face_003.jpg",
    emotion: "sad",
    confidence: 0.82,
  },
  {
    id: 4,
    ts: "2024-11-28T10:12:08Z",
    filename: "angry_face_004.jpg",
    emotion: "angry",
    confidence: 0.91,
  },
  {
    id: 5,
    ts: "2024-11-28T10:11:01Z",
    filename: "surprised_face_005.jpg",
    emotion: "surprised",
    confidence: 0.78,
  },
  {
    id: 6,
    ts: "2024-11-28T10:09:54Z",
    filename: "happy_face_006.jpg",
    emotion: "happy",
    confidence: 0.93,
  },
  {
    id: 7,
    ts: "2024-11-28T10:08:47Z",
    filename: "neutral_face_007.jpg",
    emotion: "neutral",
    confidence: 0.85,
  },
  {
    id: 8,
    ts: "2024-11-28T10:07:40Z",
    filename: "fear_face_008.jpg",
    emotion: "fear",
    confidence: 0.76,
  },
];

// Use placeholder images from a service like Unsplash or Picsum
export function getMockImageUrl(filename: string): string {
  // Using Picsum Photos for placeholder images - different image per filename
  const seed = filename.split("_").join("").replace(".jpg", "");
  return `https://picsum.photos/seed/${seed}/400/300`;
}

export const MOCK_METRICS = {
  total: 8,
  by_label: {
    happy: 2,
    neutral: 2,
    sad: 1,
    angry: 1,
    surprised: 1,
    fear: 1,
  },
};

