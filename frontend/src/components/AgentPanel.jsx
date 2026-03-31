import ArgumentBubble from './ArgumentBubble';
import FallacyAlert from './FallacyAlert';
import ThinkingIndicator from './ThinkingIndicator';
import './AgentPanel.css';

export default function AgentPanel({
  side,
  arguments: args,
  fallacies,
  thinkingAgent,
}) {
  const isPro = side === 'pro';
  const title = isPro ? 'Prosecutor' : 'Defender';
  const icon = isPro ? '⚔️' : '🛡️';
  const subtitle = isPro ? 'Argues FOR the claim' : 'Argues AGAINST the claim';

  // Determine if this panel's agent is thinking
  const isThinking =
    (isPro && thinkingAgent === 'prosecutor') ||
    (!isPro && thinkingAgent === 'defender');

  const isFallacyCheck =
    (isPro && thinkingAgent === 'fallacy_detector_pro') ||
    (!isPro && thinkingAgent === 'fallacy_detector_def');

  return (
    <div className={`agent-panel panel-${side}`} id={`panel-${side}`}>
      <div className={`agent-panel-header header-${side}`}>
        <div className="agent-title-row">
          <span className="agent-icon">{icon}</span>
          <div>
            <h3 className="agent-title">{title}</h3>
            <p className="agent-subtitle">{subtitle}</p>
          </div>
        </div>
        {args.length > 0 && (
          <span className="agent-round-count">{args.length} arg{args.length > 1 ? 's' : ''}</span>
        )}
      </div>

      <div className="agent-panel-body">
        {args.length === 0 && !isThinking && (
          <div className="agent-empty">
            <span className="agent-empty-icon">{isPro ? '🔵' : '🔴'}</span>
            <p>Waiting for debate to begin...</p>
          </div>
        )}

        {args.map((arg, index) => (
          <div key={index} className="argument-group">
            <ArgumentBubble
              argument={arg}
              side={side}
              round={arg.round || index + 1}
            />
            {fallacies[index] && (
              <FallacyAlert
                fallacy={fallacies[index]}
                side={side}
                round={arg.round || index + 1}
              />
            )}
          </div>
        ))}

        {isThinking && (
          <ThinkingIndicator agent={isPro ? 'prosecutor' : 'defender'} side={side} />
        )}

        {isFallacyCheck && (
          <ThinkingIndicator
            agent={isPro ? 'fallacy_detector_pro' : 'fallacy_detector_def'}
            side={side}
          />
        )}
      </div>
    </div>
  );
}
