// ---------------------------------------------------------------------------
// API client — all calls go through the FastAPI backend.
//
// Base URL is configured via the VITE_API_URL environment variable.
// In development, create frontend/.env.local:
//   VITE_API_URL=http://localhost:8000
//
// In production (Azure App Service) set it as an application setting:
//   VITE_API_URL=https://<your-backend-app>.azurewebsites.net
//
// All endpoints are prefixed with /api/v1 to match the FastAPI router setup.
// ---------------------------------------------------------------------------

const BASE = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1`;

/**
 * Send a chat message.
 * POST /api/v1/chat
 */
export async function sendMessage(sessionId, message, language, images = []) {
  const res = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      language,
      images,
    }),
  });
  return res.json();
}

/**
 * Submit thumbs up/down feedback on a message.
 * POST /api/v1/feedback
 */
export async function sendFeedback(sessionId, messageId, rating) {
  await fetch(`${BASE}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message_id: messageId, rating }),
  });
}

/**
 * Ask the backend to summarize the conversation into a ticket title + description.
 * POST /api/v1/chat/summarize
 * Returns { title, description }
 */
export async function summarizeTicket(sessionId, language = 'en') {
  const res = await fetch(`${BASE}/chat/summarize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, language }),
  });
  return res.json();
}

/**
 * Create a support ticket.
 * POST /api/v1/tickets
 */
export async function createTicket(sessionId, summary, description, userName, priority = 'medium') {
  const res = await fetch(`${BASE}/tickets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id:  sessionId,
      summary,
      description,
      user_name:   userName,
      priority,
    }),
  });
  return res.json();
}

/**
 * Get a specific ticket by ID.
 * GET /api/v1/tickets/{ticketId}
 */
export async function getTicket(ticketId) {
  const res = await fetch(`${BASE}/tickets/${ticketId}`);
  return res.json();
}

/**
 * Get suggested questions (FAQs) for the given language.
 * GET /api/v1/faqs?language={language}
 */
export async function getSuggestions(language) {
  const res = await fetch(`${BASE}/faqs?language=${language}`);
  const data = await res.json();
  return data.suggestions ?? data;
}

/**
 * Get admin analytics dashboard data.
 * GET /api/v1/admin/analytics
 */
export async function getAdminStats() {
  const res = await fetch(`${BASE}/admin/analytics`);
  return res.json();
}

/**
 * Get conversation logs for admin dashboard.
 * GET /api/v1/admin/conversations  (maps to chat sessions)
 */
export async function getAdminConversations() {
  const res = await fetch(`${BASE}/chat/sessions`);
  return res.json();
}

/**
 * Get all tickets for admin dashboard.
 * GET /api/v1/tickets (admin sees all)
 */
export async function getAdminTickets() {
  const res = await fetch(`${BASE}/tickets`);
  return res.json();
}
