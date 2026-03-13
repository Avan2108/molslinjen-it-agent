import styles from './ChatWindow.module.css';

export default function TypingIndicator() {
  return (
    <div className={`${styles.msgRow} ${styles.botRow}`}>
      <div className={styles.avatar}>IT</div>
      <div className={styles.typingBubble}>
        <span /><span /><span />
      </div>
    </div>
  );
}
