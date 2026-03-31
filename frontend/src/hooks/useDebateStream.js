/**
 * useDebateStream — SSE Hook for DebateOS
 * Manages EventSource connection to debate stream endpoint.
 * Parses SSE events into React state for live UI updates.
 */

import { useState, useCallback, useRef } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const EVENT_TYPES = [
  'DEBATE_START',
  'PRO_ARGUMENT',
  'PRO_FALLACY',
  'DEF_ARGUMENT',
  'DEF_FALLACY',
  'JUDGE_RESULT',
  'ROUND_SUMMARY',
  'FINAL_VERDICT',
  'ERROR',
  'STREAM_END',
];

export function useDebateStream() {
  const [events, setEvents] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState(null);
  const [currentRound, setCurrentRound] = useState(0);
  const [debateId, setDebateId] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, starting, streaming, completed, error
  const [thinkingAgent, setThinkingAgent] = useState(null);
  const eventSourceRef = useRef(null);

  // ─── Start a new debate ───────────────────────────────────
  const startDebate = useCallback(async (claim, rounds = 3) => {
    // Cleanup previous connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    // Reset state
    setEvents([]);
    setError(null);
    setCurrentRound(0);
    setStatus('starting');
    setIsStarting(true);
    setThinkingAgent(null);

    try {
      // Step 1: Create the debate
      const response = await fetch(`${API_BASE}/debate/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ claim, rounds }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Failed to start debate');
      }

      const data = await response.json();
      const newDebateId = data.debate_id;
      setDebateId(newDebateId);

      // Step 2: Connect to SSE stream
      const eventSource = new EventSource(`${API_BASE}/debate/${newDebateId}/stream`);
      eventSourceRef.current = eventSource;
      setIsStreaming(true);
      setIsStarting(false);
      setStatus('streaming');

      // Show prosecutor as first thinking agent
      setThinkingAgent('prosecutor');

      // Listen for all event types
      EVENT_TYPES.forEach((eventType) => {
        eventSource.addEventListener(eventType, (e) => {
          try {
            const eventData = JSON.parse(e.data);
            handleEvent(eventType, eventData);
          } catch (parseErr) {
            console.error('Failed to parse SSE event:', parseErr);
          }
        });
      });

      eventSource.onerror = (e) => {
        console.error('SSE connection error:', e);
        // Don't set error if the stream completed normally
        if (eventSource.readyState === EventSource.CLOSED) return;
        eventSource.close();
        setIsStreaming(false);
        setStatus('error');
        setError('Connection lost. The debate may still be running on the server.');
        setThinkingAgent(null);
      };

    } catch (err) {
      console.error('Failed to start debate:', err);
      setError(err.message);
      setIsStarting(false);
      setIsStreaming(false);
      setStatus('error');
      setThinkingAgent(null);
    }
  }, []);

  // ─── Handle individual events ─────────────────────────────
  const handleEvent = useCallback((eventType, eventData) => {
    setEvents((prev) => [...prev, { type: eventType, data: eventData, timestamp: Date.now() }]);

    switch (eventType) {
      case 'DEBATE_START':
        setCurrentRound(0);
        setThinkingAgent('prosecutor');
        break;

      case 'PRO_ARGUMENT':
        setCurrentRound(eventData.round || 0);
        // After PRO argues, fallacy detector runs
        setThinkingAgent('fallacy_detector_pro');
        break;

      case 'PRO_FALLACY':
        // After PRO fallacy check, defender thinks
        setThinkingAgent('defender');
        break;

      case 'DEF_ARGUMENT':
        // After DEF argues, fallacy detector runs
        setThinkingAgent('fallacy_detector_def');
        break;

      case 'DEF_FALLACY':
        // After DEF fallacy check, judge evaluates
        setThinkingAgent('judge');
        break;

      case 'JUDGE_RESULT':
        // Judge done, waiting for round summary
        setThinkingAgent(null);
        break;

      case 'ROUND_SUMMARY':
        // Round complete. If not early stop, prosecutor thinks next
        if (!eventData.content?.early_stop) {
          setThinkingAgent('prosecutor');
        } else {
          setThinkingAgent(null);
        }
        break;

      case 'FINAL_VERDICT':
        setIsStreaming(false);
        setStatus('completed');
        setThinkingAgent(null);
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
          eventSourceRef.current = null;
        }
        break;

      case 'STREAM_END':
        setIsStreaming(false);
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
          eventSourceRef.current = null;
        }
        break;

      case 'ERROR':
        setError(eventData.content?.error || 'Unknown error');
        setStatus('error');
        setThinkingAgent(null);
        break;

      default:
        break;
    }
  }, []);

  // ─── Reset debate ─────────────────────────────────────────
  const resetDebate = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setEvents([]);
    setIsStreaming(false);
    setIsStarting(false);
    setError(null);
    setCurrentRound(0);
    setDebateId(null);
    setStatus('idle');
    setThinkingAgent(null);
  }, []);

  // ─── Derived state helpers ────────────────────────────────
  const proArguments = events
    .filter((e) => e.type === 'PRO_ARGUMENT')
    .map((e) => ({ ...e.data.content, round: e.data.round }));

  const defArguments = events
    .filter((e) => e.type === 'DEF_ARGUMENT')
    .map((e) => ({ ...e.data.content, round: e.data.round }));

  const proFallacies = events
    .filter((e) => e.type === 'PRO_FALLACY')
    .map((e) => ({ ...e.data.content, round: e.data.round }));

  const defFallacies = events
    .filter((e) => e.type === 'DEF_FALLACY')
    .map((e) => ({ ...e.data.content, round: e.data.round }));

  const judgeResults = events
    .filter((e) => e.type === 'JUDGE_RESULT')
    .map((e) => ({ ...e.data.content, round: e.data.round }));

  const roundSummaries = events
    .filter((e) => e.type === 'ROUND_SUMMARY')
    .map((e) => e.data.content);

  const finalVerdict = events.find((e) => e.type === 'FINAL_VERDICT')?.data?.content || null;

  return {
    // Actions
    startDebate,
    resetDebate,

    // State
    events,
    isStreaming,
    isStarting,
    error,
    currentRound,
    debateId,
    status,
    thinkingAgent,

    // Derived
    proArguments,
    defArguments,
    proFallacies,
    defFallacies,
    judgeResults,
    roundSummaries,
    finalVerdict,
  };
}
