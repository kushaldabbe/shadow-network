/**
 * useGameApi — API integration hook for Shadow Network frontend.
 */

const API_BASE = '/api';

async function apiCall(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  };

  const response = await fetch(url, config);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  // Handle audio responses
  if (response.headers.get('content-type')?.includes('audio')) {
    return response.blob();
  }

  return response.json();
}

export function useGameApi() {
  // World state
  const getWorldState = () => apiCall('/world-state');

  // Operatives
  const getOperatives = () => apiCall('/operatives');

  // Issue order
  const issueOrder = (order, operative = null) =>
    apiCall('/order', {
      method: 'POST',
      body: JSON.stringify({ order, operative }),
    });

  // Turn management
  const startTurn = () => apiCall('/start-turn', { method: 'POST' });
  const endTurn = () => apiCall('/end-turn', { method: 'POST' });

  // Respond to event
  const respondToEvent = (action) =>
    apiCall('/respond-to-event', {
      method: 'POST',
      body: JSON.stringify({ action }),
    });

  // Transmissions
  const getTransmissions = () => apiCall('/transmissions');

  // Briefing
  const getBriefing = () => apiCall('/briefing');

  // Rogue events
  const getRogueEvents = () => apiCall('/rogue-events');

  // Extract operative
  const extractOperative = (codename) =>
    apiCall('/extract', {
      method: 'POST',
      body: JSON.stringify({ codename }),
    });

  // New game
  const newGame = () => apiCall('/new-game', { method: 'POST' });

  // Game over check
  const checkGameOver = () => apiCall('/game-over');

  // Audio generation
  const generateAudio = async (codename, text) => {
    try {
      const blob = await apiCall(`/audio/generate/${codename}`, {
        method: 'POST',
        body: JSON.stringify({ text }),
      });
      return URL.createObjectURL(blob);
    } catch {
      return null;
    }
  };

  return {
    getWorldState,
    getOperatives,
    issueOrder,
    startTurn,
    endTurn,
    respondToEvent,
    getTransmissions,
    getBriefing,
    getRogueEvents,
    extractOperative,
    newGame,
    checkGameOver,
    generateAudio,
  };
}
