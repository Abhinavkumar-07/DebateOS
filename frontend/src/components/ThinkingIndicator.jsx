import './ThinkingIndicator.css';

const AGENT_LABELS = {
  prosecutor: { label: 'Prosecutor is building argument', icon: '🔵' },
  defender: { label: 'Defender is crafting counter', icon: '🔴' },
  judge: { label: 'Judge is evaluating', icon: '🟣' },
  fallacy_detector_pro: { label: 'Analyzing Prosecutor for fallacies', icon: '🔍' },
  fallacy_detector_def: { label: 'Analyzing Defender for fallacies', icon: '🔍' },
};

export default function ThinkingIndicator({ agent, side }) {
  if (!agent) return null;

  const info = AGENT_LABELS[agent] || { label: 'Processing...', icon: '⏳' };
  const sideClass = side || (agent.includes('pro') || agent === 'prosecutor' ? 'pro' : agent === 'defender' || agent.includes('def') ? 'def' : 'judge');

  return (
    <div className={`thinking-indicator thinking-${sideClass}`}>
      <span className="thinking-icon">{info.icon}</span>
      <span className="thinking-label">{info.label}</span>
      <div className="thinking-dots">
        <span className="dot" style={{ animationDelay: '0ms' }}>.</span>
        <span className="dot" style={{ animationDelay: '200ms' }}>.</span>
        <span className="dot" style={{ animationDelay: '400ms' }}>.</span>
      </div>
    </div>
  );
}
