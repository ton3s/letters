import {
  LetterRequest,
  LetterResponse,
  LetterSuggestion,
  ValidationResult,
  HealthStatus,
} from '../types';
import { getAuthHeader } from '../utils/apiAuth';

// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:7071/api';

// Check if we're using API Management (for additional headers if needed)
const isUsingAPIM = API_BASE_URL.includes('azure-api.net');

// Helper function for API requests
async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  // Get authentication header
  const authHeader = await getAuthHeader();
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...authHeader,
      // Add subscription key header if using APIM and configured
      ...(isUsingAPIM && process.env.REACT_APP_APIM_SUBSCRIPTION_KEY ? {
        'Ocp-Apim-Subscription-Key': process.env.REACT_APP_APIM_SUBSCRIPTION_KEY
      } : {}),
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

}

// Export individual functions for convenience
export const {
  checkHealth,
  generateLetter,
  suggestLetterType,
  validateLetter,
} = ApiService;