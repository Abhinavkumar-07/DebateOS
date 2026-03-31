import './FallacyAlert.css';

const SEVERITY_LABELS = ['', 'Minor', 'Moderate', 'Significant', 'Major', 'Critical'];
const SEVERITY_COLORS = ['', '#22c55e', '#eab308', '#f97316', '#ef4444', '#dc2626'];

export default function FallacyAlert({ fallacy, side, round }) {
  if (!fallacy || !fallacy.fallacy_detected) {
    return (
      <div className={`fallacy-alert fallacy-clear fallacy-${side} animate-fade-in`}>
        <span className="fallacy-clear-icon">✅</span>
        <span className="fallacy-clear-text">No fallacies detected</span>
      </div>
    );
  }

  const severityLabel = SEVERITY_LABELS[fallacy.severity] || 'Unknown';

  return (
    <div className={`fallacy-alert fallacy-found fallacy-${side} animate-scale-in`} id={`fallacy-${side}-round-${round}`}>
      <div className="fallacy-header">
        <span className="fallacy-icon">⚠️</span>
        <span className="fallacy-type">{fallacy.type}</span>
        <span
          className="fallacy-severity"
          style={{ background: `${SEVERITY_COLORS[fallacy.severity]}20`, color: SEVERITY_COLORS[fallacy.severity] }}
        >
          {severityLabel} ({fallacy.severity}/5)
        </span>
      </div>
      <p className="fallacy-explanation">{fallacy.explanation}</p>
      {fallacy.quote && (
        <blockquote className="fallacy-quote">
          "{fallacy.quote}"
        </blockquote>
      )}
    </div>
  );
}
