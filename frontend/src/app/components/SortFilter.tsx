interface SortFilterProps {
  sortBy: string;
  sortOrder: "asc" | "desc";
  onSortChange: (sortBy: string, sortOrder: "asc" | "desc") => void;
}

export default function SortFilter({ sortBy, sortOrder, onSortChange }: SortFilterProps) {
  const sortOptions = [
    { value: "relevance", label: "Relevance" },
    { value: "published_date", label: "Date" },
    { value: "title", label: "Title" },
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700">Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value, sortOrder)}
            className="border-2 border-gray-300 rounded-md px-3 py-2 text-sm text-gray-900 bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-w-[120px] cursor-pointer"
          >
            {sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>

          <button
            onClick={() => onSortChange(sortBy, sortOrder === "asc" ? "desc" : "asc")}
            className="flex items-center space-x-1 px-3 py-2 border-2 border-gray-300 rounded-md hover:bg-gray-50 text-sm text-gray-900 bg-white min-w-[100px] cursor-pointer"
          >
            <span>{sortOrder === "asc" ? "Ascending" : "Descending"}</span>
            <svg
              className={`h-4 w-4 transform transition-transform ${sortOrder === "desc" ? "rotate-180" : ""}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 11l5-5m0 0l5 5m-5-5v12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
