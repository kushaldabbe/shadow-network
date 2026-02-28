import React, { useRef, useEffect, useState } from 'react';

/**
 * TransmissionLog — Scrollable log of operative transmissions with audio playback.
 */
export default function TransmissionLog({ transmissions, onPlayAudio, pendingOrder }) {
  const logEndRef = useRef(null);
  const [playingId, setPlayingId] = useState(null);

  // Auto-scroll to bottom on new transmissions
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transmissions]);

  const handlePlay = async (transmission) => {
    if (playingId === transmission.id) {
      setPlayingId(null);
      return;
    }
    setPlayingId(transmission.id);
    if (onPlayAudio) {
      await onPlayAudio(transmission.codename, transmission.response);
    }
    setPlayingId(null);
  };

  const getCodeColor = (codename) => {
    const colors = {
      NIGHTHAWK: 'text-cyan-400',
      CEDAR: 'text-green-400',
      GHOST: 'text-yellow-400',
      SABLE: 'text-purple-400',
      LOTUS: 'text-pink-400',
    };
    return colors[codename] || 'text-terminal-green';
  };

  const getRiskBadge = (risk) => {
    const badges = {
      low: 'bg-green-900/50 text-green-400 border-green-800',
      medium: 'bg-yellow-900/50 text-yellow-400 border-yellow-800',
      high: 'bg-red-900/50 text-red-400 border-red-800',
      critical: 'bg-red-900/80 text-red-300 border-red-600 alert-flash',
    };
    return badges[risk] || badges.medium;
  };

  if ((!transmissions || transmissions.length === 0) && !pendingOrder) {
    return (
      <div className="panel h-full flex flex-col">
        <div className="panel-header">◈ TRANSMISSION LOG</div>
        <div className="p-3 flex-1 flex items-center justify-center">
          <div className="text-gray-600 text-xs text-center">
            <div className="mb-2">No transmissions received</div>
            <div className="text-gray-700">Issue an order to begin</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="panel h-full flex flex-col">
      <div className="panel-header flex items-center justify-between">
        <span>◈ TRANSMISSION LOG</span>
        <span className="text-gray-500 text-[10px]">{transmissions.length} entries</span>
      </div>
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {/* Pending transmission indicator */}
        {pendingOrder && (
          <div className="transmission-enter bg-black/30 border border-terminal-amber/30 rounded p-2">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 bg-terminal-amber rounded-full animate-pulse" />
              <span className="text-terminal-amber text-xs font-bold tracking-wider">
                TRANSMITTING{pendingOrder.operative ? ` TO ${pendingOrder.operative}` : ''}
              </span>
            </div>
            <div className="text-[10px] text-gray-500 italic mb-2">
              ORDER: {pendingOrder.order}
            </div>
            <div className="flex items-center gap-1 text-[10px] text-gray-600">
              <span className="inline-block w-1.5 h-1.5 bg-terminal-green rounded-full animate-pulse" />
              <span>Encrypting transmission</span>
              <span className="loading-dots"></span>
            </div>
            <div className="mt-2 h-1 bg-gray-900 rounded overflow-hidden">
              <div className="h-full bg-terminal-amber/50 rounded animate-[transmitPulse_2s_ease-in-out_infinite]" style={{ width: '60%' }} />
            </div>
          </div>
        )}

        {transmissions.map((t) => (
          <div
            key={t.id}
            className="transmission-enter bg-black/30 border border-terminal-border rounded p-2"
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className={`font-bold text-xs tracking-wider ${getCodeColor(t.codename)}`}>
                  {t.codename}
                </span>
                {t.risk_level && (
                  <span
                    className={`text-[9px] px-1.5 py-0.5 rounded border ${getRiskBadge(
                      t.risk_level
                    )}`}
                  >
                    {t.risk_level.toUpperCase()}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handlePlay(t)}
                  className="text-terminal-green/60 hover:text-terminal-green text-xs transition-colors"
                  title="Play audio transmission"
                >
                  {playingId === t.id ? '⏹' : '🔊'}
                </button>
                <span className="text-gray-600 text-[10px]">T{t.turn}</span>
              </div>
            </div>

            {/* Order */}
            <div className="text-[10px] text-gray-500 mb-1 italic">
              ORDER: {t.order}
            </div>

            {/* Response */}
            <div className="text-xs text-gray-300 leading-relaxed whitespace-pre-wrap">
              {t.response}
            </div>
          </div>
        ))}
        <div ref={logEndRef} />
      </div>
    </div>
  );
}
