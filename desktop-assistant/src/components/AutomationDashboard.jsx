import React, { useState, useEffect } from 'react';
import { Mic, MicOff, Eye, EyeOff, Terminal } from 'lucide-react';

const AutomationDashboard = () => {
  const [isListening, setIsListening] = useState(false);
  const [isWatching, setIsWatching] = useState(false);
  const [commandLog, setCommandLog] = useState([]);
  const [status, setStatus] = useState('Idle');
  const [error, setError] = useState(null);

  const API_URL = 'http://localhost:5000';

  const toggleListening = async () => {
    try {
      setError(null);
      const response = await fetch(`${API_URL}/toggle-voice`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ enabled: !isListening })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setIsListening(data.voice_enabled);
      setStatus(data.voice_enabled ? 'Listening...' : 'Idle');
    } catch (err) {
      console.error('Error:', err);
      setError(`Failed to toggle voice: ${err.message}`);
      setStatus('Error');
    }
  };

  const toggleWatching = async () => {
    try {
      setError(null);
      const response = await fetch(`${API_URL}/toggle-visual`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ enabled: !isWatching })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setIsWatching(data.visual_enabled);
    } catch (err) {
      console.error('Error:', err);
      setError(`Failed to toggle visual: ${err.message}`);
    }
  };

  // Fetch command history periodically
  useEffect(() => {
    const fetchCommandHistory = async () => {
      try {
        const response = await fetch(`${API_URL}/command-history`);
        if (response.ok) {
          const data = await response.json();
          setCommandLog(data.history || []);
        }
      } catch (err) {
        console.error('Error fetching history:', err);
      }
    };

    const interval = setInterval(fetchCommandHistory, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Desktop Assistant</h1>
          <p className="text-gray-600">Your personal automation system</p>
          {error && (
            <div className="mt-4 p-4 bg-red-100 text-red-700 rounded-lg">
              {error}
            </div>
          )}
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Control Panel */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Control Panel</h2>
            <div className="flex space-x-4">
              <button
                onClick={toggleListening}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
                  isListening ? 'bg-red-500 text-white' : 'bg-gray-200 text-gray-700'
                }`}
              >
                {isListening ? <Mic className="h-5 w-5" /> : <MicOff className="h-5 w-5" />}
                <span>{isListening ? 'Stop Listening' : 'Start Listening'}</span>
              </button>

              <button
                onClick={toggleWatching}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
                  isWatching ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
                }`}
              >
                {isWatching ? <Eye className="h-5 w-5" /> : <EyeOff className="h-5 w-5" />}
                <span>{isWatching ? 'Stop Watching' : 'Start Watching'}</span>
              </button>
            </div>

            <div className="mt-4">
              <div className="bg-gray-100 p-4 rounded-lg">
                <p className="text-sm font-medium text-gray-700">Status: {status}</p>
              </div>
            </div>
          </div>

          {/* Command Log */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Command Log</h2>
            <div className="bg-gray-900 text-green-400 p-4 rounded-lg h-64 overflow-y-auto font-mono">
              {commandLog.length === 0 ? (
                <p className="text-gray-500">No commands executed yet...</p>
              ) : (
                commandLog.map((cmd, index) => (
                  <div key={index} className="flex items-start space-x-2 mb-2">
                    <Terminal className="h-4 w-4 mt-1" />
                    <p>{`[${cmd.timestamp}] ${cmd.type}: ${cmd.command} (${cmd.status})`}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutomationDashboard;