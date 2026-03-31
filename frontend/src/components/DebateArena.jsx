import AgentPanel from './AgentPanel';
import ScoreTracker from './ScoreTracker';
import JudgePanel from './JudgePanel';
import VerdictCard from './VerdictCard';
import './DebateArena.css';

export default function DebateArena({
  claim,
  proArguments,
  defArguments,
  proFallacies,
  defFallacies,
  judgeResults,
  roundSummaries,
  finalVerdict,
  thinkingAgent,
  currentRound,
  status,
  onNewDebate,
}) {
  return (
    <div className="debate-arena" id="debate-arena">
      {/* Active Claim Banner */}
      <div className="debate-claim-banner glass-card animate-slide-up">
        <div className="claim-banner-content">
          <span className="claim-banner-label">Debating</span>
          <h2 className="claim-banner-text">"{claim}"</h2>
        </div>
        <div className="claim-banner-meta">
          {status === 'streaming' && (
            <span className="debate-status status-live">
              <span className="live-dot" /> LIVE — Round {currentRound}
            </span>
          )}
          {status === 'completed' && (
            <span className="debate-status status-done">✅ Completed</span>
          )}
        </div>
      </div>

      {/* Main Arena: PRO vs DEF */}
      <div className="arena-columns">
        <AgentPanel
          side="pro"
          arguments={proArguments}
          fallacies={proFallacies}
          thinkingAgent={thinkingAgent}
        />
        <AgentPanel
          side="def"
          arguments={defArguments}
          fallacies={defFallacies}
          thinkingAgent={thinkingAgent}
        />
      </div>

      {/* Score Tracker */}
      <ScoreTracker judgeResults={judgeResults} roundSummaries={roundSummaries} />

      {/* Judge Panel */}
      <JudgePanel
        judgeResults={judgeResults}
        thinkingAgent={thinkingAgent}
        currentRound={currentRound}
      />

      {/* Final Verdict Overlay */}
      <VerdictCard
        verdict={finalVerdict}
        claim={claim}
        onNewDebate={onNewDebate}
      />
    </div>
  );
}
