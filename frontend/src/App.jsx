import React, { useState, useEffect, useCallback, useRef } from 'react';
import TopBar from './components/TopBar';
import WorldMap from './components/WorldMap';
import OperativePanel from './components/OperativePanel';
import TransmissionLog from './components/TransmissionLog';
import DirectorConsole from './components/DirectorConsole';
import IntelBrief from './components/IntelBrief';
import AlertBanner from './components/AlertBanner';
import { useGameApi } from './hooks/useGameApi';

export default function App() {
  // API
  const api = useGameApi();

  // State
  const [worldState, setWorldState] = useState(null);
  const [operatives, setOperatives] = useState([]);
  const [transmissions, setTransmissions] = useState([]);
  const [briefing, setBriefing] = useState('');
  const [currentEvent, setCurrentEvent] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [gameOver, setGameOver] = useState(null);
  const [selectedOperative, setSelectedOperative] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [turnStarted, setTurnStarted] = useState(false);
  const [statusMessage, setStatusMessage] = useState('Initializing secure connection...');

  const audioRef = useRef(null);

  // --- Data Fetching ---
  const refreshState = useCallback(async () => {
    try {
      const [ws, ops] = await Promise.all([
        api.getWorldState(),
        api.getOperatives(),
      ]);
      setWorldState(ws);
      setOperatives(ops);
    } catch (err) {
      console.error('Failed to refresh state:', err);
    }
  }, []);

  // Initial load
  useEffect(() => {
    refreshState().then(() => {
      setStatusMessage('Secure connection established. Ready for operations.');
    });
  }, [refreshState]);

  // --- Turn Management ---
  const handleStartTurn = async () => {
    setIsLoading(true);
    setStatusMessage('Generating world event and intelligence briefing...');
    try {
      const result = await api.startTurn();

      if (result.game_over) {
        setGameOver(result.game_over);
        return;
      }

      setCurrentEvent(result.event);
      setBriefing(result.briefing);
      setTurnStarted(true);
      setStatusMessage('Turn started. Awaiting your orders, Director.');
      await refreshState();
    } catch (err) {
      setStatusMessage(`Error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEndTurn = async () => {
    setIsLoading(true);
    setStatusMessage('Processing end of turn... checking autonomous triggers...');
    try {
      const result = await api.endTurn();

      if (result.game_over) {
        setGameOver(result.game_over);
        return;
      }

      // Handle rogue events
      if (result.rogue_events && result.rogue_events.length > 0) {
        setAlerts(result.rogue_events);
      }

      setTurnStarted(false);
      setCurrentEvent(null);
      setBriefing('');
      setStatusMessage(`Turn ${result.new_turn} ready. Threat level: ${result.threat_level}.`);
      await refreshState();
    } catch (err) {
      setStatusMessage(`Error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Order Handling ---
  const handleSendOrder = async (order, operative) => {
    setIsLoading(true);
    setStatusMessage(`Transmitting order${operative ? ` to ${operative}` : ''}...`);
    try {
      const orderText = operative ? `${operative}: ${order}` : order;
      const result = await api.issueOrder(orderText, operative);

      if (result.game_over) {
        setGameOver(result.game_over);
        return;
      }

      // Add transmission to log
      if (result.transmission) {
        setTransmissions((prev) => [...prev, result.transmission]);
      }

      // Update intel report
      if (result.intel_report) {
        setBriefing(result.intel_report);
      }

      setStatusMessage('Transmission received. Awaiting further orders.');
      await refreshState();
    } catch (err) {
      setStatusMessage(`Transmission error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Event Response ---
  const handleEventAction = async (action) => {
    setIsLoading(true);
    setStatusMessage(`Processing directive: ${action.substring(0, 50)}...`);
    try {
      await api.respondToEvent(action);
      setStatusMessage('Directive acknowledged.');
      await refreshState();
    } catch (err) {
      setStatusMessage(`Error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Audio ---
  const handlePlayAudio = async (codename, text) => {
    try {
      const audioUrl = await api.generateAudio(codename, text);
      if (audioUrl && audioRef.current) {
        audioRef.current.src = audioUrl;
        audioRef.current.play();
      }
    } catch (err) {
      console.error('Audio playback failed:', err);
    }
  };

  // --- New Game ---
  const handleNewGame = async () => {
    setIsLoading(true);
    try {
      await api.newGame();
      setWorldState(null);
      setOperatives([]);
      setTransmissions([]);
      setBriefing('');
      setCurrentEvent(null);
      setAlerts([]);
      setGameOver(null);
      setTurnStarted(false);
      setStatusMessage('New operation initialized. All systems nominal.');
      await refreshState();
    } catch (err) {
      setStatusMessage(`Error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-terminal-dark font-mono">
      {/* CRT overlay */}
      <div className="crt-overlay" />

      {/* Hidden audio element */}
      <audio ref={audioRef} className="hidden" />

      {/* Alert system */}
      <AlertBanner
        alerts={alerts}
        gameOver={gameOver}
        onNewGame={handleNewGame}
      />

      {/* Top Bar */}
      <TopBar worldState={worldState} />

      {/* Turn control bar */}
      <div className="bg-black/50 border-b border-terminal-border px-4 py-1.5 flex items-center justify-between">
        <div className="text-[10px] text-gray-500 flex-1 truncate">
          {statusMessage}
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {!turnStarted ? (
            <button
              onClick={handleStartTurn}
              disabled={isLoading}
              className="px-3 py-1 bg-terminal-green/20 text-terminal-green border border-terminal-green/40 rounded text-[10px] font-bold tracking-wider hover:bg-terminal-green/30 transition-colors disabled:opacity-50"
            >
              {isLoading ? 'PROCESSING...' : '▶ START TURN'}
            </button>
          ) : (
            <button
              onClick={handleEndTurn}
              disabled={isLoading}
              className="px-3 py-1 bg-terminal-amber/20 text-terminal-amber border border-terminal-amber/40 rounded text-[10px] font-bold tracking-wider hover:bg-terminal-amber/30 transition-colors disabled:opacity-50"
            >
              {isLoading ? 'PROCESSING...' : '⏭ END TURN'}
            </button>
          )}
          <button
            onClick={handleNewGame}
            disabled={isLoading}
            className="px-3 py-1 bg-terminal-red/10 text-terminal-red/60 border border-terminal-red/20 rounded text-[10px] tracking-wider hover:bg-terminal-red/20 hover:text-terminal-red transition-colors disabled:opacity-50"
          >
            ↺ RESET
          </button>
        </div>
      </div>

      {/* Main 4-panel layout */}
      <div className="flex-1 grid grid-cols-[280px_1fr] grid-rows-2 gap-px bg-terminal-border overflow-hidden">
        {/* Top Left: World Map */}
        <div className="row-span-1">
          <WorldMap worldState={worldState} />
        </div>

        {/* Top Right: Transmission Log */}
        <div className="row-span-1">
          <TransmissionLog
            transmissions={transmissions}
            onPlayAudio={handlePlayAudio}
          />
        </div>

        {/* Bottom Left: Operatives */}
        <div className="row-span-1">
          <OperativePanel
            operatives={operatives}
            selectedOperative={selectedOperative}
            onSelect={setSelectedOperative}
          />
        </div>

        {/* Bottom Right: Director Console + Intel Brief */}
        <div className="row-span-1 grid grid-rows-[1fr_1fr] gap-px bg-terminal-border">
          <DirectorConsole
            operatives={operatives}
            onSendOrder={handleSendOrder}
            isLoading={isLoading}
          />
          <IntelBrief
            briefing={briefing}
            currentEvent={currentEvent}
            onEventAction={handleEventAction}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  );
}
