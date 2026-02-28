import React, { useState, useEffect } from 'react';

/**
 * AlertBanner — Rogue event notifications with auto-dismiss + game-over overlay.
 */
export default function AlertBanner({ alerts, gameOver, onNewGame }) {
  const [visibleAlerts, setVisibleAlerts] = useState([]);

  useEffect(() => {
    if (alerts && alerts.length > 0) {
      setVisibleAlerts((prev) => [...prev, ...alerts]);

      // Auto-dismiss non-critical alerts after 15 seconds
      const timer = setTimeout(() => {
        setVisibleAlerts((prev) =>
          prev.filter((a) => a.severity === 'critical')
        );
      }, 15000);

      return () => clearTimeout(timer);
    }
  }, [alerts]);

  const dismissAlert = (index) => {
    setVisibleAlerts((prev) => prev.filter((_, i) => i !== index));
  };

  const getSeverityStyle = (severity) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-900/80 border-red-500 text-red-200';
      case 'warning':
        return 'bg-amber-900/60 border-amber-500 text-amber-200';
      default:
        return 'bg-terminal-panel border-terminal-border text-gray-300';
    }
  };

  return (
    <>
      {/* Game Over Overlay */}
      {gameOver && gameOver.game_over && (
        <div className="game-over-overlay">
          <div className="text-center max-w-lg px-8">
            <div className="text-terminal-red text-3xl font-bold tracking-widest mb-4 alert-flash">
              ◆ GAME OVER ◆
            </div>
            <div className="text-gray-300 text-sm leading-relaxed mb-6 whitespace-pre-wrap">
              {gameOver.reason}
            </div>
            <div className="text-gray-600 text-xs mb-6 tracking-wider">
              TYPE: {gameOver.type?.toUpperCase()}
            </div>
            <button
              onClick={onNewGame}
              className="px-6 py-2 bg-terminal-green/20 text-terminal-green border border-terminal-green/50 rounded text-xs font-bold tracking-widest hover:bg-terminal-green/30 transition-colors btn-glow"
            >
              ◆ NEW OPERATION
            </button>
          </div>
        </div>
      )}

      {/* Alert banners */}
      {visibleAlerts.length > 0 && (
        <div className="fixed top-12 right-4 z-50 space-y-2 max-w-md">
          {visibleAlerts.map((alert, index) => (
            <div
              key={index}
              className={`transmission-enter border rounded p-3 shadow-lg ${getSeverityStyle(
                alert.severity
              )}`}
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="text-xs font-bold tracking-wider mb-1">
                    {alert.title || 'ALERT'}
                  </div>
                  <div className="text-[11px] leading-relaxed">
                    {alert.narration
                      ? alert.narration.substring(0, 200) + (alert.narration.length > 200 ? '...' : '')
                      : 'Details pending...'}
                  </div>
                </div>
                <button
                  onClick={() => dismissAlert(index)}
                  className="text-gray-500 hover:text-white text-xs flex-shrink-0"
                >
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
