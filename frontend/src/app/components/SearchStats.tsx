interface SearchStatsProps {
  totalResults: number;
  currentPage: number;
  pageSize: number;
  totalPages: number;
  searchTime?: number;
}

export default function SearchStats({ totalResults, currentPage, pageSize, totalPages, searchTime }: SearchStatsProps) {
  const startResult = (currentPage - 1) * pageSize + 1;
  const endResult = Math.min(currentPage * pageSize, totalResults);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
        <div className="flex items-center space-x-4 text-sm text-gray-600">
          <span>
            Showing{" "}
            <span className="font-semibold text-gray-900">
              {startResult}-{endResult}
            </span>{" "}
            of <span className="font-semibold text-gray-900">{totalResults}</span> results
          </span>
          {searchTime && <span className="text-gray-500">({searchTime.toFixed(2)}s)</span>}
        </div>

        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <span>
            Page {currentPage} of {totalPages}
          </span>
        </div>
      </div>
    </div>
  );
}
