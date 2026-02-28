import React from 'react';

/**
 * TopBar — Turn counter, threat level, exposure, trust.
 */
export default function TopBar({ worldState }) {
  if (!worldState) return null;

  const { turn, threat_level, agency_exposure_level, director_trust_score } = worldState;

  const threatColors = {
    LOW: 'text-terminal-green',
    MODERATE: 'text-terminal-amber',
    HIGH: 'text-terminal-red',
    CRITICAL: 'text-terminal-red alert-flash',
  };

  const getTrustColor = (score) => {
    if (score >= 70) return 'text-terminal-green';
    if (score >= 40) return 'text-terminal-amber';
    return 'text-terminal-red';
  };

  const getExposureColor = (level) => {
    if (level <= 30) return 'text-terminal-green';
    if (level <= 60) return 'text-terminal-amber';
    return 'text-terminal-red';
  };

  return (
    <div className="bg-terminal-panel border-b border-terminal-border px-4 py-1.5 flex items-center justify-between">
      {/* Title */}
      <div className="flex items-center gap-3">
        <span className="text-terminal-green font-bold text-xs tracking-widest">
          ◆ SHADOW NETWORK
        </span>
        <span className="text-gray-600 text-[10px]">|</span>
        <span className="text-gray-400 text-[10px] tracking-wider">DIRECTOR CONSOLE v1.0</span>
      </div>

      {/* Status indicators */}
      <div className="flex items-center gap-4 text-[11px]">
        {/* Turn */}
        <div className="flex items-center gap-2">
          <span className="text-gray-500 tracking-wider">TURN</span>
          <span className="text-terminal-green font-bold text-sm">{turn || 1}</span>
        </div>

        <span className="text-gray-700">│</span>

        {/* Threat Level */}
        <div className="flex items-center gap-2">
          <span className="text-gray-500 tracking-wider">THREAT</span>
          <span className={`font-bold ${threatColors[threat_level] || 'text-gray-400'}`}>
            {threat_level || 'UNKNOWN'}
          </span>
        </div>

        <span className="text-gray-700">│</span>

        {/* Exposure */}
        <div className="flex items-center gap-2">
          <span className="text-gray-500 tracking-wider">EXPOSURE</span>
          <span className={`font-bold ${getExposureColor(agency_exposure_level)}`}>
            {agency_exposure_level}%
          </span>
        </div>

        <span className="text-gray-700">│</span>

        {/* Trust */}
        <div className="flex items-center gap-2">
          <span className="text-gray-500 tracking-wider">TRUST</span>
          <span className={`font-bold ${getTrustColor(director_trust_score)}`}>
            {director_trust_score}%
          </span>
        </div>
      </div>
    </div>
  );
}
