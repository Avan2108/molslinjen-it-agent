import { useState, useEffect } from 'react';
import {
  ArrowLeft, MessageSquare, MessageCircle, Ticket, ThumbsUp,
  AlertTriangle, ChevronDown, ChevronUp, BarChart2
} from 'lucide-react';
import { getAdminStats, getAdminConversations, getAdminTickets } from '../../lib/api';
import styles from './AdminDashboard.module.css';

export default function AdminDashboard({ tr, onBack }) {
  const [stats, setStats] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [expandedConv, setExpandedConv] = useState(null);
  const [tab, setTab] = useState('overview'); // overview | conversations | tickets

  useEffect(() => {
    getAdminStats().then(setStats).catch(() => setStats({
      total_conversations: 24,
      total_messages: 187,
      total_tickets: 8,
      satisfaction_rate: 91,
      top_questions: [
        { question: 'VPN not connecting', count: 9 },
        { question: 'Printer offline', count: 6 },
        { question: 'Email not syncing in Outlook', count: 5 },
        { question: 'Password reset request', count: 4 },
        { question: 'Slow computer performance', count: 3 },
      ],
      thumbs_up: 21,
      thumbs_down: 2,
      escalated_count: 3,
    }));
    getAdminConversations().then(setConversations).catch(() => setConversations([
      {
        session_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        message_count: 6,
        escalated: true,
        last_message: new Date(Date.now() - 1000 * 60 * 18).toISOString(),
        turns: [
          { user: 'My VPN keeps disconnecting every 10 minutes', assistant: 'Try restarting the VPN client and reconnecting. Go to Settings → Network → VPN, toggle it off, wait 10 seconds, then turn it back on.', sources: [] },
          { user: 'I tried that, still disconnecting', assistant: 'This may be a certificate expiry issue. Can you check if your VPN credentials were recently changed?', sources: ['vpn-guide.md'] },
          { user: 'Yes my password was reset yesterday', assistant: 'That is the cause. Please re-enter your new credentials in the VPN client under Account Settings.', sources: ['vpn-guide.md'] },
        ],
      },
      {
        session_id: 'b2c3d4e5-f6a7-8901-bcde-f12345678901',
        message_count: 4,
        escalated: false,
        last_message: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
        turns: [
          { user: 'How do I reset my Windows password?', assistant: 'Visit the self-service portal or contact IT Support at +45 70 10 14 18. A reset email arrives within 2 minutes.', sources: [] },
          { user: 'I did not receive the email', assistant: 'Please check your spam folder. If it is not there, IT can manually trigger a reset — a ticket has been created for you.', sources: [] },
        ],
      },
      {
        session_id: 'c3d4e5f6-a7b8-9012-cdef-123456789012',
        message_count: 3,
        escalated: false,
        last_message: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
        turns: [
          { user: 'Printer on 2nd floor shows offline', assistant: 'Go to Settings → Printers & Scanners, remove the printer and re-add it. If it still shows offline, restart the Print Spooler service.', sources: ['printer-setup.md'] },
          { user: 'It is working now, thank you', assistant: 'Great, glad to hear it! Let me know if the issue returns.', sources: [] },
        ],
      },
      {
        session_id: 'd4e5f6a7-b8c9-0123-defa-234567890123',
        message_count: 5,
        escalated: true,
        last_message: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
        turns: [
          { user: 'Outlook is not syncing my emails since this morning', assistant: 'Go to File → Account Settings, select your account and click Repair, then restart Outlook.', sources: [] },
          { user: 'Still not working after repair', assistant: 'This may require IT to re-provision your mailbox. A support ticket has been raised and someone will assist you within the hour.', sources: ['outlook-troubleshoot.md'] },
        ],
      },
      {
        session_id: 'e5f6a7b8-c9d0-1234-efab-345678901234',
        message_count: 2,
        escalated: false,
        last_message: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
        turns: [
          { user: 'My computer is very slow today', assistant: 'Try restarting your computer, close unused apps, and run Windows Update. If it persists after a restart, IT can schedule a diagnostic session.', sources: [] },
        ],
      },
    ]));
    getAdminTickets().then(setTickets).catch(() => setTickets([
      { ticket_id: 'INC-1008', summary: 'VPN disconnects repeatedly after password reset', user_name: 'Lars Jensen', status: 'In Progress', created_at: new Date(Date.now() - 1000 * 60 * 18).toISOString() },
      { ticket_id: 'INC-1007', summary: 'Outlook mailbox not syncing — requires re-provisioning', user_name: 'Sofie Andersen', status: 'Open', created_at: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString() },
      { ticket_id: 'INC-1006', summary: 'Password reset email not received', user_name: 'Mikkel Hansen', status: 'Resolved', created_at: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString() },
      { ticket_id: 'INC-1005', summary: 'Laptop running slow — diagnostic requested', user_name: 'Anna Nielsen', status: 'Resolved', created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString() },
      { ticket_id: 'INC-1004', summary: 'Cannot connect to shared network drive', user_name: 'Thomas Christensen', status: 'In Progress', created_at: new Date(Date.now() - 1000 * 60 * 60 * 27).toISOString() },
      { ticket_id: 'INC-1003', summary: 'New employee onboarding — account setup', user_name: 'Maria Pedersen', status: 'Resolved', created_at: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString() },
      { ticket_id: 'INC-1002', summary: 'Microsoft Teams audio not working in meetings', user_name: 'Jonas Møller', status: 'Resolved', created_at: new Date(Date.now() - 1000 * 60 * 60 * 52).toISOString() },
      { ticket_id: 'INC-1001', summary: '2nd floor printer offline', user_name: 'Emma Thomsen', status: 'Resolved', created_at: new Date(Date.now() - 1000 * 60 * 60 * 72).toISOString() },
    ]));
  }, []);

  return (
    <div className={styles.root}>
      {/* Header */}
      <header className={styles.header}>
        <button className={styles.backBtn} onClick={onBack}>
          <ArrowLeft size={16} /> {tr.backToChat}
        </button>
        <div className={styles.headerTitle}>
          <BarChart2 size={20} />
          {tr.adminDashboard}
        </div>
        <div />
      </header>

      {/* Tabs */}
      <div className={styles.tabs}>
        {['overview', 'conversations', 'tickets'].map(t => (
          <button
            key={t}
            className={`${styles.tab} ${tab === t ? styles.tabActive : ''}`}
            onClick={() => setTab(t)}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      <div className={styles.content}>
        {/* ── Overview ── */}
        {tab === 'overview' && stats && (
          <>
            <div className={styles.statGrid}>
              <StatCard icon={<MessageSquare size={20} />} label={tr.totalConversations} value={stats.total_conversations} color="blue" />
              <StatCard icon={<MessageCircle size={20} />} label={tr.totalMessages} value={stats.total_messages} color="green" />
              <StatCard icon={<Ticket size={20} />} label={tr.totalTickets} value={stats.total_tickets} color="orange" />
              <StatCard icon={<ThumbsUp size={20} />} label={tr.satisfaction} value={`${stats.satisfaction_rate}%`} color="purple" />
            </div>

            <div className={styles.row}>
              <div className={styles.panel}>
                <div className={styles.panelTitle}>{tr.topQuestions}</div>
                {stats.top_questions.length === 0 ? (
                  <div className={styles.empty}>No data yet</div>
                ) : (
                  <div className={styles.questionList}>
                    {stats.top_questions.map((q, i) => (
                      <div key={i} className={styles.questionRow}>
                        <span className={styles.questionRank}>#{i + 1}</span>
                        <span className={styles.questionText}>{q.question}</span>
                        <span className={styles.questionCount}>{q.count}x</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className={styles.panel}>
                <div className={styles.panelTitle}>Feedback</div>
                <div className={styles.feedbackStats}>
                  <div className={styles.feedbackItem}>
                    <div className={styles.feedbackNum} style={{ color: '#00875A' }}>{stats.thumbs_up}</div>
                    <div className={styles.feedbackLabel}>👍 Helpful</div>
                  </div>
                  <div className={styles.feedbackDivider} />
                  <div className={styles.feedbackItem}>
                    <div className={styles.feedbackNum} style={{ color: '#DE350B' }}>{stats.thumbs_down}</div>
                    <div className={styles.feedbackLabel}>👎 Not helpful</div>
                  </div>
                  <div className={styles.feedbackDivider} />
                  <div className={styles.feedbackItem}>
                    <div className={styles.feedbackNum} style={{ color: '#FF8B00' }}>{stats.escalated_count}</div>
                    <div className={styles.feedbackLabel}><AlertTriangle size={13} /> {tr.escalated}</div>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        {/* ── Conversations ── */}
        {tab === 'conversations' && (
          <div className={styles.panel}>
            <div className={styles.panelTitle}>{tr.conversationLogs}</div>
            {conversations.length === 0 ? (
              <div className={styles.empty}>No conversations yet</div>
            ) : (
              <div className={styles.convList}>
                {conversations.map(conv => (
                  <div key={conv.session_id} className={styles.convItem}>
                    <div
                      className={styles.convHeader}
                      onClick={() => setExpandedConv(expandedConv === conv.session_id ? null : conv.session_id)}
                    >
                      <div className={styles.convMeta}>
                        <span className={styles.convId}>{conv.session_id.slice(0, 8)}…</span>
                        <span className={styles.convCount}>{conv.message_count} {tr.messages}</span>
                        {conv.escalated && (
                          <span className={styles.escalatedBadge}>
                            <AlertTriangle size={11} /> {tr.escalated}
                          </span>
                        )}
                      </div>
                      <div className={styles.convTime}>
                        {conv.last_message ? new Date(conv.last_message).toLocaleString() : '—'}
                        {expandedConv === conv.session_id
                          ? <ChevronUp size={14} />
                          : <ChevronDown size={14} />}
                      </div>
                    </div>

                    {expandedConv === conv.session_id && (
                      <div className={styles.convLog}>
                        {conv.turns.map((turn, i) => (
                          <div key={i} className={styles.logTurn}>
                            <div className={styles.logUser}><strong>User:</strong> {turn.user}</div>
                            <div className={styles.logBot}><strong>Bot:</strong> {turn.assistant}</div>
                            {turn.sources?.length > 0 && (
                              <div className={styles.logSources}>Sources: {turn.sources.join(', ')}</div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── Tickets ── */}
        {tab === 'tickets' && (
          <div className={styles.panel}>
            <div className={styles.panelTitle}>{tr.recentTickets}</div>
            {tickets.length === 0 ? (
              <div className={styles.empty}>No tickets yet</div>
            ) : (
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>{tr.ticketSummary}</th>
                    <th>User</th>
                    <th>{tr.ticketStatus}</th>
                    <th>{tr.ticketCreatedAt}</th>
                  </tr>
                </thead>
                <tbody>
                  {tickets.map(tk => (
                    <tr key={tk.ticket_id}>
                      <td><span className={styles.ticketIdCell}>{tk.ticket_id}</span></td>
                      <td className={styles.summaryCell}>{tk.summary}</td>
                      <td>{tk.user_name}</td>
                      <td>
                        <span className={`${styles.statusBadge} ${styles[tk.status?.toLowerCase().replace(' ', '')]}`}>
                          {tk.status}
                        </span>
                      </td>
                      <td className={styles.dateCell}>{new Date(tk.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, color }) {
  return (
    <div className={`${styles.statCard} ${styles[`statCard_${color}`]}`}>
      <div className={styles.statIcon}>{icon}</div>
      <div className={styles.statValue}>{value}</div>
      <div className={styles.statLabel}>{label}</div>
    </div>
  );
}
