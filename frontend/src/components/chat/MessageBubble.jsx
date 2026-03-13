import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  FileText, AlertTriangle, Phone, Ticket,
  ThumbsUp, ThumbsDown, Copy, Check
} from 'lucide-react';
import styles from './ChatWindow.module.css';

export default function MessageBubble({
  msg, userName, lang, tr,
  feedback, summarizing, copiedMsgId, copied,
  onFeedback, onCopy, onOpenTicket, onOpenCreate, onContactIT,
}) {
  return (
    <div className={`${styles.msgRow} ${msg.role === 'user' ? styles.userRow : styles.botRow}`}>
      {msg.role === 'bot' && <div className={styles.avatar}>IT</div>}
      {msg.role === 'user' && (
        <div className={styles.avatarUser}>{userName[0].toUpperCase()}</div>
      )}

      <div className={styles.msgContent}>
        {/* Attached images above user bubble */}
        {msg.role === 'user' && msg.images?.length > 0 && (
          <div className={styles.attachedImages}>
            {msg.images.map((src, i) => (
              <img key={i} src={src} alt="attachment" className={styles.attachedThumb} />
            ))}
          </div>
        )}

        <div className={`${styles.bubble} ${msg.role === 'user' ? styles.userBubble : styles.botBubble}`}>
          {msg.role === 'bot' ? (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
          ) : (
            msg.text
          )}
        </div>

        {/* Sources */}
        {msg.role === 'bot' && msg.sources?.length > 0 && (
          <div className={styles.sources}>
            <FileText size={11} />
            {tr.sources}: {msg.sources.join(', ')}
          </div>
        )}

        {/* Escalation card */}
        {msg.role === 'bot' && msg.escalate && !msg.ticketCreated && (
          <div className={styles.escalateCard}>
            <div className={styles.escalateHeader}>
              <AlertTriangle size={15} />
              {tr.escalateTitle}
            </div>
            <p className={styles.escalateMsg}>{tr.escalateMsg}</p>
            <div className={styles.escalateBtns}>
              <button
                className={styles.escalatePrimary}
                onClick={() => onOpenCreate(msg.id)}
                disabled={summarizing === msg.id}
              >
                <Ticket size={13} />
                {summarizing === msg.id
                  ? (lang === 'da' ? 'Genererer...' : 'Generating...')
                  : tr.createTicket}
              </button>
              <button className={styles.escalateSecondary} onClick={() => onContactIT(tr)}>
                <Phone size={13} />
                {copied ? (lang === 'da' ? 'Kopieret!' : 'Copied!') : tr.contactIT}
              </button>
            </div>
          </div>
        )}

        {/* Ticket created confirmation */}
        {msg.role === 'bot' && msg.ticketCreated && (
          <div
            className={styles.ticketConfirm}
            onClick={() => onOpenTicket(msg.ticketCreated)}
            title="Click to view details"
          >
            <Ticket size={13} />
            {tr.ticketCreated}: <strong>{msg.ticketCreated.ticket_id}</strong>
            &nbsp;·&nbsp;{tr.ticketStatus}: {msg.ticketCreated.status}
            &nbsp;·&nbsp;{lang === 'da' ? 'Ventetid' : 'Est. wait'}: {msg.ticketCreated.estimated_wait}
            &nbsp;·&nbsp;<span style={{ textDecoration: 'underline', cursor: 'pointer' }}>
              {lang === 'da' ? 'Vis detaljer' : 'View details'}
            </span>
          </div>
        )}

        {/* Feedback + copy row */}
        {msg.role === 'bot' && (
          <div className={styles.feedbackRow}>
            <button
              className={`${styles.feedbackBtn} ${feedback[msg.id] === 'up' ? styles.feedbackActive : ''}`}
              onClick={() => onFeedback(msg.id, 'up')}
              title={tr.thumbsUpTitle}
            >
              <ThumbsUp size={13} />
            </button>
            <button
              className={`${styles.feedbackBtn} ${feedback[msg.id] === 'down' ? styles.feedbackActiveDown : ''}`}
              onClick={() => onFeedback(msg.id, 'down')}
              title={tr.thumbsDownTitle}
            >
              <ThumbsDown size={13} />
            </button>
            <button
              className={`${styles.copyBtn} ${copiedMsgId === msg.id ? styles.copyBtnDone : ''}`}
              onClick={() => onCopy(msg.id, msg.text)}
              title={lang === 'da' ? 'Kopiér svar' : 'Copy response'}
            >
              {copiedMsgId === msg.id ? <Check size={13} /> : <Copy size={13} />}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
