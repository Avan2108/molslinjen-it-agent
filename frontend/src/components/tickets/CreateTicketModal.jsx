import { useState, useEffect, useRef } from 'react';
import { X, Ticket, AlertTriangle, Paperclip, Trash2 } from 'lucide-react';
import styles from './CreateTicketModal.module.css';

const PRIORITIES = [
  { value: 'low',    label: 'Low',    labelDa: 'Lav',    color: '#00875A' },
  { value: 'medium', label: 'Medium', labelDa: 'Middel', color: '#FF8B00' },
  { value: 'high',   label: 'High',   labelDa: 'Høj',    color: '#DE350B' },
  { value: 'urgent', label: 'Urgent', labelDa: 'Kritisk',color: '#6200ea' },
];

export default function CreateTicketModal({
  defaultTitle,
  defaultDescription,
  lang,
  tr,
  onSubmit,
  onClose,
}) {
  const [title, setTitle]             = useState(defaultTitle || '');
  const [description, setDescription] = useState(defaultDescription || '');
  const [priority, setPriority]       = useState('medium');
  const [attachments, setAttachments] = useState([]);
  const [submitting, setSubmitting]   = useState(false);
  const [errors, setErrors]           = useState({});
  const fileInputRef = useRef(null);
  const titleRef     = useRef(null);

  const da = lang === 'da';

  // Close on Escape
  useEffect(() => {
    function onKey(e) { if (e.key === 'Escape') onClose(); }
    window.addEventListener('keydown', onKey);
    titleRef.current?.focus();
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  function validate() {
    const e = {};
    if (!title.trim())       e.title       = da ? 'Titel er påkrævet'       : 'Title is required';
    if (!description.trim()) e.description = da ? 'Beskrivelse er påkrævet' : 'Description is required';
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!validate()) return;
    setSubmitting(true);
    await onSubmit({ title: title.trim(), description: description.trim(), priority, attachments });
    setSubmitting(false);
  }

  function handleFiles(e) {
    const files = Array.from(e.target.files);
    setAttachments(prev => {
      const existing = new Set(prev.map(f => f.name));
      const fresh = files.filter(f => !existing.has(f.name));
      return [...prev, ...fresh];
    });
    e.target.value = '';
  }

  function removeAttachment(name) {
    setAttachments(prev => prev.filter(f => f.name !== name));
  }

  const selectedPriority = PRIORITIES.find(p => p.value === priority);

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>

        {/* ── Header ── */}
        <div className={styles.header}>
          <div className={styles.headerLeft}>
            <div className={styles.headerIcon}><Ticket size={18} /></div>
            <div>
              <div className={styles.headerTitle}>
                {da ? 'Opret supportbillet' : 'Create Support Ticket'}
              </div>
              <div className={styles.headerSub}>
                {da ? 'Udfyld detaljerne nedenfor' : 'Fill in the details below'}
              </div>
            </div>
          </div>
          <button className={styles.closeBtn} onClick={onClose} title="Close">
            <X size={18} />
          </button>
        </div>

        {/* ── Form ── */}
        <form onSubmit={handleSubmit} className={styles.form}>

          {/* Title */}
          <div className={styles.field}>
            <label className={styles.label}>
              {da ? 'Titel' : 'Title'}
              <span className={styles.required}>*</span>
            </label>
            <input
              ref={titleRef}
              className={`${styles.input} ${errors.title ? styles.inputError : ''}`}
              placeholder={da ? 'Kort beskrivelse af problemet…' : 'Brief description of the issue…'}
              value={title}
              onChange={e => { setTitle(e.target.value); setErrors(p => ({ ...p, title: '' })); }}
              maxLength={120}
            />
            {errors.title && <div className={styles.errorMsg}><AlertTriangle size={11} /> {errors.title}</div>}
            <div className={styles.charCount}>{title.length}/120</div>
          </div>

          {/* Description */}
          <div className={styles.field}>
            <label className={styles.label}>
              {da ? 'Beskrivelse' : 'Description'}
              <span className={styles.required}>*</span>
            </label>
            <textarea
              className={`${styles.textarea} ${errors.description ? styles.inputError : ''}`}
              placeholder={da
                ? 'Beskriv problemet i detaljer — trin til at reproducere, fejlmeddelelser, hvad du allerede har prøvet…'
                : 'Describe the issue in detail — steps to reproduce, error messages, what you have already tried…'}
              value={description}
              onChange={e => { setDescription(e.target.value); setErrors(p => ({ ...p, description: '' })); }}
              rows={5}
            />
            {errors.description && (
              <div className={styles.errorMsg}><AlertTriangle size={11} /> {errors.description}</div>
            )}
          </div>

          {/* Priority */}
          <div className={styles.field}>
            <label className={styles.label}>{da ? 'Prioritet' : 'Priority'}</label>
            <div className={styles.priorityGroup}>
              {PRIORITIES.map(p => (
                <button
                  key={p.value}
                  type="button"
                  className={`${styles.priorityBtn} ${priority === p.value ? styles.priorityBtnActive : ''}`}
                  style={priority === p.value ? { borderColor: p.color, color: p.color, background: p.color + '18' } : {}}
                  onClick={() => setPriority(p.value)}
                >
                  <span
                    className={styles.priorityDot}
                    style={{ background: p.color }}
                  />
                  {da ? p.labelDa : p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Attachments */}
          <div className={styles.field}>
            <label className={styles.label}>{da ? 'Vedhæftninger' : 'Attachments'}</label>
            <div
              className={styles.dropZone}
              onClick={() => fileInputRef.current?.click()}
              onDragOver={e => { e.preventDefault(); e.currentTarget.classList.add(styles.dropZoneActive); }}
              onDragLeave={e => e.currentTarget.classList.remove(styles.dropZoneActive)}
              onDrop={e => {
                e.preventDefault();
                e.currentTarget.classList.remove(styles.dropZoneActive);
                const files = Array.from(e.dataTransfer.files);
                setAttachments(prev => {
                  const existing = new Set(prev.map(f => f.name));
                  return [...prev, ...files.filter(f => !existing.has(f.name))];
                });
              }}
            >
              <Paperclip size={18} className={styles.dropIcon} />
              <span>{da ? 'Klik eller træk filer hertil' : 'Click or drag files here'}</span>
              <span className={styles.dropHint}>PNG, JPG, PDF, DOCX — max 10 MB each</span>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className={styles.fileInput}
              onChange={handleFiles}
              accept=".png,.jpg,.jpeg,.gif,.pdf,.doc,.docx,.txt,.csv,.xlsx,.log"
            />

            {attachments.length > 0 && (
              <div className={styles.fileList}>
                {attachments.map(f => (
                  <div key={f.name} className={styles.fileItem}>
                    <Paperclip size={12} />
                    <span className={styles.fileName}>{f.name}</span>
                    <span className={styles.fileSize}>({(f.size / 1024).toFixed(0)} KB)</span>
                    <button
                      type="button"
                      className={styles.removeFileBtn}
                      onClick={() => removeAttachment(f.name)}
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className={styles.footer}>
            <div className={styles.priorityPreview}>
              <span
                className={styles.priorityBadge}
                style={{ background: selectedPriority.color + '20', color: selectedPriority.color }}
              >
                <span className={styles.priorityDot} style={{ background: selectedPriority.color }} />
                {da ? selectedPriority.labelDa : selectedPriority.label}
              </span>
              {attachments.length > 0 && (
                <span className={styles.attachmentCount}>
                  <Paperclip size={11} /> {attachments.length}
                </span>
              )}
            </div>
            <div className={styles.footerBtns}>
              <button type="button" className={styles.cancelBtn} onClick={onClose}>
                {da ? 'Annuller' : 'Cancel'}
              </button>
              <button type="submit" className={styles.submitBtn} disabled={submitting}>
                {submitting
                  ? (da ? 'Opretter…' : 'Creating…')
                  : (da ? 'Opret billet' : 'Create Ticket')}
              </button>
            </div>
          </div>

        </form>
      </div>
    </div>
  );
}
