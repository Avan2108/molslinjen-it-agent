# Phase 5: Frontend Components

## Overview
Implement the React components for the chat interface, ticket management, FAQ browser, feedback widget, and admin dashboard.

## Prerequisites
- Phase 2 completed (Authentication working)
- Phase 4 completed (Backend APIs functional)
- Tailwind CSS configured

---

## Tasks

### 5.1 Create Shared Components

**Assignee:** Frontend Developer
**Estimated effort:** 4 hours

#### Files to Create:

1. **Create `frontend/src/components/shared/Button.tsx`:**
   ```typescript
   interface ButtonProps {
     variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
     size?: 'sm' | 'md' | 'lg';
     loading?: boolean;
     disabled?: boolean;
     children: React.ReactNode;
     onClick?: () => void;
   }

   export function Button({ variant = 'primary', size = 'md', ... }: ButtonProps) {
     // Implementation with Tailwind classes
   }
   ```

2. **Create `frontend/src/components/shared/Input.tsx`:**
   ```typescript
   interface InputProps {
     label?: string;
     error?: string;
     // ... standard input props
   }
   ```

3. **Create `frontend/src/components/shared/Card.tsx`:**
   ```typescript
   export function Card({ children, className }: CardProps) {
     return (
       <div className={clsx('bg-white rounded-lg shadow p-4', className)}>
         {children}
       </div>
     );
   }
   ```

4. **Create `frontend/src/components/shared/Modal.tsx`:**
   - Accessible modal with focus trap
   - Backdrop click to close
   - Escape key to close

5. **Create `frontend/src/components/shared/Spinner.tsx`:**
   - Loading spinner with sizes
   - Optional loading text

6. **Create `frontend/src/components/shared/Avatar.tsx`:**
   - User avatar with initials fallback

7. **Create `frontend/src/components/shared/Badge.tsx`:**
   - Status badges (open, resolved, etc.)
   - Color variants

8. **Create `frontend/src/components/shared/index.ts`:**
   - Export all shared components

#### Acceptance Criteria:
- [ ] All components are accessible (ARIA)
- [ ] Components support keyboard navigation
- [ ] Components match design system
- [ ] Components are responsive

---

### 5.2 Implement Chat Components

**Assignee:** Frontend Developer
**Estimated effort:** 12 hours

#### Files to Create:

1. **Create `frontend/src/components/chat/ChatWindow.tsx`:**
   ```typescript
   export function ChatWindow() {
     const { messages, isLoading, sendMessage } = useChat();

     return (
       <div className="flex flex-col h-full">
         <ChatHeader />
         <MessageList messages={messages} isLoading={isLoading} />
         <ChatInput onSend={sendMessage} disabled={isLoading} />
       </div>
     );
   }
   ```

2. **Create `frontend/src/components/chat/MessageList.tsx`:**
   ```typescript
   interface MessageListProps {
     messages: Message[];
     isLoading: boolean;
   }

   export function MessageList({ messages, isLoading }: MessageListProps) {
     const messagesEndRef = useRef<HTMLDivElement>(null);

     // Auto-scroll to bottom on new messages
     useEffect(() => {
       messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
     }, [messages]);

     return (
       <div className="flex-1 overflow-y-auto p-4 space-y-4">
         {messages.map((msg, index) => (
           <MessageBubble key={index} message={msg} />
         ))}
         {isLoading && <TypingIndicator />}
         <div ref={messagesEndRef} />
       </div>
     );
   }
   ```

3. **Create `frontend/src/components/chat/MessageBubble.tsx`:**
   ```typescript
   interface MessageBubbleProps {
     message: Message;
   }

   export function MessageBubble({ message }: MessageBubbleProps) {
     const isUser = message.role === MessageRole.USER;

     return (
       <div className={clsx(
         'flex',
         isUser ? 'justify-end' : 'justify-start'
       )}>
         <div className={clsx(
           'max-w-[80%] rounded-lg p-3',
           isUser
             ? 'bg-primary-600 text-white'
             : 'bg-gray-100 text-gray-900'
         )}>
           <p className="whitespace-pre-wrap">{message.content}</p>

           {message.sources && message.sources.length > 0 && (
             <SourceList sources={message.sources} />
           )}

           {!isUser && (
             <FeedbackButtons messageIndex={...} />
           )}
         </div>
       </div>
     );
   }
   ```

4. **Create `frontend/src/components/chat/ChatInput.tsx`:**
   ```typescript
   interface ChatInputProps {
     onSend: (message: string) => void;
     disabled?: boolean;
   }

   export function ChatInput({ onSend, disabled }: ChatInputProps) {
     const [input, setInput] = useState('');
     const { t } = useTranslation();

     const handleSubmit = (e: FormEvent) => {
       e.preventDefault();
       if (input.trim() && !disabled) {
         onSend(input.trim());
         setInput('');
       }
     };

     return (
       <form onSubmit={handleSubmit} className="border-t p-4">
         <div className="flex gap-2">
           <input
             type="text"
             value={input}
             onChange={(e) => setInput(e.target.value)}
             placeholder={t('chat.placeholder')}
             disabled={disabled}
             className="flex-1 rounded-lg border p-2 focus:ring-2 focus:ring-primary-500"
             maxLength={4000}
           />
           <Button type="submit" disabled={disabled || !input.trim()}>
             {t('chat.send')}
           </Button>
         </div>
       </form>
     );
   }
   ```

5. **Create `frontend/src/components/chat/SourceList.tsx`:**
   ```typescript
   // Display sources with links
   // Expandable/collapsible
   ```

6. **Create `frontend/src/components/chat/TypingIndicator.tsx`:**
   ```typescript
   // Animated dots or pulsing indicator
   ```

7. **Create `frontend/src/components/chat/ChatHeader.tsx`:**
   ```typescript
   // Title, new conversation button, history toggle
   ```

8. **Create `frontend/src/components/chat/ChatHistory.tsx`:**
   ```typescript
   // Sidebar with previous conversations
   // Click to load conversation
   ```

9. **Create `frontend/src/hooks/useChat.ts`:**
   ```typescript
   export function useChat() {
     const [messages, setMessages] = useState<Message[]>([]);
     const [sessionId, setSessionId] = useState<string | null>(null);
     const [isLoading, setIsLoading] = useState(false);

     const sendMessage = async (content: string) => {
       setIsLoading(true);

       // Add user message immediately
       const userMessage: Message = {
         role: MessageRole.USER,
         content,
         timestamp: new Date().toISOString(),
       };
       setMessages(prev => [...prev, userMessage]);

       try {
         const response = await post<ChatResponse>('/chat', {
           message: content,
           session_id: sessionId,
         });

         setSessionId(response.session_id);

         const agentMessage: Message = {
           role: MessageRole.AGENT,
           content: response.message,
           timestamp: new Date().toISOString(),
           sources: response.sources,
         };
         setMessages(prev => [...prev, agentMessage]);
       } catch (error) {
         // Handle error - show error message
       } finally {
         setIsLoading(false);
       }
     };

     return { messages, isLoading, sendMessage, sessionId };
   }
   ```

#### Acceptance Criteria:
- [ ] Messages display correctly (user vs agent styling)
- [ ] Auto-scroll to new messages
- [ ] Loading indicator while waiting for response
- [ ] Sources displayed with links
- [ ] Input validation (max length, not empty)
- [ ] Enter to send, Shift+Enter for newline
- [ ] Accessible (screen reader, keyboard nav)
- [ ] Responsive on mobile

#### Testing:
```typescript
// frontend/src/components/chat/__tests__/ChatInput.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInput } from '../ChatInput';

test('calls onSend when form submitted', () => {
  const onSend = vi.fn();
  render(<ChatInput onSend={onSend} />);

  const input = screen.getByPlaceholderText(/type your question/i);
  fireEvent.change(input, { target: { value: 'Hello' } });
  fireEvent.submit(input.closest('form')!);

  expect(onSend).toHaveBeenCalledWith('Hello');
});

test('does not submit empty messages', () => {
  const onSend = vi.fn();
  render(<ChatInput onSend={onSend} />);

  fireEvent.submit(screen.getByRole('button'));

  expect(onSend).not.toHaveBeenCalled();
});
```

---

### 5.3 Implement Feedback Components

**Assignee:** Frontend Developer
**Estimated effort:** 4 hours

#### Files to Create:

1. **Create `frontend/src/components/chat/FeedbackButtons.tsx`:**
   ```typescript
   interface FeedbackButtonsProps {
     sessionId: string;
     messageIndex: number;
   }

   export function FeedbackButtons({ sessionId, messageIndex }: FeedbackButtonsProps) {
     const [submitted, setSubmitted] = useState(false);
     const [showModal, setShowModal] = useState(false);
     const { t } = useTranslation();

     const handleFeedback = async (rating: FeedbackRating) => {
       if (rating === FeedbackRating.DOWN) {
         setShowModal(true);
       } else {
         await submitFeedback({ sessionId, messageIndex, rating });
         setSubmitted(true);
       }
     };

     if (submitted) {
       return <span className="text-sm text-gray-500">{t('chat.feedbackThanks')}</span>;
     }

     return (
       <>
         <div className="flex gap-2 mt-2">
           <button onClick={() => handleFeedback(FeedbackRating.UP)}>👍</button>
           <button onClick={() => handleFeedback(FeedbackRating.DOWN)}>👎</button>
         </div>

         {showModal && (
           <FeedbackModal
             sessionId={sessionId}
             messageIndex={messageIndex}
             onClose={() => setShowModal(false)}
             onSubmit={() => setSubmitted(true)}
           />
         )}
       </>
     );
   }
   ```

2. **Create `frontend/src/components/chat/FeedbackModal.tsx`:**
   ```typescript
   // Modal with:
   // - Reason selection (too_long, wrong_answer, did_not_help)
   // - Optional comment text area
   // - Submit button
   ```

#### Acceptance Criteria:
- [ ] Thumbs up/down buttons on agent messages
- [ ] Negative feedback opens modal
- [ ] Reason selection required for negative
- [ ] Optional comment field
- [ ] Success state after submission

---

### 5.4 Implement Ticket Components

**Assignee:** Frontend Developer
**Estimated effort:** 8 hours

#### Files to Create:

1. **Create `frontend/src/components/tickets/TicketList.tsx`:**
   ```typescript
   export function TicketList() {
     const { tickets, isLoading } = useTickets();

     if (isLoading) return <Spinner />;

     if (tickets.length === 0) {
       return <EmptyState message={t('tickets.noTickets')} />;
     }

     return (
       <div className="space-y-4">
         {tickets.map(ticket => (
           <TicketCard key={ticket.id} ticket={ticket} />
         ))}
       </div>
     );
   }
   ```

2. **Create `frontend/src/components/tickets/TicketCard.tsx`:**
   ```typescript
   // Card showing:
   // - Subject
   // - Status badge
   // - Priority
   // - Created date
   // - Click to expand/navigate
   ```

3. **Create `frontend/src/components/tickets/TicketDetail.tsx`:**
   ```typescript
   // Full ticket view:
   // - All ticket fields
   // - Notes/comments
   // - Add note form
   ```

4. **Create `frontend/src/components/tickets/CreateTicketForm.tsx`:**
   ```typescript
   // Form for manual ticket creation:
   // - Subject (required)
   // - Description (required)
   // - Priority dropdown
   // - Submit button
   ```

5. **Create `frontend/src/hooks/useTickets.ts`:**
   ```typescript
   export function useTickets(statusFilter?: string) {
     // Fetch and manage tickets
   }
   ```

#### Acceptance Criteria:
- [ ] List tickets with status/priority badges
- [ ] Filter by status
- [ ] View ticket details
- [ ] Add notes to tickets
- [ ] Create new ticket
- [ ] Form validation

---

### 5.5 Implement FAQ Components

**Assignee:** Frontend Developer
**Estimated effort:** 4 hours

#### Files to Create:

1. **Create `frontend/src/components/faqs/FAQBrowser.tsx`:**
   ```typescript
   export function FAQBrowser() {
     const [category, setCategory] = useState<string | null>(null);
     const [search, setSearch] = useState('');
     const { faqs, categories } = useFAQs(category);

     const filtered = faqs.filter(faq =>
       faq.question.toLowerCase().includes(search.toLowerCase())
     );

     return (
       <div>
         <SearchInput value={search} onChange={setSearch} />
         <CategoryFilter categories={categories} selected={category} onSelect={setCategory} />
         <FAQList faqs={filtered} />
       </div>
     );
   }
   ```

2. **Create `frontend/src/components/faqs/FAQItem.tsx`:**
   ```typescript
   // Expandable FAQ item
   // Question as header
   // Answer when expanded
   // Helpful? buttons
   ```

3. **Create `frontend/src/components/faqs/FAQList.tsx`:**
   - List of FAQItem components
   - Empty state when no results

---

### 5.6 Implement Admin Components

**Assignee:** Frontend Developer
**Estimated effort:** 10 hours

#### Files to Create:

1. **Create `frontend/src/components/admin/AdminLayout.tsx`:**
   ```typescript
   // Admin page layout with:
   // - Sidebar navigation
   // - Header with user info
   // - Main content area
   ```

2. **Create `frontend/src/components/admin/AnalyticsDashboard.tsx`:**
   ```typescript
   // Dashboard showing:
   // - Key metrics cards (conversations, users, resolution rate)
   // - Intent breakdown chart
   // - Top queries list
   // - Trend graphs
   ```

3. **Create `frontend/src/components/admin/KnowledgeGaps.tsx`:**
   ```typescript
   // Table of knowledge gaps:
   // - Query
   // - Occurrences
   // - Intent
   // - Actions (mark resolved)
   ```

4. **Create `frontend/src/components/admin/FAQManager.tsx`:**
   ```typescript
   // CRUD interface for FAQs:
   // - List with edit/delete
   // - Create form
   // - Reorder functionality
   ```

5. **Create `frontend/src/components/admin/ReindexPanel.tsx`:**
   ```typescript
   // Trigger reindex
   // Show progress
   // Display status
   ```

6. **Create `frontend/src/hooks/useAnalytics.ts`:**
   - Fetch analytics data
   - Date range selection

#### Acceptance Criteria:
- [ ] Admin-only route protection
- [ ] Analytics dashboard with real data
- [ ] Knowledge gaps table with actions
- [ ] FAQ CRUD operations
- [ ] Reindex trigger and status
- [ ] Activity logs viewer

---

### 5.7 Create Pages and Routing

**Assignee:** Frontend Developer
**Estimated effort:** 4 hours

#### Files to Create:

1. **Create `frontend/src/pages/ChatPage.tsx`:**
   ```typescript
   export function ChatPage() {
     return (
       <Layout>
         <ChatWindow />
       </Layout>
     );
   }
   ```

2. **Create `frontend/src/pages/TicketsPage.tsx`**

3. **Create `frontend/src/pages/FAQsPage.tsx`**

4. **Create `frontend/src/pages/AdminPage.tsx`:**
   ```typescript
   export function AdminPage() {
     // Protected route - admin only
     return (
       <AdminLayout>
         <Outlet />
       </AdminLayout>
     );
   }
   ```

5. **Update `frontend/src/App.tsx`:**
   ```typescript
   import { BrowserRouter, Routes, Route } from 'react-router-dom';

   function App() {
     return (
       <AuthProvider>
         <BrowserRouter>
           <Routes>
             <Route path="/" element={<ChatPage />} />
             <Route path="/tickets" element={<ProtectedRoute><TicketsPage /></ProtectedRoute>} />
             <Route path="/faqs" element={<FAQsPage />} />
             <Route path="/admin" element={<AdminRoute><AdminPage /></AdminRoute>}>
               <Route index element={<AnalyticsDashboard />} />
               <Route path="gaps" element={<KnowledgeGaps />} />
               <Route path="faqs" element={<FAQManager />} />
             </Route>
           </Routes>
         </BrowserRouter>
       </AuthProvider>
     );
   }
   ```

---

## Component Testing Checklist

For each component:
- [ ] Unit tests for logic
- [ ] Accessibility audit (axe-core)
- [ ] Responsive testing (mobile, tablet, desktop)
- [ ] Keyboard navigation
- [ ] Screen reader testing
- [ ] Loading states
- [ ] Error states
- [ ] Empty states

---

## Definition of Done

- [ ] All components implemented per specs
- [ ] Components fully tested
- [ ] Accessibility audit passed
- [ ] Responsive on all breakpoints
- [ ] i18n strings used (no hardcoded text)
- [ ] Loading/error states handled
- [ ] Design review passed
- [ ] Documentation updated
