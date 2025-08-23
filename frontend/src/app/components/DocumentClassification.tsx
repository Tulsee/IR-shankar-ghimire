"use client";

import { useState, useEffect } from "react";
import { ApiService, ClassificationResult, ModelInfo } from "../services/api";
import LoadingSpinner from "./LoadingSpinner";

export default function DocumentClassification() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<ClassificationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modelType, setModelType] = useState<"naive_bayes" | "logistic_regression">("naive_bayes");
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);

  // Load model info on component mount
  useEffect(() => {
    const loadModelInfo = async () => {
      try {
        const info = await ApiService.getModelInfo(modelType);
        setModelInfo(info);
      } catch (err) {
        console.error("Failed to load model info:", err);
      }
    };

    loadModelInfo();
  }, [modelType]);

  const handleClassify = async () => {
    if (!text.trim()) {
      setError("Please enter some text to classify");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const classificationResult = await ApiService.classifyText(text, modelType);
      setResult(classificationResult);
    } catch (err) {
      setError("Failed to classify text. Please try again.");
      console.error("Classification error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setText("");
    setResult(null);
    setError(null);
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "business":
        return "text-blue-700 bg-blue-100 border-blue-300";
      case "health":
        return "text-green-700 bg-green-100 border-green-300";
      case "politics":
        return "text-purple-700 bg-purple-100 border-purple-300";
      default:
        return "text-gray-700 bg-gray-100 border-gray-300";
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "text-green-600";
    if (confidence >= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      {/* Model Selection Card */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
        <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
              />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Model Configuration
          </h2>
        </div>

        <div className="p-6">
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="model-select" className="block text-sm font-semibold text-gray-700 mb-3">
                Classification Algorithm
              </label>
              <div className="relative">
                <select
                  id="model-select"
                  value={modelType}
                  onChange={(e) => setModelType(e.target.value as "naive_bayes" | "logistic_regression")}
                  className="w-full appearance-none bg-white border-2 border-gray-300 rounded-xl px-4 py-3 pr-10 text-gray-900 font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 hover:border-gray-400"
                >
                  <option value="naive_bayes">Naive Bayes Classifier</option>
                  <option value="logistic_regression">Logistic Regression</option>
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none">
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
            </div>

            {modelInfo && (
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 border border-green-200">
                <div className="flex items-center gap-2 mb-2">
                  <div className={`w-3 h-3 rounded-full ${modelInfo.is_trained ? "bg-green-500" : "bg-red-500"}`}></div>
                  <span className="font-semibold text-gray-700">
                    {modelInfo.is_trained ? "Model Ready" : "Model Not Trained"}
                  </span>
                </div>
                <div className="text-sm text-gray-600">
                  <span className="font-medium">{modelInfo.total_documents}</span> training documents
                </div>
                <div className="text-xs text-gray-500 mt-1">Categories: {modelInfo.categories.join(", ")}</div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Input Section */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
            Text Input
          </h2>
        </div>

        <div className="p-6 space-y-6">
          <div>
            <label htmlFor="text-input" className="block text-sm font-semibold text-gray-700 mb-3">
              Enter text to classify
            </label>
            <div className="relative">
              <textarea
                id="text-input"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Type or paste your text here... Try different types of content to test the model's accuracy and robustness."
                className="w-full h-48 p-4 border-2 border-gray-300 rounded-xl resize-none text-gray-900 text-base leading-relaxed placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 hover:border-gray-400"
                maxLength={5000}
              />
              <div className="absolute bottom-3 right-3 text-xs text-gray-500 bg-white px-2 py-1 rounded-md border">
                {text.length}/5000 chars • {text.split(/\s+/).filter((word) => word.length > 0).length} words
              </div>
            </div>
          </div>

          {/* Quick Test Examples */}
          <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Quick Test Examples
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <button
                onClick={() =>
                  setText(
                    "The government announced new economic policies to stimulate growth and reduce unemployment. Parliament will vote on the budget next week."
                  )
                }
                className="text-left p-4 bg-purple-100 hover:bg-purple-200 text-purple-800 rounded-lg text-sm transition-all duration-200 hover:shadow-md transform hover:-translate-y-0.5"
              >
                <div className="font-semibold mb-1">Politics</div>
                <div className="text-xs opacity-80">Government policies & parliament</div>
              </button>
              <button
                onClick={() =>
                  setText(
                    "The company reported strong quarterly earnings driven by increased sales and successful product launches in emerging markets."
                  )
                }
                className="text-left p-4 bg-blue-100 hover:bg-blue-200 text-blue-800 rounded-lg text-sm transition-all duration-200 hover:shadow-md transform hover:-translate-y-0.5"
              >
                <div className="font-semibold mb-1">Business</div>
                <div className="text-xs opacity-80">Earnings & market performance</div>
              </button>
              <button
                onClick={() =>
                  setText(
                    "The clinical trial showed promising results for the new cancer treatment, with patients experiencing significant improvement in their condition."
                  )
                }
                className="text-left p-4 bg-green-100 hover:bg-green-200 text-green-800 rounded-lg text-sm transition-all duration-200 hover:shadow-md transform hover:-translate-y-0.5"
              >
                <div className="font-semibold mb-1">Health</div>
                <div className="text-xs opacity-80">Medical research & treatment</div>
              </button>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <p className="text-red-700 text-sm font-medium">{error}</p>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4">
            <button
              onClick={handleClassify}
              disabled={loading || !text.trim()}
              className="flex-1 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 text-white px-8 py-4 rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl disabled:shadow-none transition-all duration-200 transform hover:-translate-y-0.5 disabled:translate-y-0 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center gap-3">
                  <LoadingSpinner size="sm" />
                  <span>Analyzing Text...</span>
                </div>
              ) : (
                <div className="flex items-center justify-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                    />
                  </svg>
                  Classify Text
                </div>
              )}
            </button>

            <button
              onClick={handleClear}
              className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-4 rounded-xl font-semibold transition-all duration-200 hover:shadow-lg transform hover:-translate-y-0.5"
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* Results Section */}
      {result && (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              Classification Results
            </h2>
          </div>

          <div className="p-6 space-y-6">
            {/* Model Information */}
            <div className="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-xl p-4 border border-indigo-200">
              <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <svg className="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                Analysis Details
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div className="bg-white rounded-lg p-3 text-center">
                  <div className="text-gray-600 text-xs">Model</div>
                  <div className="font-semibold text-gray-800 capitalize">
                    {result.model_used ? result.model_used.replace("_", " ") : "Unknown"}
                  </div>
                </div>
                {result.text_length && (
                  <>
                    <div className="bg-white rounded-lg p-3 text-center">
                      <div className="text-gray-600 text-xs">Characters</div>
                      <div className="font-semibold text-gray-800">{result.text_length}</div>
                    </div>
                    <div className="bg-white rounded-lg p-3 text-center">
                      <div className="text-gray-600 text-xs">Processed</div>
                      <div className="font-semibold text-gray-800">{result.processed_text_length}</div>
                    </div>
                  </>
                )}
                <div className="bg-white rounded-lg p-3 text-center">
                  <div className="text-gray-600 text-xs">Confidence</div>
                  <div className={`font-bold text-lg ${getConfidenceColor(result.confidence || 0)}`}>
                    {((result.confidence || 0) * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>

            {/* Predicted Category */}
            <div className="text-center">
              <div className="inline-flex items-center gap-3 bg-gradient-to-r from-gray-50 to-gray-100 rounded-2xl p-6 border-2 border-gray-200">
                <div className="text-sm font-medium text-gray-600">Predicted Category:</div>
                <div
                  className={`px-6 py-3 rounded-xl text-lg font-bold capitalize border-2 shadow-lg ${getCategoryColor(
                    result.predicted_category || "unknown"
                  )}`}
                >
                  {result.predicted_category || "Unknown"}
                </div>
              </div>
            </div>

            {/* Probability Scores */}
            <div className="bg-gray-50 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
                Probability Distribution
              </h3>
              <div className="space-y-4">
                {result.probabilities &&
                  Object.entries(result.probabilities)
                    .sort(([, a], [, b]) => b - a)
                    .map(([category, probability]) => (
                      <div key={category} className="bg-white rounded-lg p-4 shadow-sm">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-3">
                            <div className={`w-4 h-4 rounded-full ${getCategoryColor(category).split(" ")[1]}`}></div>
                            <span className="capitalize font-semibold text-gray-700 text-lg">{category}</span>
                          </div>
                          <span className="font-bold text-gray-800 text-lg">{(probability * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                          <div
                            className={`h-3 rounded-full transition-all duration-500 ease-out ${
                              category === "business"
                                ? "bg-gradient-to-r from-blue-400 to-blue-600"
                                : category === "health"
                                ? "bg-gradient-to-r from-green-400 to-green-600"
                                : "bg-gradient-to-r from-purple-400 to-purple-600"
                            }`}
                            style={{ width: `${Math.max(probability * 100, 2)}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
