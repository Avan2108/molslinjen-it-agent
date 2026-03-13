import { useEffect } from 'react';
import { X, Ticket, Clock, User, FileText, CheckCircle } from 'lucide-react';
import styles from './TicketModal.module.css';

export default function TicketModal({ ticket, tr, lang, onClose }) {
  // Close on Escape key
  useEffect(() => {
    function onKey(e) { if (e.key === 'Escape') onClose(); }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  const statusColor = {
    Open:          { bg: '#e3f2fd', color: '#1565c0' },
    'In Progress': { bg: '#fff3e0', color: '#e65100' },
    Pending:       { bg: '#fce4ec', color: '#c62828' },
    Resolved:      { bg: '#e8f5e9', color: '#2e7d32' },
  }[ticket.status] || { bg: '#f1f3f4', color: '#5f6368' };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerLeft}>
            <div className={styles.headerIcon}><Ticket size={18} /></div>
            <div>
              <div className={styles.ticketId}>{ticket.ticket_id}</div>
              <div className={styles.headerSub}>Support Ticket</div>
            </div>
          </div>
          <button className={styles.closeBtn} onClick={onClose}><X size={18} /></button>
        </div>

        {/* Status banner */}
        <div
          className={styles.statusBanner}
          style={{ background: statusColor.bg, color: statusColor.color }}
        >
          <CheckCircle size={15} />
          <span>{tr.ticketStatus}: <strong>{ticket.status}</strong></span>
          {ticket.estimated_wait && (
            <span className={styles.waitTime}>
              <Clock size={13} />
              {lang === 'da' ? 'Forventet ventetid' : 'Est. wait'}: {ticket.estimated_wait}
            </span>
          )}
        </div>

        {/* Details grid */}
        <div className={styles.details}>
          <div className={styles.detailRow}>
            <div className={styles.detailLabel}>
              <FileText size={13} /> {tr.ticketSummary}
            </div>
            <div className={styles.detailValue}>{ticket.summary}</div>
          </div>

          <div className={styles.detailRow}>
            <div className={styles.detailLabel}>
              <User size={13} /> {lang === 'da' ? 'Oprettet af' : 'Created by'}
            </div>
            <div className={styles.detailValue}>{ticket.user_name}</div>
          </div>

          <div className={styles.detailRow}>
            <div className={styles.detailLabel}>
              <Clock size={13} /> {tr.ticketCreatedAt}
            </div>
            <div className={styles.detailValue}>
              {new Date(ticket.created_at).toLocaleString()}
            </div>
          </div>
        </div>

        {/* Conversation history */}
        {ticket.description && (
          <div className={styles.descSection}>
            <div className={styles.descTitle}>
              {lang === 'da' ? 'Samtalehistorik' : 'Conversation History'}
            </div>
            <div className={styles.descBody}>{ticket.description}</div>
          </div>
        )}

        <div className={styles.footer}>
          <button className={styles.closeFooterBtn} onClick={onClose}>
            {lang === 'da' ? 'Luk' : 'Close'}
          </button>
        </div>
      </div>
    </div>
  );
}
