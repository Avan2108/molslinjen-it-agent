/**
 * TypeScript enums matching backend definitions
 */

export enum Intent {
  KNOWLEDGE_QUERY = 'knowledge_query',
  TICKET_CREATE = 'ticket_create',
  TICKET_STATUS = 'ticket_status',
  DIAGNOSTICS = 'diagnostics',
  ONBOARDING = 'onboarding',
  ADMIN = 'admin',
  OFF_TOPIC = 'off_topic',
  UNCLEAR = 'unclear',
  FEEDBACK = 'feedback',
}

export enum MessageRole {
  USER = 'user',
  AGENT = 'agent',
}

export enum TicketStatus {
  OPEN = 'open',
  IN_PROGRESS = 'in_progress',
  RESOLVED = 'resolved',
  CLOSED = 'closed',
}

export enum TicketPriority {
  URGENT = 1,
  HIGH = 2,
  MEDIUM = 3,
  LOW = 4,
}

export enum FeedbackRating {
  UP = 'up',
  DOWN = 'down',
}

export enum FeedbackReason {
  TOO_LONG = 'too_long',
  WRONG_ANSWER = 'wrong_answer',
  DID_NOT_HELP = 'did_not_help',
}

export enum Locale {
  AUTO = 'auto',
  EN = 'en',
  DA = 'da',
  SV = 'sv',
}

export enum UserRole {
  EMPLOYEE = 'Employee',
  IT_ADMIN = 'ITAdmin',
}
