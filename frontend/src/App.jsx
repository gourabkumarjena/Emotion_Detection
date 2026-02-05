import { useState, useEffect } from 'react'

function App() {
  const [isStreaming, setIsStreaming] = useState(true);
  const [serverStatus, setServerStatus] = useState('Checking...');

  // Check backend health
  useEffect(() => {
    const checkServer = async () => {
      try {
        const res = await fetch('http://localhost:8000/');
        if (res.ok) {
          setServerStatus('Online');
        } else {
          setServerStatus('Error');
        }
      } catch (e) {
        setServerStatus('Offline');
      }
    };

    // Check every 5 seconds
    checkServer();
    const interval = setInterval(checkServer, 5000);
    return () => clearInterval(interval);
  }, []);

  const toggleStream = () => {
    setIsStreaming(!isStreaming);
  };

  const toggleConfidence = async () => {
    try {
      await fetch('http://localhost:8000/toggle_confidence', { method: 'POST' });
    } catch (e) {
      console.error("Failed to toggle confidence");
    }
  };

  return (
    <div className="app-container fade-in">
      <header>
        <h1>Emotion Detector</h1>
        <div className={`status-badge`}>
          <div className="status-dot" style={{ color: serverStatus === 'Online' ? '#34d399' : '#ef4444' }}></div>
          System {serverStatus}
        </div>
      </header>

      <main>
        <div className="video-container">
          {isStreaming ? (
            <img
              src="http://localhost:8000/video_feed"
              alt="Live Video Feed"
              className="video-feed"
              onError={(e) => {
                e.target.style.display = 'none';
                // You could show a placeholder here
              }}
            />
          ) : (
            <div style={{ color: 'var(--secondary-text)' }}>Stream Paused</div>
          )}
        </div>

        <aside className="controls-container">
          <div className="control-group">
            <h2>Controls</h2>
            <button className="btn" onClick={toggleStream}>
              {isStreaming ? 'Stop Camera' : 'Start Camera'}
            </button>
            <button className="btn btn-secondary" onClick={toggleConfidence}>
              Toggle Confidence
            </button>
          </div>

          <div className="control-group">
            <h2>Analytics</h2>
            <div className="info-card">
              <div className="info-item">
                <span className="info-label">Frame Rate</span>
                <span className="info-value">30 FPS</span>
              </div>
              <div className="info-item">
                <span className="info-label">Resolution</span>
                <span className="info-value">640 x 480</span>
              </div>
              <div className="info-item">
                <span className="info-label">Active Model</span>
                <span className="info-value">PyTorch CNN</span>
              </div>
            </div>

            <div className="info-card">
              <div className="info-item">
                <span className="info-label">Detection Mode</span>
                <span className="info-value">Haar Cascade</span>
              </div>
            </div>
          </div>
        </aside>
      </main>
    </div>
  )
}

export default App
