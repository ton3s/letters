// User and Authentication Types
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
  avatar?: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Letter Types
export type LetterType = 
  | 'claim_denial'
  | 'claim_approval'
  | 'policy_renewal'
  | 'coverage_change'
  | 'premium_increase'
  | 'cancellation'
  | 'welcome'
  | 'general';

export interface CustomerInfo {
  name: string;
  policy_number: string;
  address?: string;
  phone?: string;
  email?: string;
  agent_name?: string;
}

export interface LetterRequest {
  customer_info: CustomerInfo;
  letter_type: LetterType;
  user_prompt: string;
  include_conversation?: boolean;
}

export interface ApprovalStatus {
  overall_approved: boolean;
  compliance_approved: boolean;
  writer_approved: boolean;
  customer_service_approved: boolean;
  status: string;
}

export interface ConversationEntry {
  round: number;
  agent: string;
  message: string;
  timestamp: string;
}

export interface LetterResponse {
  letter_content: string;
  approval_status: ApprovalStatus;
  total_rounds: number;
  document_id?: string;
  timestamp?: string;
  agent_conversation?: ConversationEntry[];
}

export interface LetterSuggestion {
  suggested_type: LetterType;
  confidence: number;
  reasoning: string;
  alternative_types?: LetterType[];
}

export interface ValidationResult {
  is_valid: boolean;
  compliance_issues: string[];
  suggestions: string[];
  compliance_score: number;
  validated_by: string;
  timestamp: string;
}

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  service: string;
  version: string;
  cosmos_db?: string;
  endpoints: string[];
}

// UI State Types
export interface ThemeState {
  mode: 'light' | 'dark';
}