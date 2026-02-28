import React from 'react';

/**
 * OperativePanel — Operative list with signal quality bars and status.
 */
export default function OperativePanel({ operatives, onSelect, selectedOperative }) {
  if (!operatives || operatives.length === 0) {
    return (
      <div className="panel h-full flex flex-col">
        <div className="panel-header">◈ OPERATIVES</div>
        <div className="p-3 text-xs text-gray-500">Loading operatives...</div>
      </div>
    );
  }

  const getStatusDot = (status) => {
    switch (status) {
      case 'active':
        return '🟢';
      case 'dark':
        return '🔴';
      case 'compromised':
        return '🟡';
      case 'extracted':
        return '⚪';
      default:
        return '⚫';
    }
  };

  const getSignalColor = (quality) => {
    if (quality >= 70) return 'bg-green-500';
    if (quality >= 50) return 'bg-yellow-500';
    if (quality >= 30) return 'bg-amber-500';
    return 'bg-red-500';
  };

  return (
    <div className="panel h-full flex flex-col">
      <div className="panel-header">◈ OPERATIVES — SIGNAL QUALITY</div>
      <div className="p-2 flex-1 overflow-y-auto space-y-1">
        {operatives.map((op) => (
          <div
            key={op.codename}
            onClick={() => onSelect && onSelect(op.codename)}
            className={`p-2 rounded cursor-pointer transition-colors text-xs ${
              selectedOperative === op.codename
                ? 'bg-terminal-green/10 border border-terminal-green/30'
                : 'hover:bg-white/5 border border-transparent'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span>{getStatusDot(op.status)}</span>
                <span
                  className={`font-bold tracking-wider ${
                    op.status === 'active'
                      ? 'text-terminal-green'
                      : op.status === 'dark'
                      ? 'text-terminal-red'
                      : 'text-gray-500'
                  }`}
                >
                  {op.codename}
                </span>
              </div>
              <span className="text-gray-500 text-[10px]">{op.status.toUpperCase()}</span>
            </div>

            <div className="flex items-center gap-2 ml-6 mb-1">
              <span className="text-gray-500 text-[10px] w-16">{op.location}</span>
            </div>

            {/* Signal quality bar */}
            <div className="ml-6 flex items-center gap-2">
              <div className="signal-bar flex-1">
                <div
                  className={`signal-fill ${getSignalColor(op.signal_quality)}`}
                  style={{ width: `${op.signal_quality}%` }}
                />
              </div>
              <span className="text-gray-500 text-[10px] w-8">{op.signal_quality}%</span>
            </div>

            {op.mission_count > 0 && (
              <div className="text-[10px] text-gray-600 ml-6 mt-1">
                {op.mission_count} mission{op.mission_count !== 1 ? 's' : ''} completed
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
