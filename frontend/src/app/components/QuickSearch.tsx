interface QuickSearchProps {
  onQuickSearch: (query: string) => void;
}

export default function QuickSearch({ onQuickSearch }: QuickSearchProps) {
  const suggestions = [
    "machine learning",
    "artificial intelligence",
    "data science",
    "blockchain",
    "cybersecurity",
    "financial analysis",
    "economics",
    "business strategy",
    "sustainable development",
    "digital transformation",
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <h3 className="text-sm font-medium text-gray-700 mb-3">Quick Search Suggestions</h3>
      <div className="flex flex-wrap gap-2">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => onQuickSearch(suggestion)}
            className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm hover:bg-blue-100 transition-colors duration-200 cursor-pointer"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}
