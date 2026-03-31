import ThinkingIndicator from './ThinkingIndicator';
import './JudgePanel.css';

export default function JudgePanel({ judgeResults, thinkingAgent, currentRound }) {
  const isThinking = thinkingAgent === 'judge';

  if (judgeResults.length === 0 && !isThinking) return null;

  return (
    <div className="judge-panel glass-card" id="judge-panel">
      <div className="judge-panel-header">
        <div className="judge-title-row">
          <span className="judge-icon">⚖️</span>
          <div>
            <h3 className="judge-title">Judge</h3>
            <p className="judge-subtitle">Evaluating logic, evidence, and rhetoric</p>
          </div>
        </div>
      </div>

      <div className="judge-panel-body">
        {isThinking && (
          <ThinkingIndicator agent="judge" side="judge" />
        )}

        {judgeResults.map((result, index) => (
          <div key={index} className="judge-round-result animate-slide-up">
            <div className="judge-result-header">
              <span className="judge-result-round">Round {result.round || index + 1}</span>
              <span className={`judge-result-winner winner-${result.winner?.toLowerCase()}`}>
                Winner: {result.winner}
              </span>
              <span className="judge-confidence">
                Confidence: {result.confidence}%
              </span>
            </div>
            {result.reasoning && (
              <p className="judge-reasoning">{result.reasoning}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
