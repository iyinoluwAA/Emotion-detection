import { useState, useMemo, useCallback, useEffect } from "react";

type Row = {
  image: string;
  imageUrl?: string;
  emotions?: string;
  timestamp?: number | string;
  reviews: { positive: number; negative: number };
};

type FilterState = {
  search: string;
  emotions: string[];
  confidenceRange: [number, number];
  dateFrom: Date | null;
  dateTo: Date | null;
};

export function useTableState(rows: Row[], pageSize = 10) {
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSizeState, setPageSizeState] = useState(pageSize);
  const [filters, setFilters] = useState<FilterState>({
    search: "",
    emotions: [],
    confidenceRange: [0, 100],
    dateFrom: null,
    dateTo: null,
  });

  // Filter and search logic
  const filteredRows = useMemo(() => {
    let result = [...rows];

    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      result = result.filter((row) => {
        const filename = row.image?.toLowerCase() || "";
        const emotion = row.emotions?.toLowerCase() || "";
        const timestamp = row.timestamp?.toString().toLowerCase() || "";
        return filename.includes(searchLower) || emotion.includes(searchLower) || timestamp.includes(searchLower);
      });
    }

    // Emotion filter
    if (filters.emotions.length > 0) {
      result = result.filter((row) => row.emotions && filters.emotions.includes(row.emotions));
    }

    // Confidence range filter
    result = result.filter((row) => {
      const confidence = row.reviews.positive;
      return confidence >= filters.confidenceRange[0] && confidence <= filters.confidenceRange[1];
    });

    // Date range filter
    if (filters.dateFrom) {
      result = result.filter((row) => {
        if (!row.timestamp) return false;
        const rowDate = new Date(row.timestamp);
        return rowDate >= filters.dateFrom!;
      });
    }

    if (filters.dateTo) {
      result = result.filter((row) => {
        if (!row.timestamp) return false;
        const rowDate = new Date(row.timestamp);
        // Set to end of day
        const endOfDay = new Date(filters.dateTo!);
        endOfDay.setHours(23, 59, 59, 999);
        return rowDate <= endOfDay;
      });
    }

    return result;
  }, [rows, filters]);

  // Pagination
  const totalPages = Math.ceil(filteredRows.length / pageSizeState);
  
  // Auto-adjust current page if it's out of bounds (e.g., after deletion)
  useEffect(() => {
    if (totalPages > 0 && currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [totalPages, currentPage]);
  
  const paginatedRows = useMemo(() => {
    const start = (currentPage - 1) * pageSizeState;
    const end = start + pageSizeState;
    return filteredRows.slice(start, end);
  }, [filteredRows, currentPage, pageSizeState]);

  // Reset to page 1 when filters change
  const updateFilters = useCallback((newFilters: Partial<FilterState>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
    setCurrentPage(1);
  }, []);

  const updateSearch = useCallback((search: string) => {
    updateFilters({ search });
  }, [updateFilters]);

  const updateEmotionFilter = useCallback((emotions: string[]) => {
    updateFilters({ emotions });
  }, [updateFilters]);

  const updateConfidenceRange = useCallback((confidenceRange: [number, number]) => {
    updateFilters({ confidenceRange });
  }, [updateFilters]);

  const updateDateFrom = useCallback((dateFrom: Date | null) => {
    updateFilters({ dateFrom });
  }, [updateFilters]);

  const updateDateTo = useCallback((dateTo: Date | null) => {
    updateFilters({ dateTo });
  }, [updateFilters]);

  // Get unique emotions for filter dropdown
  const availableEmotions = useMemo(() => {
    const emotions = new Set<string>();
    rows.forEach((row) => {
      if (row.emotions) {
        emotions.add(row.emotions);
      }
    });
    return Array.from(emotions).sort();
  }, [rows]);

  return {
    // Data
    allRows: rows,
    filteredRows,
    paginatedRows,
    availableEmotions,

    // Pagination
    currentPage,
    totalPages,
    pageSize: pageSizeState,
    setCurrentPage,
    setPageSize: setPageSizeState,

    // Filters
    filters,
    updateSearch,
    updateEmotionFilter,
    updateConfidenceRange,
    updateDateFrom,
    updateDateTo,
    clearFilters: () => {
      setFilters({
        search: "",
        emotions: [],
        confidenceRange: [0, 100],
        dateFrom: null,
        dateTo: null,
      });
      setCurrentPage(1);
    },
  };
}

