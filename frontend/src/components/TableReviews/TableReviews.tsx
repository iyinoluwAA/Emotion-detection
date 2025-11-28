import React, { useState, useMemo } from "react";
import { Anchor, Group, Progress, Table, Text, Image, Modal, Badge, Tooltip, Box, ActionIcon } from "@mantine/core";
import { IconPhoto, IconArrowUp, IconArrowDown, IconArrowsSort } from "@tabler/icons-react";
import classes from "./TableReviews.module.css";
import { getImageUrl } from "@/api/config";
import { CONSTANTS } from "@/constants";
import { formatTimestamp, formatRelativeTime } from "@/utils/dateFormat";
import { getEmotionColor } from "@/utils/emotionColors";
import { EmptyState } from "@/components/EmptyState/EmptyState";

type Row = {
  image: string;
  imageUrl?: string;
  emotions?: string;
  timestamp?: number | string;
  reviews: { positive: number; negative: number };
};

type SortField = "timestamp" | "emotion" | "confidence" | null;
type SortDirection = "asc" | "desc";

export function TableReviews({ rows = [] as Row[] }: { rows?: Row[] }) {
  const [opened, setOpened] = useState(false);
  const [selectedImage, setSelectedImage] = useState<{ url: string; filename: string; emotion?: string } | null>(null);
  const [sortField, setSortField] = useState<SortField>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");

  const sortedRows = useMemo(() => {
    if (!sortField) return rows;
    
    return [...rows].sort((a, b) => {
      let aVal: any;
      let bVal: any;
      
      switch (sortField) {
        case "timestamp":
          aVal = a.timestamp ? new Date(a.timestamp).getTime() : 0;
          bVal = b.timestamp ? new Date(b.timestamp).getTime() : 0;
          break;
        case "emotion":
          aVal = a.emotions || "";
          bVal = b.emotions || "";
          break;
        case "confidence":
          aVal = a.reviews.positive;
          bVal = b.reviews.positive;
          break;
        default:
          return 0;
      }
      
      if (aVal < bVal) return sortDirection === "asc" ? -1 : 1;
      if (aVal > bVal) return sortDirection === "asc" ? 1 : -1;
      return 0;
    });
  }, [rows, sortField, sortDirection]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) {
      return <IconArrowsSort size={14} style={{ opacity: 0.3 }} />;
    }
    return sortDirection === "asc" ? <IconArrowUp size={14} /> : <IconArrowDown size={14} />;
  };

  if (!rows || rows.length === 0) {
    return (
      <EmptyState
        title="No predictions yet"
        message="Upload an image or capture from camera to see emotion analysis results here."
        icon={<IconPhoto size={64} stroke={1.5} style={{ opacity: 0.5 }} />}
      />
    );
  }

  const handleImageClick = (row: Row) => {
    const imageUrl = row.imageUrl || getImageUrl(row.image);
    if (imageUrl) {
      setSelectedImage({
        url: imageUrl,
        filename: row.image,
        emotion: row.emotions,
      });
      setOpened(true);
    }
  };

  const trs = sortedRows.map((row) => {
    const totalReviews = row.reviews.positive + row.reviews.negative;
    const positive = totalReviews > 0 ? (row.reviews.positive / totalReviews) * 100 : 0;
    const negative = totalReviews > 0 ? (row.reviews.negative / totalReviews) * 100 : 0;
    const imageUrl = row.imageUrl || getImageUrl(row.image);
    const hasImage = imageUrl && row.image !== "upload";

    return (
      <Table.Tr key={row.image + (row.timestamp ?? "")} className={classes.tableRow}>
        <Table.Td>
          <Group gap="xs" align="center">
            {hasImage ? (
              <Tooltip label="Click to view full image" withArrow>
                <Box
                  style={{
                    cursor: "pointer",
                    borderRadius: 6,
                    overflow: "hidden",
                    border: "1px solid var(--mantine-color-gray-3)",
                    transition: "transform 0.2s, box-shadow 0.2s",
                  }}
                  onClick={() => handleImageClick(row)}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = "scale(1.05)";
                    e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.15)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = "scale(1)";
                    e.currentTarget.style.boxShadow = "none";
                  }}
                >
                  <Image
                    src={imageUrl}
                    alt={row.image}
                    w={CONSTANTS.THUMBNAIL_SIZE}
                    h={CONSTANTS.THUMBNAIL_SIZE}
                    fit="cover"
                    fallbackSrc="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80'%3E%3Crect fill='%23ddd' width='80' height='80'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' dy='.3em' fill='%23999' font-size='12'%3ENo Image%3C/text%3E%3C/svg%3E"
                  />
                </Box>
              </Tooltip>
            ) : (
              <Box
                style={{
                  width: CONSTANTS.THUMBNAIL_SIZE,
                  height: CONSTANTS.THUMBNAIL_SIZE,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  backgroundColor: "var(--mantine-color-gray-1)",
                  borderRadius: 6,
                  border: "1px solid var(--mantine-color-gray-3)",
                }}
              >
                <IconPhoto size={24} color="var(--mantine-color-gray-5)" />
              </Box>
            )}
            <Text fz="sm" fw={500} truncate style={{ maxWidth: 120 }}>
              {row.image}
            </Text>
          </Group>
        </Table.Td>
        <Table.Td>
          <Tooltip label={formatTimestamp(row.timestamp)} withArrow>
            <Text fz="sm" c="dimmed">
              {formatRelativeTime(row.timestamp)}
            </Text>
          </Tooltip>
        </Table.Td>
        <Table.Td>
          {row.emotions ? (
            <Badge color={getEmotionColor(row.emotions)} variant="light" size="md">
              {row.emotions}
            </Badge>
          ) : (
            <Text fz="sm" c="dimmed">
              -
            </Text>
          )}
        </Table.Td>
        <Table.Td>
          <Text fz="sm" fw={600}>
            {Intl.NumberFormat().format(totalReviews)}
          </Text>
        </Table.Td>
        <Table.Td>
          <Group justify="space-between" gap="xs" mb={4}>
            <Text fz="xs" c="teal" fw={700}>
              {Math.round(positive)}%
            </Text>
            <Text fz="xs" c="red" fw={700}>
              {Math.round(negative)}%
            </Text>
          </Group>
          <Progress.Root style={{ height: 10, borderRadius: 4 }}>
            <Progress.Section className={classes.progressSection} value={positive} color="teal" />
            <Progress.Section className={classes.progressSection} value={negative} color="red" />
          </Progress.Root>
        </Table.Td>
      </Table.Tr>
    );
  });

  return (
    <>
      <Box style={{ overflowX: "auto", WebkitOverflowScrolling: "touch" }}>
        <Table.ScrollContainer minWidth={600}>
          <Table
            verticalSpacing="md"
            highlightOnHover
            style={{ tableLayout: "auto" }}
          >
            <Table.Thead>
              <Table.Tr>
                <Table.Th style={{ minWidth: 150 }}>Image</Table.Th>
                <Table.Th style={{ minWidth: 140 }}>
                  <Group gap={4} style={{ cursor: "pointer" }} onClick={() => handleSort("timestamp")}>
                    <Text fw={600}>Timestamp</Text>
                    <SortIcon field="timestamp" />
                  </Group>
                </Table.Th>
                <Table.Th style={{ minWidth: 100 }}>
                  <Group gap={4} style={{ cursor: "pointer" }} onClick={() => handleSort("emotion")}>
                    <Text fw={600}>Emotion</Text>
                    <SortIcon field="emotion" />
                  </Group>
                </Table.Th>
                <Table.Th style={{ minWidth: 100 }}>
                  <Group gap={4} style={{ cursor: "pointer" }} onClick={() => handleSort("confidence")}>
                    <Text fw={600}>Confidence</Text>
                    <SortIcon field="confidence" />
                  </Group>
                </Table.Th>
                <Table.Th style={{ minWidth: 180 }}>Distribution</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>{trs}</Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      </Box>

      <Modal
        opened={opened}
        onClose={() => setOpened(false)}
        title={
          <Group gap="xs">
            <Text fw={600}>{selectedImage?.filename}</Text>
            {selectedImage?.emotion && (
              <Badge color="blue" variant="light">
                {selectedImage.emotion}
              </Badge>
            )}
          </Group>
        }
        size="xl"
        centered
      >
        {selectedImage && (
          <Image
            src={selectedImage.url}
            alt={selectedImage.filename}
            fit="contain"
            style={{ maxHeight: "70vh", width: "100%" }}
            fallbackSrc="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300'%3E%3Crect fill='%23ddd' width='400' height='300'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' dy='.3em' fill='%23999'%3EImage not available%3C/text%3E%3C/svg%3E"
          />
        )}
      </Modal>
    </>
  );
}