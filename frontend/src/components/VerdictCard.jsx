import './VerdictCard.css';

export default function VerdictCard({ verdict, claim, onNewDebate }) {
  if (!verdict) return null;

  const winnerIsPro = verdict.winner === 'PRO';
  const winnerLabel = winnerIsPro ? 'Prosecutor' : 'Defender';
  const winnerIcon = winnerIsPro ? '⚔️' : '🛡️';

  return (
    <div className="verdict-overlay animate-fade-in" id="verdict-overlay">
      <div className="verdict-card animate-scale-in glass-card">
        {/* Crown/Winner */}
        <div className={`verdict-crown ${winnerIsPro ? 'crown-pro' : 'crown-def'}`}>
          <span className="crown-icon">👑</span>
        </div>

        <h2 className="verdict-title">Final Verdict</h2>
        <p className="verdict-claim">"{claim}"</p>

        <div className={`verdict-winner ${winnerIsPro ? 'winner-pro' : 'winner-def'}`}>
          <span className="verdict-winner-icon">{winnerIcon}</span>
          <span className="verdict-winner-label">{winnerLabel} Wins!</span>
        </div>

        {/* Score Summary */}
        <div className="verdict-scores">
          <div className="verdict-score-card score-card-pro">
            <span className="verdict-score-label">🔵 Prosecutor</span>
            <span className="verdict-score-value">{verdict.pro_total_score}</span>
            <span className="verdict-score-wins">{verdict.pro_round_wins} round{verdict.pro_round_wins !== 1 ? 's' : ''} won</span>
          </div>
          <div className="verdict-score-divider">vs</div>
          <div className="verdict-score-card score-card-def">
            <span className="verdict-score-label">🔴 Defender</span>
            <span className="verdict-score-value">{verdict.def_total_score}</span>
            <span className="verdict-score-wins">{verdict.def_round_wins} round{verdict.def_round_wins !== 1 ? 's' : ''} won</span>
          </div>
        </div>

        {/* Confidence Meter */}
        <div className="verdict-confidence">
          <div className="confidence-header">
            <span className="confidence-label">Confidence</span>
            <span className="confidence-value">{verdict.confidence}%</span>
          </div>
          <div className="confidence-track">
            <div
              className="confidence-fill"
              style={{ width: `${verdict.confidence}%` }}
            />
          </div>
        </div>

        {/* Summary */}
        <p className="verdict-summary">{verdict.summary}</p>

        {/* Meta */}
        <div className="verdict-meta">
          <span>📊 {verdict.total_rounds_played} rounds played</span>
        </div>

        <button className="verdict-new-btn" onClick={onNewDebate} id="new-debate-btn">
          🔄 New Debate
        </button>
      </div>
    </div>
  );
}
