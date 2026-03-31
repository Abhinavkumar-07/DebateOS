import { useState } from 'react';
import { useDebateStream } from './hooks/useDebateStream';
import ClaimInput from './components/ClaimInput';
import DebateArena from './components/DebateArena';
import './App.css';

export default function App() {
  const [activeClaim, setActiveClaim] = useState(null);

  const {
    startDebate,
    resetDebate,
    isStreaming,
    isStarting,
    error,
    currentRound,
    status,
    thinkingAgent,
    proArguments,
    defArguments,
    proFallacies,
    defFallacies,
    judgeResults,
    roundSummaries,
    finalVerdict,
  } = useDebateStream();

  const handleStartDebate = (claim) => {
    setActiveClaim(claim);
    startDebate(claim, 3);
  };

  const handleNewDebate = () => {
    setActiveClaim(null);
    resetDebate();
  };

  const isActive = status !== 'idle';

  return (
    <div className="app">
      {/* ─── Header ─── */}
      <header className="app-header">
        <div className="app-logo" onClick={handleNewDebate} style={{ cursor: 'pointer' }}>
          <div className="app-logo-icon">⚡</div>
          <div>
            <h1>DebateOS</h1>
            <span>Adversarial AI Reasoning Engine</span>
          </div>
        </div>
      </header>

      {/* ─── Main ─── */}
      <main className="app-main">
        {/* Claim Input */}
        <ClaimInput
          onSubmit={handleStartDebate}
          disabled={isStreaming || isStarting}
          compact={isActive}
        />

        {/* Error Display */}
        {error && (
          <div className="error-banner animate-slide-up">
            <span>⚠️ {error}</span>
            <button onClick={handleNewDebate} className="error-retry-btn">
              Try Again
            </button>
          </div>
        )}

        {/* Debate Arena */}
        {isActive && activeClaim && (
          <DebateArena
            claim={activeClaim}
            proArguments={proArguments}
            defArguments={defArguments}
            proFallacies={proFallacies}
            defFallacies={defFallacies}
            judgeResults={judgeResults}
            roundSummaries={roundSummaries}
            finalVerdict={finalVerdict}
            thinkingAgent={thinkingAgent}
            currentRound={currentRound}
            status={status}
            onNewDebate={handleNewDebate}
          />
        )}
      </main>
    </div>
  );
}
