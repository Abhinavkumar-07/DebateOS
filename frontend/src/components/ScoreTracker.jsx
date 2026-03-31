import './ScoreTracker.css';

export default function ScoreTracker({ judgeResults, roundSummaries }) {
  if (!judgeResults || judgeResults.length === 0) return null;

  return (
    <div className="score-tracker animate-slide-up" id="score-tracker">
      <h3 className="score-tracker-title">📊 Score Tracker</h3>
      <div className="score-rounds">
        {judgeResults.map((result, index) => (
          <div key={index} className="score-round-card glass-card">
            <div className="score-round-header">
              <span className="score-round-label">Round {result.round || index + 1}</span>
              <span className={`score-round-winner winner-${result.winner?.toLowerCase()}`}>
                {result.winner === 'PRO' ? '🔵' : '🔴'} {result.winner} wins
              </span>
            </div>

            <div className="score-comparison">
              {/* PRO Scores */}
              <div className="score-side score-side-pro">
                <span className="score-side-label">Prosecutor</span>
                <ScoreBar label="Logic" value={result.pro_scores?.logic_score} max={10} color="pro" />
                <ScoreBar label="Evidence" value={result.pro_scores?.evidence_score} max={10} color="pro" />
                <ScoreBar label="Rhetoric" value={result.pro_scores?.rhetoric_score} max={10} color="pro" />
                {result.pro_fallacy_penalty > 0 && (
                  <div className="penalty-row">
                    <span className="penalty-label">⚠️ Fallacy Penalty</span>
                    <span className="penalty-value">-{result.pro_fallacy_penalty}</span>
                  </div>
                )}
                <div className="score-final">
                  <span>Final</span>
                  <span className="score-final-value pro-text">{result.pro_final_score}</span>
                </div>
              </div>

              <div className="score-vs">VS</div>

              {/* DEF Scores */}
              <div className="score-side score-side-def">
                <span className="score-side-label">Defender</span>
                <ScoreBar label="Logic" value={result.def_scores?.logic_score} max={10} color="def" />
                <ScoreBar label="Evidence" value={result.def_scores?.evidence_score} max={10} color="def" />
                <ScoreBar label="Rhetoric" value={result.def_scores?.rhetoric_score} max={10} color="def" />
                {result.def_fallacy_penalty > 0 && (
                  <div className="penalty-row">
                    <span className="penalty-label">⚠️ Fallacy Penalty</span>
                    <span className="penalty-value">-{result.def_fallacy_penalty}</span>
                  </div>
                )}
                <div className="score-final">
                  <span>Final</span>
                  <span className="score-final-value def-text">{result.def_final_score}</span>
                </div>
              </div>
            </div>

            {result.reasoning && (
              <p className="score-reasoning">💭 {result.reasoning}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function ScoreBar({ label, value, max, color }) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));

  return (
    <div className="score-bar-row">
      <span className="score-bar-label">{label}</span>
      <div className="score-bar-track">
        <div
          className={`score-bar-fill bar-${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="score-bar-value">{value}</span>
    </div>
  );
}
