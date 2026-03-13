import ChatWindow from '../components/chat/ChatWindow';

export default function ChatPage({ lang, tr, userName, userRole, darkMode, onToggleLang, onToggleDark, onOpenAdmin }) {
  return (
    <ChatWindow
      lang={lang}
      tr={tr}
      userName={userName}
      userRole={userRole}
      darkMode={darkMode}
      onToggleLang={onToggleLang}
      onToggleDark={onToggleDark}
      onOpenAdmin={onOpenAdmin}
    />
  );
}
