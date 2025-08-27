"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { ApiService, Publication } from "../services/api";
import LoadingSpinner from "./LoadingSpinner";
import { SearchSkeleton } from "./PublicationSkeleton";
import SearchStats from "./SearchStats";
import SortFilter from "./SortFilter";
import QuickSearch from "./QuickSearch";

interface SearchComponentProps {
  onResultsChange?: (total: number) => void;
}

export default function SearchComponent({ onResultsChange }: SearchComponentProps) {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [results, setResults] = useState<Publication[]>([]);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalResults, setTotalResults] = useState(0);
  const [pageSize] = useState(10);
  const [error, setError] = useState<string | null>(null);
  const [searchTime, setSearchTime] = useState<number>(0);
  const [sortBy, setSortBy] = useState("relevance");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const debounceRef = useRef<NodeJS.Timeout | null>(null);

  // Debounce effect for query
  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      setDebouncedQuery(query);
    }, 4000); // 300ms debounce delay

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [query]);

  // Clear search function
  const handleClearSearch = () => {
    // Clear any pending debounce timeout
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    setQuery("");
    setDebouncedQuery(""); // Also clear debounced query immediately
    setCurrentPage(1);
    searchPublications("", 1); // Trigger search with empty query to show all results
  };

  // Search function
  const searchPublications = useCallback(
    async (searchQuery: string, page: number = 1) => {
      try {
        setLoading(true);
        setError(null);
        const startTime = performance.now();

        const data = await ApiService.searchPublications(searchQuery, page, pageSize);

        const endTime = performance.now();
        setSearchTime((endTime - startTime) / 1000);

        setResults(data.results);
        setTotalPages(data.total_pages);
        setTotalResults(data.total);
        setCurrentPage(data.page);

        // Notify parent component of results change
        if (onResultsChange) {
          onResultsChange(data.total);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
        setResults([]);
      } finally {
        setLoading(false);
      }
    },
    [pageSize, onResultsChange]
  );

  // Handle search
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    searchPublications(query, 1);
  };

  // Handle page change
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    searchPublications(query, page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // Handle quick search
  const handleQuickSearch = (suggestion: string) => {
    setQuery(suggestion);
    setCurrentPage(1);
    searchPublications(suggestion, 1);
  };

  // Handle sort change
  const handleSortChange = (newSortBy: string, newSortOrder: "asc" | "desc") => {
    setSortBy(newSortBy);
    setSortOrder(newSortOrder);

    // Sort current results
    const sortedResults = [...results].sort((a, b) => {
      let aVal, bVal;

      switch (newSortBy) {
        case "published_date":
          aVal = new Date(a.published_date || "").getTime();
          bVal = new Date(b.published_date || "").getTime();
          break;
        case "title":
          aVal = a.title.toLowerCase();
          bVal = b.title.toLowerCase();
          break;
        case "relevance":
        default:
          aVal = a.score;
          bVal = b.score;
          break;
      }

      if (newSortOrder === "asc") {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

    setResults(sortedResults);
  };

  // Load initial data and handle debounced search
  useEffect(() => {
    searchPublications(""); // Load all publications initially
  }, [searchPublications]);

  // Effect to trigger search when debounced query changes
  useEffect(() => {
    setCurrentPage(1);
    searchPublications(debouncedQuery, 1);
  }, [debouncedQuery, searchPublications]);

  return (
    <div className="space-y-6">
      {/* Search Section */}
      <div className="bg-gradient-to-r from-white to-gray-50 rounded-2xl shadow-xl p-8 border border-gray-200 backdrop-blur-sm">
        <form onSubmit={handleSearch} className="space-y-6">
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg
                className="h-6 w-6 text-gray-400 group-focus-within:text-blue-500 transition-colors duration-200"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search publications by title, authors, or keywords..."
              className="w-full pl-12 pr-12 py-4 border-2 border-gray-300 rounded-xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 text-lg text-gray-900 bg-white placeholder-gray-400 shadow-sm transition-all duration-200 hover:shadow-md"
            />
            {query && (
              <button
                type="button"
                onClick={handleClearSearch}
                className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600 transition-colors duration-200 cursor-pointer"
                aria-label="Clear search"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>

          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
            <div className="flex flex-wrap gap-3">
              <button
                type="submit"
                disabled={loading}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-3 rounded-xl hover:from-blue-700 hover:to-indigo-700 focus:ring-4 focus:ring-blue-500/20 focus:ring-offset-2 font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 cursor-pointer"
              >
                {loading ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span>Searching...</span>
                  </>
                ) : (
                  <>
                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                      />
                    </svg>
                    <span>Search</span>
                  </>
                )}
              </button>

              {query && (
                <button
                  type="button"
                  onClick={handleClearSearch}
                  className="bg-gray-100 text-gray-700 px-6 py-3 rounded-xl hover:bg-gray-200 focus:ring-4 focus:ring-gray-500/20 font-medium transition-all duration-200 flex items-center space-x-2 shadow-sm hover:shadow-md cursor-pointer"
                >
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                  <span>Clear</span>
                </button>
              )}
            </div>

            {totalResults > 0 && (
              <div className="bg-blue-50 text-blue-700 px-4 py-2 rounded-xl border border-blue-200">
                Found <span className="font-bold text-blue-800">{totalResults.toLocaleString()}</span> publications
                {loading && <span className="ml-2 text-blue-600">...</span>}
              </div>
            )}
          </div>
        </form>
      </div>

      {/* Quick Search Suggestions - Show when no query or no results */}
      {(!query || (!loading && results.length === 0 && query)) && <QuickSearch onQuickSearch={handleQuickSearch} />}

      {/* Error Message */}
      {error && (
        <div className="bg-gradient-to-r from-red-50 to-red-100 border-2 border-red-200 rounded-xl p-6 shadow-lg">
          <div className="flex items-center space-x-3 text-red-700">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-red-800">Search Error</h3>
              <p className="text-red-600">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Search Stats */}
      {!loading && totalResults > 0 && (
        <SearchStats
          totalResults={totalResults}
          currentPage={currentPage}
          pageSize={pageSize}
          totalPages={totalPages}
          searchTime={searchTime}
        />
      )}

      {/* Sort/Filter Controls */}
      {!loading && totalResults > 0 && (
        <SortFilter sortBy={sortBy} sortOrder={sortOrder} onSortChange={handleSortChange} />
      )}

      {/* Results Section */}
      <div className="space-y-4">
        {loading ? (
          <SearchSkeleton />
        ) : (
          results.map((publication, index) => (
            <PublicationCard key={`${publication.link}-${index}`} publication={publication} />
          ))
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={handlePageChange} />
      )}

      {/* No Results */}
      {!loading && results.length === 0 && query && (
        <div className="text-center py-16 bg-gradient-to-br from-gray-50 to-white rounded-2xl shadow-xl border border-gray-200">
          <div className="max-w-md mx-auto">
            <div className="bg-gray-100 rounded-full p-4 w-20 h-20 mx-auto mb-6 flex items-center justify-center">
              <svg className="h-10 w-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0120 12a8 8 0 00-16 0 8 8 0 002 5.291"
                />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">No publications found</h3>
            <p className="text-gray-600 mb-6">We couldn&apos;t find any publications matching your search terms.</p>
            <div className="space-y-3">
              <p className="text-sm text-gray-500">Try:</p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Using different keywords</li>
                <li>• Checking your spelling</li>
                <li>• Using broader search terms</li>
              </ul>
            </div>
            <button
              onClick={handleClearSearch}
              className="mt-6 bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-colors duration-200 font-medium shadow-lg hover:shadow-xl cursor-pointer"
            >
              Browse All Publications
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// Publication Card Component
function PublicationCard({ publication }: { publication: Publication }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const formatDate = (dateString: string) => {
    if (!dateString) return "Date not available";
    try {
      // Handle the format "11 Feb 2025"
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        // If date parsing fails, return the original string
        return dateString;
      }
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    } catch {
      return dateString;
    }
  };

  const truncateText = (text: string, maxLength: number) => {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

  return (
    <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-200 overflow-hidden group hover:-translate-y-1">
      <div className="p-8">
        {/* Header */}
        <div className="flex justify-between items-start mb-6">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-900 mb-3 leading-tight">
              <a
                href={publication.link}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-blue-600 transition-colors duration-200 group-hover:text-blue-700"
              >
                {publication.title}
              </a>
            </h3>

            {/* Authors */}
            <div className="flex flex-wrap items-center gap-2 mb-4">
              <div className="bg-blue-100 rounded-full p-1.5">
                <svg className="h-4 w-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
              </div>
              <div className="text-sm text-gray-600">
                {publication.authors && publication.authors.length > 0
                  ? publication.authors.slice(0, 3).map((author, idx) => (
                      <span key={idx} className="inline-block">
                        {author.profile ? (
                          <a
                            href={author.profile}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 hover:underline transition-colors duration-200 font-medium"
                          >
                            {author.name}
                          </a>
                        ) : (
                          <span>{author.name}</span>
                        )}
                        {idx < Math.min(publication.authors.length - 1, 2) ? ", " : ""}
                        {idx === 2 && publication.authors.length > 3 ? " and others" : ""}
                      </span>
                    ))
                  : "Authors not available"}
              </div>
            </div>

            {/* Date and Score */}
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center space-x-2 bg-gray-100 rounded-full px-3 py-2">
                <div className="bg-green-100 rounded-full p-1">
                  <svg className="h-3 w-3 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                </div>
                <span className="text-sm font-medium text-gray-700">{formatDate(publication.published_date)}</span>
              </div>

              {publication.score > 0 && (
                <div className="bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-800 px-3 py-2 rounded-full text-sm font-semibold border border-blue-200">
                  <span className="text-xs">Relevance</span> {(publication.score * 100).toFixed(1)}%
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Abstract */}
        {publication.abstract && (
          <div className="space-y-4">
            <div className="border-t border-gray-200 pt-6">
              <h4 className="text-base font-bold text-gray-800 mb-3 flex items-center">
                <div className="bg-purple-100 rounded-full p-1.5 mr-2">
                  <svg className="h-4 w-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5.291A7.962 7.962 0 0120 12a8 8 0 00-16 0 8 8 0 002 5.291"
                    />
                  </svg>
                </div>
                Abstract
              </h4>
              <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                <p className="text-gray-700 leading-relaxed">
                  {isExpanded ? publication.abstract : truncateText(publication.abstract, 300)}
                  {publication.abstract.length > 300 && (
                    <button
                      onClick={() => setIsExpanded(!isExpanded)}
                      className="ml-2 text-blue-600 hover:text-blue-800 font-semibold text-sm underline decoration-2 underline-offset-2 hover:decoration-blue-800 transition-all duration-200 cursor-pointer"
                    >
                      {isExpanded ? "Show less" : "Read more"}
                    </button>
                  )}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-between items-center mt-8 pt-6 border-t border-gray-200">
          <a
            href={publication.link}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-xl hover:from-blue-700 hover:to-indigo-700 focus:ring-4 focus:ring-blue-500/20 transition-all duration-200 text-sm font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 group"
          >
            <span>View Publication</span>
            <svg
              className="h-4 w-4 group-hover:translate-x-0.5 transition-transform duration-200"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
              />
            </svg>
          </a>
        </div>
      </div>
    </div>
  );
}

// Pagination Component
function Pagination({
  currentPage,
  totalPages,
  onPageChange,
}: {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}) {
  const getVisiblePages = () => {
    const pages: (number | string)[] = [];
    const showEllipsis = totalPages > 7;

    if (!showEllipsis) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (currentPage <= 4) {
        pages.push(1, 2, 3, 4, 5, "...", totalPages);
      } else if (currentPage >= totalPages - 3) {
        pages.push(1, "...", totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages);
      } else {
        pages.push(1, "...", currentPage - 1, currentPage, currentPage + 1, "...", totalPages);
      }
    }

    return pages;
  };

  return (
    <div className="flex items-center justify-center space-x-2 py-6">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="px-3 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
      >
        Previous
      </button>

      {getVisiblePages().map((page, index) => (
        <button
          key={index}
          onClick={() => (typeof page === "number" ? onPageChange(page) : undefined)}
          disabled={typeof page !== "number"}
          className={`px-3 py-2 rounded-lg cursor-pointer ${
            page === currentPage
              ? "bg-blue-600 text-white"
              : typeof page === "number"
              ? "border border-gray-300 text-gray-700 hover:bg-gray-50"
              : "text-gray-400 cursor-default"
          }`}
        >
          {page}
        </button>
      ))}

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="px-3 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
      >
        Next
      </button>
    </div>
  );
}
