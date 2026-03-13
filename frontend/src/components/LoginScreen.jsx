import { useState } from 'react';
import { Globe } from 'lucide-react';
import styles from './LoginScreen.module.css';

// Image served from /public
const ferryBg = '/molslinjenLoginScreen.png';

export default function LoginScreen({ tr, onLogin, onToggleLang, lang }) {
  const [name, setName] = useState('');
  const [role, setRole] = useState('employee'); // 'employee' | 'admin'

  function handleSubmit(e) {
    e.preventDefault();
    if (name.trim()) onLogin(name.trim(), role);
  }

  // ── When Microsoft SSO (MSAL) is configured, the name input and manual
  // ── login button will be removed. The "Continue with Microsoft" button
  // ── will call msalInstance.loginRedirect() and the callback in app/page.js
  // ── will set the user name & role from the Azure AD token claims.

  return (
    <div className={styles.root}>
      {/* Ferry background photo */}
      <img src={ferryBg} className={styles.ferryBg} alt="" aria-hidden="true" />

      <button className={styles.langBtn} onClick={onToggleLang} title={tr.languageLabel}>
        <Globe size={16} />
        {tr.language}
      </button>

      <div className={styles.card}>
        <h1 className={styles.title}>{tr.loginTitle}</h1>
        <p className={styles.subtitle}>{tr.loginSubtitle}</p>
        <form onSubmit={handleSubmit} className={styles.form}>
          <input
            className={styles.input}
            type="text"
            placeholder={tr.loginPlaceholder}
            value={name}
            onChange={e => setName(e.target.value)}
            autoFocus
          />

          {/* Role selector */}
          <div className={styles.roleGroup}>
            <button
              type="button"
              className={`${styles.roleBtn} ${role === 'employee' ? styles.roleBtnActive : ''}`}
              onClick={() => setRole('employee')}
            >
              <span className={styles.roleIcon}>👤</span>
              <span>
                <div className={styles.roleLabel}>{lang === 'da' ? 'Medarbejder' : 'Employee'}</div>
                <div className={styles.roleDesc}>{lang === 'da' ? 'IT hjælp & support' : 'IT help & support'}</div>
              </span>
            </button>
            <button
              type="button"
              className={`${styles.roleBtn} ${role === 'admin' ? styles.roleBtnActive : ''}`}
              onClick={() => setRole('admin')}
            >
              <span className={styles.roleIcon}>🛡️</span>
              <span>
                <div className={styles.roleLabel}>IT Admin</div>
                <div className={styles.roleDesc}>{lang === 'da' ? 'Dashboard & logs' : 'Dashboard & logs'}</div>
              </span>
            </button>
          </div>

          <button className={styles.btn} type="submit" disabled={!name.trim()}>
            {tr.loginBtn}
          </button>

          <div className={styles.divider}>{lang === 'da' ? 'eller' : 'or'}</div>

          {/* Microsoft SSO — plug in MSAL onClick handler when Azure AD app is registered */}
          <button type="button" className={styles.ssoBtn}>
            <svg className={styles.ssoIcon} viewBox="0 0 21 21" xmlns="http://www.w3.org/2000/svg">
              <rect x="1" y="1" width="9" height="9" fill="#F25022"/>
              <rect x="11" y="1" width="9" height="9" fill="#7FBA00"/>
              <rect x="1" y="11" width="9" height="9" fill="#00A4EF"/>
              <rect x="11" y="11" width="9" height="9" fill="#FFB900"/>
            </svg>
            {lang === 'da' ? 'Fortsæt med Microsoft' : 'Continue with Microsoft'}
          </button>
        </form>
      </div>
    </div>
  );
}
