import React from 'react';

/**
 * WorldMap — Tension meters per region.
 */
export default function WorldMap({ worldState }) {
  if (!worldState || !worldState.regions) return null;

  const regions = worldState.regions;

  const getTensionColor = (tension) => {
    if (tension >= 80) return 'bg-red-500';
    if (tension >= 60) return 'bg-amber-500';
    if (tension >= 40) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getTensionLabel = (tension) => {
    if (tension >= 80) return 'CRITICAL';
    if (tension >= 60) return 'HIGH';
    if (tension >= 40) return 'ELEVATED';
    return 'STABLE';
  };

  return (
    <div className="panel h-full flex flex-col">
      <div className="panel-header">◈ WORLD MAP — REGIONAL TENSIONS</div>
      <div className="p-3 flex-1 overflow-y-auto space-y-4">
        {Object.entries(regions).map(([key, region]) => (
          <div key={key} className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-300">
                {region.flag || '🌐'} {region.name || key.toUpperCase()}
              </span>
              <span
                className={`font-bold ${
                  region.tension >= 80
                    ? 'text-terminal-red'
                    : region.tension >= 60
                    ? 'text-terminal-amber'
                    : 'text-terminal-green'
                }`}
              >
                {region.tension}% — {getTensionLabel(region.tension)}
              </span>
            </div>
            <div className="tension-bar">
              <div
                className={`tension-fill ${getTensionColor(region.tension)}`}
                style={{ width: `${region.tension}%` }}
              />
            </div>
            {region.active_missions && region.active_missions.length > 0 && (
              <div className="text-[10px] text-gray-500 mt-1">
                ACTIVE: {region.active_missions.join(', ')}
              </div>
            )}
          </div>
        ))}

        {/* Compromised assets */}
        {worldState.compromised_assets && worldState.compromised_assets.length > 0 && (
          <div className="mt-4 pt-3 border-t border-terminal-border">
            <div className="text-xs text-terminal-red font-bold tracking-wider mb-1">
              ⚠ COMPROMISED ASSETS
            </div>
            {worldState.compromised_assets.map((asset) => (
              <div key={asset} className="text-xs text-red-400 ml-2">
                • {asset}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
