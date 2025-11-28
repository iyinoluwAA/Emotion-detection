import React, { useState, useMemo } from "react";
import { TextInput, Select, Button, Group, Paper, Stack, MultiSelect, RangeSlider, Text, Badge, ActionIcon, Menu } from "@mantine/core";
import { IconSearch, IconFilter, IconX, IconDownload, IconFileText, IconCode } from "@tabler/icons-react";
import { DatePickerInput } from "@mantine/dates";
import { formatTimestamp } from "@/utils/dateFormat";

type FilterState = {
  search: string;
  emotions: string[];
  confidenceRange: [number, number];
  dateFrom: Date | null;
  dateTo: Date | null;
};

type Props = {
  searchValue: string;
  onSearchChange: (value: string) => void;
  emotionFilter: string[];
  onEmotionFilterChange: (value: string[]) => void;
  confidenceRange: [number, number];
  onConfidenceRangeChange: (value: [number, number]) => void;
  dateFrom: Date | null;
  dateTo: Date | null;
  onDateFromChange: (value: Date | null) => void;
  onDateToChange: (value: Date | null) => void;
  onExportCSV: () => void;
  onExportJSON: () => void;
  availableEmotions: string[];
  totalResults: number;
  filteredResults: number;
};

export function TableControls({
  searchValue,
  onSearchChange,
  emotionFilter,
  onEmotionFilterChange,
  confidenceRange,
  onConfidenceRangeChange,
  dateFrom,
  dateTo,
  onDateFromChange,
  onDateToChange,
  onExportCSV,
  onExportJSON,
  availableEmotions,
  totalResults,
  filteredResults,
}: Props) {
  const [filtersOpen, setFiltersOpen] = useState(false);
  const hasActiveFilters = emotionFilter.length > 0 || confidenceRange[0] > 0 || confidenceRange[1] < 100 || dateFrom || dateTo;

  const clearFilters = () => {
    onEmotionFilterChange([]);
    onConfidenceRangeChange([0, 100]);
    onDateFromChange(null);
    onDateToChange(null);
  };

  return (
    <Stack gap="md">
      {/* Search and Export Bar */}
      <Group gap="md" wrap="nowrap">
        <TextInput
          placeholder="Search by filename, emotion, timestamp..."
          leftSection={<IconSearch size={16} />}
          value={searchValue}
          onChange={(e) => onSearchChange(e.target.value)}
          style={{ flex: 1 }}
          rightSection={
            searchValue && (
              <ActionIcon size="sm" variant="subtle" onClick={() => onSearchChange("")}>
                <IconX size={14} />
              </ActionIcon>
            )
          }
        />
        <Menu position="bottom-end">
          <Menu.Target>
            <Button leftSection={<IconDownload size={16} />} variant="light">
              Export
            </Button>
          </Menu.Target>
          <Menu.Dropdown>
            <Menu.Item leftSection={<IconFileText size={16} />} onClick={onExportCSV}>
              Export as CSV
            </Menu.Item>
            <Menu.Item leftSection={<IconCode size={16} />} onClick={onExportJSON}>
              Export as JSON
            </Menu.Item>
          </Menu.Dropdown>
        </Menu>
        <Button
          variant={hasActiveFilters ? "filled" : "light"}
          color={hasActiveFilters ? "blue" : "gray"}
          leftSection={<IconFilter size={16} />}
          onClick={() => setFiltersOpen(!filtersOpen)}
        >
          Filters {hasActiveFilters && <Badge size="sm" ml={4}>{emotionFilter.length + (dateFrom ? 1 : 0) + (dateTo ? 1 : 0)}</Badge>}
        </Button>
      </Group>

      {/* Results Count */}
      <Group justify="space-between">
        <Text size="sm" c="dimmed">
          Showing {filteredResults} of {totalResults} results
          {searchValue && ` matching "${searchValue}"`}
        </Text>
        {hasActiveFilters && (
          <Button variant="subtle" size="xs" leftSection={<IconX size={14} />} onClick={clearFilters}>
            Clear filters
          </Button>
        )}
      </Group>

      {/* Filter Panel */}
      {filtersOpen && (
        <Paper withBorder p="md" radius="md">
          <Stack gap="md">
            <Group justify="space-between">
              <Text fw={600}>Filters</Text>
              <ActionIcon variant="subtle" onClick={() => setFiltersOpen(false)}>
                <IconX size={16} />
              </ActionIcon>
            </Group>

            <MultiSelect
              label="Emotions"
              placeholder="Select emotions to filter"
              data={availableEmotions}
              value={emotionFilter}
              onChange={(value) => onEmotionFilterChange(value)}
              clearable
            />

            <div>
              <Text size="sm" fw={500} mb="xs">
                Confidence: {confidenceRange[0]}% - {confidenceRange[1]}%
              </Text>
              <RangeSlider
                value={confidenceRange}
                onChange={(value) => onConfidenceRangeChange(value as [number, number])}
                min={0}
                max={100}
                step={1}
                marks={[
                  { value: 0, label: "0%" },
                  { value: 50, label: "50%" },
                  { value: 100, label: "100%" },
                ]}
              />
            </div>

            <Group grow>
              <DatePickerInput
                label="Date from"
                placeholder="Pick date"
                value={dateFrom}
                onChange={(value) => onDateFromChange(value as Date | null)}
                clearable
              />
              <DatePickerInput
                label="Date to"
                placeholder="Pick date"
                value={dateTo}
                onChange={(value) => onDateToChange(value as Date | null)}
                clearable
                minDate={dateFrom || undefined}
              />
            </Group>
          </Stack>
        </Paper>
      )}
    </Stack>
  );
}

