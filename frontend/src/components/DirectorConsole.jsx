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
      <div className="p-3 flex flex-col flex-1">
        {/* Operative selector */}
        <div className="mb-3">
          <label className="text-[10px] text-gray-500 tracking-wider block mb-1">
            TARGET OPERATIVE
          </label>
          <select
            value={selectedOperative}
            onChange={(e) => setSelectedOperative(e.target.value)}
            className="w-full bg-black/50 border border-terminal-border rounded px-2 py-1.5 text-xs text-terminal-green focus:border-terminal-green focus:outline-none"
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
        <form onSubmit={handleSubmit} className="flex-1 flex flex-col">
          <label className="text-[10px] text-gray-500 tracking-wider block mb-1">
            MISSION ORDER
          </label>
          <textarea
            value={orderText}
            onChange={(e) => setOrderText(e.target.value)}
            placeholder="Type your order to the operative..."
            className="flex-1 bg-black/50 border border-terminal-border rounded px-2 py-1.5 text-xs text-gray-200 focus:border-terminal-green focus:outline-none resize-none min-h-[60px]"
            disabled={isLoading}
          />

          <button
            type="submit"
            disabled={!orderText.trim() || isLoading}
            className={`mt-2 w-full py-2 rounded text-xs font-bold tracking-widest transition-all btn-glow ${
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
        <div className="mt-3 pt-2 border-t border-terminal-border">
          <div className="text-[10px] text-gray-600 tracking-wider mb-1">SAMPLE MISSIONS</div>
          <div className="space-y-1">
            {quickOrders.map((order, i) => (
              <button
                key={i}
                onClick={() => handleQuickOrder(order)}
                className="w-full text-left text-[10px] text-gray-500 hover:text-terminal-green px-1.5 py-1 rounded hover:bg-terminal-green/5 transition-colors truncate"
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
