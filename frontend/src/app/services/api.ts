// API service for making requests to the backend
export const API_BASE_URL = "http://127.0.0.1:8000";

export interface Publication {
  title: string;
  link: string;
  authors: string[];
  published_date: string;
  abstract: string;
  score: number;
}

export interface SearchResponse {
  results: Publication[];
  total: number;
  page: number;
  size: number;
  total_pages: number;
}

export class ApiService {
  static async searchPublications(query: string = "", page: number = 1, size: number = 10): Promise<SearchResponse> {
    const params = new URLSearchParams({
      query,
      page: page.toString(),
      size: size.toString(),
    });

    const response = await fetch(`${API_BASE_URL}/search?${params}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  static async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/`);
      return response.ok;
    } catch {
      return false;
    }
  }
}
