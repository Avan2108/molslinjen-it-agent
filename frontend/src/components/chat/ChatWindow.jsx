import { useState } from 'react';
import { Globe, LayoutDashboard, Plus, Phone, Mail, Clock, Search } from 'lucide-react';
import { Moon, Sun } from 'lucide-react';
import { useChat } from '../../hooks/useChat';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import TypingIndicator from './TypingIndicator';
import TicketModal from '../tickets/TicketModal';
import CreateTicketModal from '../tickets/CreateTicketModal';
import styles from './ChatWindow.module.css';

const molsIcon = '/MolsLogo.png';

export default function ChatWindow({
  lang, tr, userName, userRole, darkMode,
  onToggleLang, onToggleDark, onOpenAdmin,
}) {
  const isAdmin = userRole === 'admin';
  const [input, setInput] = useState('');

  const chat = useChat({ lang, userName });

  const showSuggestions = chat.messages.length === 0;

  return (
    <div className={styles.layout}>
      {/* View ticket modal */}
      {chat.modalTicket && (
        <TicketModal
          ticket={chat.modalTicket}
          tr={tr}
          lang={lang}
          onClose={() => chat.setModalTicket(null)}
        />
      )}

      {/* Create ticket modal */}
      {chat.pendingTicket && (
        <CreateTicketModal
          defaultTitle={chat.pendingTicket.defaultTitle}
          defaultDescription={chat.pendingTicket.defaultDescription}
          lang={lang}
          tr={tr}
          onSubmit={chat.handleCreateTicket}
          onClose={() => chat.setPendingTicket(null)}
        />
      )}

      {/* ── Sidebar ── */}
      <aside className={styles.sidebar}>
        <div className={styles.sidebarLogo}>
          <img src={molsIcon} className={styles.sidebarLogoIcon} alt="Molslinjen" />
          <div>
            <div className={styles.sidebarLogoTitle}>{tr.title}</div>
            <div className={styles.sidebarLogoSub}>Molslinjen IT Support</div>
          </div>
        </div>

        <button className={styles.newChatBtn} onClick={chat.startNewChat}>
          <Plus size={16} /> {tr.newChat}
        </button>

        {/* Ticket lookup */}
        <div className={styles.sidebarSection}>
          <div className={styles.sidebarSectionTitle}>{tr.checkTicket}</div>
          <form onSubmit={chat.handleTicketLookup} className={styles.ticketForm}>
            <input
              className={styles.ticketInput}
              placeholder="INC-1001"
              value={chat.ticketLookup}
              onChange={e => chat.setTicketLookup(e.target.value)}
            />
            <button type="submit" className={styles.ticketSearchBtn}>
              <Search size={14} />
            </button>
          </form>
          {chat.ticketResult && !chat.ticketResult.error && (
            <div
              className={styles.ticketCard}
              onClick={() => chat.setModalTicket(chat.ticketResult)}
              title="Click to view details"
            >
              <div className={styles.ticketCardTop}>
                <div className={styles.ticketCardId}>{chat.ticketResult.ticket_id}</div>
                <span className={`${styles.ticketBadge} ${styles[chat.ticketResult.status?.toLowerCase().replace(' ', '')]}`}>
                  {chat.ticketResult.status}
                </span>
              </div>
              <div className={styles.ticketCardSummary}>{chat.ticketResult.summary}</div>
              <div className={styles.ticketCardHint}>
                {lang === 'da' ? 'Klik for detaljer' : 'Click to view details'} →
              </div>
            </div>
          )}
          {chat.ticketResult?.error && (
            <div className={styles.ticketNotFound}>{chat.ticketResult.error}</div>
          )}
        </div>

        <div className={styles.sidebarBottom}>
          {isAdmin && (
            <div className={styles.sidebarContactBlock}>
              <div className={styles.sidebarSectionTitle}>
                {lang === 'en' ? 'Admin' : 'Administration'}
              </div>
              <button className={styles.sidebarBtn} onClick={onOpenAdmin}>
                <LayoutDashboard size={14} /> {tr.adminDashboard}
              </button>
            </div>
          )}

          <div className={styles.sidebarContactBlock}>
            <div className={styles.sidebarSectionTitle}>
              {lang === 'en' ? 'Preferences' : 'Indstillinger'}
            </div>
            <button className={styles.sidebarBtn} onClick={onToggleLang}>
              <Globe size={14} />
              {lang === 'en' ? 'Switch to Danish' : 'Switch to English'}
            </button>
            <button className={styles.sidebarBtn} onClick={onToggleDark}>
              {darkMode ? <Sun size={14} /> : <Moon size={14} />}
              {darkMode
                ? (lang === 'da' ? 'Lyst tema' : 'Light mode')
                : (lang === 'da' ? 'Mørkt tema' : 'Dark mode')}
            </button>
          </div>

          <div className={styles.sidebarContactBlock}>
            <div className={styles.sidebarSectionTitle}>IT Support</div>
            <div className={styles.contactItem}><Phone size={13} /> {tr.itPhone}</div>
            <div className={styles.contactItem}><Mail size={13} /> {tr.itEmail}</div>
            <div className={styles.contactItem}><Clock size={13} /> {tr.itHours}</div>
          </div>
        </div>
      </aside>

      {/* ── Main chat area ── */}
      <main className={styles.main}>
        <div className={styles.messages}>
          {showSuggestions && (
            <div className={styles.welcomeArea}>
              <div className={styles.welcomeTitle}>
                {lang === 'da' ? `Hej ${userName}!` : `Hi ${userName}!`}
              </div>
              <div className={styles.welcomeSub}>
                {lang === 'da'
                  ? 'Hvad kan jeg hjælpe dig med i dag?'
                  : 'What can I help you with today?'}
              </div>
              <div className={styles.suggestionsGrid}>
                {chat.suggestions.map((s, i) => (
                  <button key={i} className={styles.suggestionChip} onClick={() => chat.sendMsg(s)}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {chat.messages.map(msg => (
            <MessageBubble
              key={msg.id}
              msg={msg}
              userName={userName}
              lang={lang}
              tr={tr}
              feedback={chat.feedback}
              summarizing={chat.summarizing}
              copiedMsgId={chat.copiedMsgId}
              copied={chat.copied}
              onFeedback={chat.handleFeedback}
              onCopy={chat.copyMessage}
              onOpenTicket={chat.setModalTicket}
              onOpenCreate={chat.openCreateTicketModal}
              onContactIT={chat.handleContactIT}
            />
          ))}

          {chat.typing && <TypingIndicator />}
          <div ref={chat.bottomRef} />
        </div>

        <ChatInput
          input={input}
          setInput={setInput}
          typing={chat.typing}
          pendingImages={chat.pendingImages}
          onSend={chat.sendMsg}
          onImageFiles={chat.handleImageFiles}
          onRemoveImage={chat.removeImage}
          lang={lang}
          tr={tr}
          imageInputRef={chat.imageInputRef}
          inputRef={chat.inputRef}
        />
      </main>
    </div>
  );
}
