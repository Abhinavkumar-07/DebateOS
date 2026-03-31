import { useState } from 'react';
import './ClaimInput.css';

const DEMO_CLAIMS = [
  'AI will replace programmers',
  'Social media is harmful to society',
  'Remote work is better than office work',
];

export default function ClaimInput({ onSubmit, disabled, compact }) {
  const [claim, setClaim] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (claim.trim() && !disabled) {
      onSubmit(claim.trim());
    }
  };

  const handleDemo = (demoClaim) => {
    if (!disabled) {
      setClaim(demoClaim);
      onSubmit(demoClaim);
    }
  };

  return (
    <section className={`claim-input-section ${compact ? 'compact' : ''}`}>
      <div className="claim-hero-text">
        <h2>Enter a Claim to Debate</h2>
        <p>
          Watch AI agents argue for and against your claim with real-time
          fallacy detection and structured scoring.
        </p>
      </div>

      <form className="claim-input-group" onSubmit={handleSubmit}>
        <div className="claim-input-wrapper">
          <input
            type="text"
            className="claim-input"
            placeholder="e.g., AI will replace programmers within 10 years..."
            value={claim}
            onChange={(e) => setClaim(e.target.value)}
            disabled={disabled}
            id="claim-input"
            autoFocus
          />
        </div>
        <button
          type="submit"
          className="claim-submit-btn"
          disabled={!claim.trim() || disabled}
          id="start-debate-btn"
        >
          {disabled ? 'Debating...' : '⚔️ Start Debate'}
        </button>
      </form>

      <div className="demo-section">
        <p className="demo-label">Or try a demo claim</p>
        <div className="demo-claims">
          {DEMO_CLAIMS.map((dc) => (
            <button
              key={dc}
              className="demo-claim-btn"
              onClick={() => handleDemo(dc)}
              disabled={disabled}
              id={`demo-${dc.slice(0, 10).replace(/\s/g, '-').toLowerCase()}`}
            >
              💬 {dc}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
