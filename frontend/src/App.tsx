import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { t } from './lib/i18n';
import LoginScreen from './components/LoginScreen';
import ChatPage from './pages/ChatPage';
import AdminPage from './pages/AdminPage';

function AppRoutes() {
  const [lang, setLang] = useState('en');
  const [darkMode, setDarkMode] = useState(false);
  const [userName, setUserName] = useState<string | null>(null);
  const [userRole, setUserRole] = useState('employee');

  const navigate = useNavigate();

  useEffect(() => {
    const storedLang = localStorage.getItem('lang');
    if (storedLang && storedLang !== 'en') setLang(storedLang);
    const storedDark = localStorage.getItem('darkMode');
    if (storedDark === 'true') setDarkMode(true);
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
    localStorage.setItem('darkMode', String(darkMode));
  }, [darkMode]);

  const tr = (t as Record<string, Record<string, string>>)[lang];

  function toggleLang() {
    const next = lang === 'en' ? 'da' : 'en';
    setLang(next);
    localStorage.setItem('lang', next);
  }

  function handleLogin(name: string, role: string) {
    setUserName(name);
    setUserRole(role);
  }

  if (!userName) {
    return (
      <LoginScreen
        lang={lang}
        tr={tr}
        onLogin={handleLogin}
        onToggleLang={toggleLang}
      />
    );
  }

  const sharedProps = {
    lang, tr, userName, userRole,
    darkMode,
    onToggleLang: toggleLang,
    onToggleDark: () => setDarkMode(d => !d),
  };

  return (
    <Routes>
      <Route
        path="/"
        element={
          <ChatPage
            {...sharedProps}
            onOpenAdmin={() => navigate('/admin')}
          />
        }
      />
      <Route
        path="/admin"
        element={
          userRole === 'admin'
            ? <AdminPage tr={tr} onBack={() => navigate('/')} />
            : <Navigate to="/" replace />
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}
