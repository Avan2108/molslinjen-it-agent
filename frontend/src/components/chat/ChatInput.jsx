import { Paperclip, X, Send } from 'lucide-react';
import styles from './ChatWindow.module.css';

export default function ChatInput({
  input, setInput, typing, pendingImages,
  onSend, onImageFiles, onRemoveImage,
  lang, tr, imageInputRef, inputRef,
}) {
  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend(input);
      setInput('');
    }
  }

  return (
    <div className={styles.inputBar}>
      {pendingImages.length > 0 && (
        <div className={styles.imagePreviewStrip}>
          {pendingImages.map(img => (
            <div key={img.b64} className={styles.imagePreviewItem}>
              <img src={img.dataUrl} alt="attachment" className={styles.imagePreviewThumb} />
              <button className={styles.imageRemoveBtn} onClick={() => onRemoveImage(img.b64)}>
                <X size={10} />
              </button>
            </div>
          ))}
        </div>
      )}

      <div className={styles.inputWrap}>
        <input
          ref={imageInputRef}
          type="file"
          accept="image/png,image/jpeg,image/gif,image/webp"
          multiple
          className={styles.fileInputHidden}
          onChange={onImageFiles}
        />
        <button
          className={styles.attachBtn}
          onClick={() => imageInputRef.current?.click()}
          disabled={typing || pendingImages.length >= 3}
          title={
            pendingImages.length >= 3
              ? 'Maximum 3 images'
              : (lang === 'da' ? 'Vedhæft screenshot' : 'Attach screenshot')
          }
        >
          <Paperclip size={17} />
        </button>

        <input
          ref={inputRef}
          className={styles.input}
          placeholder={tr.placeholder}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          disabled={typing}
        />
        <button
          className={styles.sendBtn}
          onClick={() => { onSend(input); setInput(''); }}
          disabled={(!input.trim() && pendingImages.length === 0) || typing}
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
