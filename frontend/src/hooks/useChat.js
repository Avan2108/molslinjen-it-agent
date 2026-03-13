import { useState, useEffect, useCallback, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import {
  sendMessage as sendMessageApi,
  sendFeedback as sendFeedbackApi,
  createTicket as createTicketApi,
  getTicket as getTicketApi,
  getSuggestions as getSuggestionsApi,
  summarizeTicket as summarizeTicketApi,
} from '../lib/api';

// Demo responses used when the backend is unreachable
const DEMO_RESPONSES = {
  en: [
    { keys: ['vpn', 'network', 'connect'], reply: 'Try restarting the VPN client and reconnecting. If the issue persists, ensure your credentials have not expired.\n\n**Quick fix:** Go to **Settings → Network → VPN**, toggle it off, wait 10 seconds, then turn it back on.' },
    { keys: ['password', 'reset', 'forgot', 'locked'], reply: 'To reset your password visit the self-service portal. A reset email arrives within 2 minutes.\n\n> Tip: New passwords must be at least 12 characters and cannot reuse the last 5.' },
    { keys: ['printer', 'print', 'offline', 'scan'], reply: 'Check the printer is powered on and on the network. On Windows go to **Settings → Printers & Scanners**, remove the printer and re-add it.\n\nIf it still shows offline, restart the print spooler:\n1. Press `Win + R`, type `services.msc`\n2. Find **Print Spooler** → right-click → Restart' },
    { keys: ['email', 'mail', 'outlook', 'sync'], reply: "If Outlook is not syncing:\n1. Go to **File → Account Settings → Account Settings**\n2. Select your account → **Repair**\n3. Restart Outlook\n\nStill not working? IT can remotely re-provision your mailbox — create a ticket and we'll fix it within the hour." },
    { keys: ['slow', 'performance', 'freeze', 'crash', 'computer'], reply: 'Quick steps to improve performance:\n- **Restart** your computer (clears memory leaks)\n- Close unused background apps\n- Run **Windows Update** (Settings → Windows Update)\n- Run **Disk Cleanup** (search in Start menu)\n\nIf performance remains poor after a restart, IT can schedule a diagnostic session.' },
  ],
  da: [
    { keys: ['vpn', 'netværk', 'forbind'], reply: 'Prøv at genstarte VPN-klienten. Gå til **Indstillinger → Netværk → VPN**, sluk den, vent 10 sekunder og tænd den igen. Kontakt IT-support på **+45 70 10 14 18**, hvis problemet fortsætter.' },
    { keys: ['adgangskode', 'nulstil', 'kodeord', 'låst'], reply: 'Besøg selvbetjeningsportalen for at nulstille din adgangskode. En nulstillingsmail modtages inden for 2 minutter.' },
    { keys: ['printer', 'udskriv', 'offline', 'scan'], reply: 'Kontroller at printeren er tændt og forbundet til netværket. Gå til **Indstillinger → Printere og scannere**, fjern printeren og tilføj den igen.' },
    { keys: ['email', 'mail', 'outlook', 'synkroniserer'], reply: 'Hvis Outlook ikke synkroniserer: Gå til **Filer → Kontoindstillinger**, vælg din konto og klik **Reparer**. Genstart derefter Outlook.' },
  ],
};

function getDemoResponse(text, lang) {
  const lower = text.toLowerCase();
  const pool = DEMO_RESPONSES[lang] || DEMO_RESPONSES.en;
  const match = pool.find(r => r.keys.some(k => lower.includes(k)));
  return match?.reply ?? (lang === 'da'
    ? 'Tak for din henvendelse. Jeg undersøger dette for dig. Hvis problemet fortsætter, kan du oprette en supportbillet eller kontakte IT-support direkte på **+45 70 10 14 18**.'
    : "Thank you for your question. I'll look into this for you. If the issue persists, you can create a support ticket or contact IT Support directly at **+45 70 10 14 18**.");
}

function getFallbackSuggestions(lang) {
  return lang === 'da'
    ? ['Mit VPN virker ikke', 'Nulstil min adgangskode', 'Printeren er offline', 'Min e-mail synkroniserer ikke']
    : ['My VPN is not connecting', 'Reset my password', 'Printer is offline', 'My email is not syncing'];
}

export function useChat({ lang, userName }) {
  const [sessionId] = useState(() => uuidv4());
  const [messages, setMessages] = useState([]);
  const [typing, setTyping] = useState(false);
  const [suggestions, setSuggestions] = useState(() => getFallbackSuggestions(lang));
  const [pendingImages, setPendingImages] = useState([]);
  const [pendingTicket, setPendingTicket] = useState(null);
  const [summarizing, setSummarizing] = useState(null);
  const [feedback, setFeedback] = useState({});
  const [copiedMsgId, setCopiedMsgId] = useState(null);
  const [ticketLookup, setTicketLookup] = useState('');
  const [ticketResult, setTicketResult] = useState(null);
  const [modalTicket, setModalTicket] = useState(null);
  const [copied, setCopied] = useState(false);

  const bottomRef = useRef(null);
  const inputRef = useRef(null);
  const imageInputRef = useRef(null);

  // Load suggestions on mount / lang change
  useEffect(() => {
    setSuggestions(getFallbackSuggestions(lang));
    getSuggestionsApi(lang)
      .then(res => { if (res?.length) setSuggestions(res); })
      .catch(() => {});
  }, [lang]);

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, typing]);

  const sendMsg = useCallback(async (text) => {
    if (!text.trim() || typing) return;
    const snapImages = [...pendingImages];
    const userMsg = { id: uuidv4(), role: 'user', text, images: snapImages.map(i => i.dataUrl) };
    setMessages(prev => [...prev, userMsg]);
    setPendingImages([]);
    setTyping(true);

    let data;
    try {
      const b64List = snapImages.map(i => i.b64);
      data = await sendMessageApi(sessionId, text, lang, b64List);
    } catch {
      await new Promise(r => setTimeout(r, 900 + Math.random() * 700));
      data = {
        message_id: uuidv4(),
        answer: getDemoResponse(text, lang),
        sources: [],
        escalate: true,
      };
    }

    setMessages(prev => [...prev, {
      id: data.message_id,
      role: 'bot',
      text: data.answer,
      sources: data.sources,
      escalate: data.escalate,
      ticketCreated: null,
    }]);
    setTyping(false);
    inputRef.current?.focus();
  }, [sessionId, lang, typing, pendingImages]);

  const handleFeedback = useCallback(async (msgId, rating) => {
    if (feedback[msgId]) return;
    setFeedback(prev => ({ ...prev, [msgId]: rating }));
    await sendFeedbackApi(sessionId, msgId, rating);
  }, [feedback, sessionId]);

  const copyMessage = useCallback((msgId, text) => {
    const markDone = () => {
      setCopiedMsgId(msgId);
      setTimeout(() => setCopiedMsgId(null), 2000);
    };
    const execFallback = () => {
      try {
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.cssText = 'position:fixed;opacity:0;pointer-events:none';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        markDone();
      } catch { /* nothing */ }
    };
    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(text).then(markDone).catch(execFallback);
    } else {
      execFallback();
    }
  }, []);

  const handleImageFiles = useCallback((e) => {
    const files = Array.from(e.target.files).slice(0, 3 - pendingImages.length);
    files.forEach(file => {
      const reader = new FileReader();
      reader.onload = ev => {
        const dataUrl = ev.target.result;
        const b64 = dataUrl.split(',')[1];
        setPendingImages(prev => {
          if (prev.length >= 3) return prev;
          if (prev.some(i => i.b64 === b64)) return prev;
          return [...prev, { dataUrl, b64 }];
        });
      };
      reader.readAsDataURL(file);
    });
    e.target.value = '';
  }, [pendingImages.length]);

  const removeImage = useCallback((b64) => {
    setPendingImages(prev => prev.filter(i => i.b64 !== b64));
  }, []);

  const openCreateTicketModal = useCallback(async (msgId) => {
    setSummarizing(msgId);
    let title = '';
    let description = '';
    try {
      const result = await summarizeTicketApi(sessionId, lang);
      title = result.title || '';
      description = result.description || '';
    } catch {
      // fallback below
    } finally {
      setSummarizing(null);
    }
    if (!title) {
      const firstUser = messages.find(m => m.role === 'user');
      title = firstUser ? firstUser.text.replace(/[?!.]+$/, '').trim().slice(0, 80) : '';
    }
    if (!description) {
      const userMsgs = messages.filter(m => m.role === 'user').map(m => m.text);
      if (userMsgs.length === 0) {
        description = '';
      } else if (userMsgs.length === 1) {
        description = `User reported: "${userMsgs[0]}"`;
      } else {
        description = `User reported: "${userMsgs[0]}"\n\nAdditional context:\n` +
          userMsgs.slice(1).map(m => `- ${m}`).join('\n');
      }
    }
    setPendingTicket({ msgId, defaultTitle: title, defaultDescription: description });
  }, [sessionId, lang, messages]);

  const handleCreateTicket = useCallback(async ({ title, description, priority, attachments }) => {
    const { msgId } = pendingTicket;
    setPendingTicket(null);
    const ticket = await createTicketApi(sessionId, title, description, userName, priority);
    ticket.priority = priority;
    ticket.attachment_count = attachments.length;
    setMessages(prev => prev.map(m => m.id === msgId ? { ...m, ticketCreated: ticket } : m));
  }, [pendingTicket, sessionId, userName]);

  const handleTicketLookup = useCallback(async (e) => {
    e.preventDefault();
    if (!ticketLookup.trim()) return;
    const result = await getTicketApi(ticketLookup.trim());
    if (result && !result.error && result.user_name !== userName) {
      setTicketResult({
        error: lang === 'da'
          ? 'Billet ikke fundet eller ingen adgang.'
          : 'Ticket not found or access denied.',
      });
      return;
    }
    setTicketResult(result);
  }, [ticketLookup, lang, userName]);

  const handleContactIT = useCallback((tr) => {
    navigator.clipboard.writeText(tr.itPhone).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }, []);

  const startNewChat = useCallback(() => {
    setMessages([]);
    setTicketResult(null);
  }, []);

  return {
    // State
    sessionId, messages, typing, suggestions,
    pendingImages, setPendingImages,
    pendingTicket, setPendingTicket,
    summarizing, feedback, copiedMsgId,
    ticketLookup, setTicketLookup,
    ticketResult, modalTicket, setModalTicket,
    copied,
    // Refs
    bottomRef, inputRef, imageInputRef,
    // Actions
    sendMsg, handleFeedback, copyMessage,
    handleImageFiles, removeImage,
    openCreateTicketModal, handleCreateTicket,
    handleTicketLookup, handleContactIT,
    startNewChat,
  };
}
