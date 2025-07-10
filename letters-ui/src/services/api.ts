import {
  LetterRequest,
  LetterResponse,
  LetterSuggestion,
  ValidationResult,
  HealthStatus,
} from '../types';

// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:7071/api';

// Helper function for API requests
async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `API request failed: ${response.statusText}`);
  }

  return response.json();
}

// API service class
export class ApiService {
  // Health check
  static async checkHealth(): Promise<HealthStatus> {
    return apiRequest<HealthStatus>('/health');
  }

  // Generate letter
  static async generateLetter(request: LetterRequest): Promise<LetterResponse> {
    return apiRequest<LetterResponse>('/draft-letter', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Suggest letter type
  static async suggestLetterType(prompt: string): Promise<LetterSuggestion> {
    return apiRequest<LetterSuggestion>('/suggest-letter-type', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });
  }

  // Validate letter
  static async validateLetter(
    letterContent: string,
    letterType: string
  ): Promise<ValidationResult> {
    return apiRequest<ValidationResult>('/validate-letter', {
      method: 'POST',
      body: JSON.stringify({
        letter_content: letterContent,
        letter_type: letterType,
      }),
    });
  }

  // Get letter history (placeholder for future implementation)
  static async getLetterHistory(userId: string): Promise<LetterResponse[]> {
    // TODO: Implement when backend supports user-specific history
    return apiRequest<LetterResponse[]>(`/letters?userId=${userId}`);
  }

  // Get analytics data (placeholder for future implementation)
  static async getAnalytics(userId: string): Promise<any> {
    // TODO: Implement when backend supports analytics
    return apiRequest<any>(`/analytics?userId=${userId}`);
  }
}

// Export individual functions for convenience
export const {
  checkHealth,
  generateLetter,
  suggestLetterType,
  validateLetter,
  getLetterHistory,
  getAnalytics,
} = ApiService;