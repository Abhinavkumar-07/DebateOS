import './ArgumentBubble.css';

export default function ArgumentBubble({ argument, side, round }) {
  const isPro = side === 'pro';

  return (
    <div
      className={`argument-bubble argument-${side} ${isPro ? 'animate-slide-left' : 'animate-slide-right'}`}
      id={`argument-${side}-round-${round}`}
    >
      <div className="argument-header">
        <span className={`argument-badge badge-${side}`}>
          {isPro ? '🔵' : '🔴'} Round {round}
        </span>
      </div>

      {isPro ? (
        <div className="argument-body">
          <div className="argument-field">
            <span className="field-label">Point</span>
            <p className="field-value">{argument.point}</p>
          </div>
          <div className="argument-field">
            <span className="field-label">Evidence</span>
            <p className="field-value">{argument.evidence}</p>
          </div>
          <div className="argument-field">
            <span className="field-label">Inference</span>
            <p className="field-value">{argument.inference}</p>
          </div>
        </div>
      ) : (
        <div className="argument-body">
          <div className="argument-field">
            <span className="field-label">Counter-Point</span>
            <p className="field-value">{argument.counter_point}</p>
          </div>
          <div className="argument-field">
            <span className="field-label">Weakness Exposed</span>
            <p className="field-value">{argument.weakness_exposed}</p>
          </div>
          <div className="argument-field">
            <span className="field-label">Alternative Evidence</span>
            <p className="field-value">{argument.alternative_evidence}</p>
          </div>
        </div>
      )}
    </div>
  );
}
