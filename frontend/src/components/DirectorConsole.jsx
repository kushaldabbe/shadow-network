import React, { useState } from 'react';

/**
 * DirectorConsole — Order input with operative dropdown + TRANSMIT button.
 */
export default function DirectorConsole({ operatives, onSendOrder, isLoading }) {
  const [selectedOperative, setSelectedOperative] = useState('');
  const [orderText, setOrderText] = useState('');

  const quickOrders = [
    { label: 'Investigate the uranium smuggling ring near the border', icon: '☢' },
    { label: 'Establish contact with the defecting double agent', icon: '🕵' },
    { label: 'Report all known intel on recent embassy surveillance', icon: '📡' },
    { label: 'Conduct dead drop exchange at the designated safe house', icon: '📦' },
    { label: 'Monitor suspect arms dealer movements in the region', icon: '🔍' },
    { label: 'Extract compromised asset before cover is blown', icon: '🚁' },
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!orderText.trim() || isLoading) return;

    onSendOrder(orderText, selectedOperative || null);
    setOrderText('');
  };

  const handleQuickOrder = (order) => {
    setOrderText(order.label || order);
  };

  const activeOperatives = (operatives || []).filter((op) => op.status === 'active');

  return (
    <div className="panel h-full flex flex-col">
      <div className="panel-header">◈ DIRECTOR CONSOLE</div>
      <div className="p-2 flex flex-col flex-1 overflow-y-auto min-h-0">
        {/* Operative selector */}
        <div className="mb-2">
          <label className="text-[9px] text-gray-500 tracking-wider block mb-0.5">
            TARGET OPERATIVE
          </label>
          <select
            value={selectedOperative}
            onChange={(e) => setSelectedOperative(e.target.value)}
            className="w-full bg-black/50 border border-terminal-border rounded px-2 py-1 text-[11px] text-terminal-green focus:border-terminal-green focus:outline-none"
          >
            <option value="">AUTO-ROUTE (Orchestrator decides)</option>
            {activeOperatives.map((op) => (
              <option key={op.codename} value={op.codename}>
                {op.codename} — {op.location}
              </option>
            ))}
          </select>
        </div>

        {/* Order input */}
        <form onSubmit={handleSubmit} className="flex flex-col">
          <label className="text-[9px] text-gray-500 tracking-wider block mb-0.5">
            MISSION ORDER
          </label>
          <textarea
            value={orderText}
            onChange={(e) => setOrderText(e.target.value)}
            placeholder="Type your order to the operative..."
            className="bg-black/50 border border-terminal-border rounded px-2 py-1 text-xs text-gray-200 focus:border-terminal-green focus:outline-none resize-none h-[48px]"
            disabled={isLoading}
          />

          <button
            type="submit"
            disabled={!orderText.trim() || isLoading}
            className={`mt-1.5 w-full py-1.5 rounded text-[11px] font-bold tracking-widest transition-all btn-glow ${
              isLoading
                ? 'bg-gray-800 text-gray-600 cursor-wait'
                : orderText.trim()
                ? 'bg-terminal-green/20 text-terminal-green border border-terminal-green/50 hover:bg-terminal-green/30'
                : 'bg-gray-900 text-gray-600 border border-gray-800 cursor-not-allowed'
            }`}
          >
            {isLoading ? (
              <span>
                TRANSMITTING<span className="loading-dots"></span>
              </span>
            ) : (
              '◆ TRANSMIT ORDER'
            )}
          </button>
        </form>

        {/* Quick orders */}
        <div className="mt-2 pt-1.5 border-t border-terminal-border">
          <div className="text-[9px] text-gray-600 tracking-wider mb-0.5">SAMPLE MISSIONS</div>
          <div className="space-y-px">
            {quickOrders.map((order, i) => (
              <button
                key={i}
                onClick={() => handleQuickOrder(order)}
                className="w-full text-left text-[10px] text-gray-500 hover:text-terminal-green px-1.5 py-0.5 rounded hover:bg-terminal-green/5 transition-colors truncate"
                disabled={isLoading}
              >
                {order.icon} {order.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
