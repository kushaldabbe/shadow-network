import React from 'react';

/**
 * IntelBrief — Orchestrator's intelligence briefing + world event with actions.
 */
export default function IntelBrief({ briefing, currentEvent, onEventAction, isLoading }) {
  return (
    <div className="panel h-full flex flex-col">
      <div className="panel-header">◈ INTELLIGENCE BRIEFING</div>
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {/* Current World Event */}
        {currentEvent && (
          <div className="bg-terminal-amber/5 border border-terminal-amber/20 rounded p-2">
            <div className="text-[10px] text-terminal-amber tracking-wider font-bold mb-1">
              ⚡ WORLD EVENT — TURN {currentEvent.turn || '?'}
            </div>
            <div className="text-xs text-amber-300 font-bold mb-1">
              {currentEvent.event_title}
            </div>
            <div className="text-xs text-gray-300 leading-relaxed mb-2 whitespace-pre-wrap">
              {currentEvent.event_description}
            </div>

            {/* Suggested actions */}
            {currentEvent.suggested_actions && currentEvent.suggested_actions.length > 0 && (
              <div className="space-y-1 mt-2">
                <div className="text-[10px] text-gray-500 tracking-wider">
                  RECOMMENDED ACTIONS
                </div>
                {currentEvent.suggested_actions.map((action, i) => (
                  <button
                    key={i}
                    onClick={() => onEventAction && onEventAction(action)}
                    disabled={isLoading}
                    className="w-full text-left text-[10px] text-gray-400 hover:text-terminal-green px-2 py-1 rounded hover:bg-terminal-green/5 transition-colors border border-transparent hover:border-terminal-green/20"
                  >
                    {i + 1}. {action}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Briefing text */}
        {briefing ? (
          <div>
            <div className="text-[10px] text-gray-500 tracking-wider mb-1">SITUATION REPORT</div>
            <div className="text-xs text-gray-300 leading-relaxed whitespace-pre-wrap">
              {briefing}
            </div>
          </div>
        ) : (
          <div className="text-xs text-gray-600 text-center py-4">
            {isLoading ? (
              <span>
                Generating briefing<span className="loading-dots"></span>
              </span>
            ) : (
              'Start a turn to receive your intelligence briefing.'
            )}
          </div>
        )}
      </div>
    </div>
  );
}
