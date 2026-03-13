/**
 * TypeScript type definitions for the Molslinjen IT Support Agent
 */

export * from './enums';

import {
  FeedbackRating,
  FeedbackReason,
  Intent,
  Locale,
  MessageRole,
  TicketPriority,
  TicketStatus,
  UserRole,
} from './enums';

// ============================================================================
// Chat Types
// ============================================================================

export interface Source {
  title: string;
  url?: string;
  snippet?: string;
  confidence: number;
}

export interface Message {
  role: MessageRole;
  content: string;
  timestamp: string;
  sources?: Source[];
  metadata?: Record<string, unknown>;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  locale?: Locale;
  context?: Record<string, unknown>;
}

export interface ChatResponse {
  session_id: string;
  message: string;
  sources: Source[];
  intent: Intent;
  confidence: number;
  requires_action: boolean;
  action_type?: string;
  action_data?: Record<string, unknown>;
  locale: Locale;
}

export interface ChatSession {
  session_id: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
  locale: Locale;
  is_escalated: boolean;
  ticket_id?: number;
}

// ============================================================================
// Ticket Types
// ============================================================================

export interface TicketNote {
  id: number;
  body: string;
  created_at: string;
  user_id: number;
  is_private: boolean;
}

export interface Ticket {
  id: number;
  subject: string;
  description: string;
  status: TicketStatus;
  priority: TicketPriority;
  requester_id: number;
  requester_email?: string;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
  closed_at?: string;
  notes: TicketNote[];
}

export interface CreateTicketRequest {
  subject: string;
  description: string;
  priority?: TicketPriority;
  custom_fields?: Record<string, unknown>;
  session_id?: string;
}

// ============================================================================
// FAQ Types
// ============================================================================

export interface FAQ {
  id: string;
  question: string;
  answer: string;
  category: string;
  locale: Locale;
  order: number;
  is_active: boolean;
}

export interface FAQCategory {
  id: string;
  name: string;
  icon?: string;
  faqs: FAQ[];
}

// ============================================================================
// Feedback Types
// ============================================================================

export interface FeedbackRequest {
  session_id: string;
  message_index: number;
  rating: FeedbackRating;
  reason?: FeedbackReason;
  comment?: string;
}

export interface FeedbackResponse {
  success: boolean;
  feedback_id: string;
}

// ============================================================================
// User Types
// ============================================================================

export interface UserInfo {
  oid: string;
  email: string;
  name: string;
  preferred_username: string;
  roles: UserRole[];
  department?: string;
  job_title?: string;
}

// ============================================================================
// Admin Types
// ============================================================================

export interface GapEntry {
  id: string;
  query: string;
  intent: Intent;
  occurrences: number;
  first_seen: string;
  last_seen: string;
  sample_session_ids: string[];
  resolved: boolean;
  resolved_at?: string;
  resolved_by?: string;
}

export interface IntentMetrics {
  intent: Intent;
  count: number;
  avg_confidence: number;
  escalation_rate: number;
}

export interface AnalyticsData {
  period_start: string;
  period_end: string;
  total_conversations: number;
  total_messages: number;
  unique_users: number;
  avg_messages_per_session: number;
  resolution_rate: number;
  escalation_rate: number;
  avg_response_time_ms: number;
  intent_breakdown: IntentMetrics[];
  satisfaction_score?: number;
  top_queries: string[];
  knowledge_gaps: GapEntry[];
}

export interface ReindexStatus {
  is_running: boolean;
  started_at?: string;
  completed_at?: string;
  documents_processed: number;
  documents_total: number;
  errors: string[];
  last_error?: string;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiError {
  detail: string;
  status_code?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}
