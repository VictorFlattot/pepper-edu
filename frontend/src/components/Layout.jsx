// Fichier Layout.jsx fusionné avec appel automatique à /memory/set_server_ip
import React, { useEffect, useRef, useState } from 'react';
import Sidebar from './Sidebar';
import { Bot, Settings, Volume2 } from 'lucide-react';
import 'rc-slider/assets/index.css';
import Slider from 'rc-slider';

export default function Layout({ children }) {
  const [pepperConnected, setPepperConnected] = useState(false);
  const [autonomyMode, setAutonomyMode] = useState('disabled');
  const [volume, setVolume] = useState(70);
  const [showVolumeSlider, setShowVolumeSlider] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const intervalRef = useRef(null);

  const getBaseUrl = () => {
    return `http://${localStorage.getItem('flask_ip') || 'localhost:5000'}`;
  };

  const toggleConnection = async () => {
    setLoading(true);
    setShowToast(false);

    const ip = localStorage.getItem('pepper_ip') || '127.0.0.1';
    const port = localStorage.getItem('pepper_port') || '9559';
    const baseUrl = getBaseUrl();

    try {
      if (pepperConnected) {
        await fetch(`${baseUrl}/pepper/disconnect`, { method: 'POST' });
        setPepperConnected(false);
        setAutonomyMode('disabled');
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        setToastMessage('Déconnecté de Pepper.');
      } else {
        const res = await fetch(`${baseUrl}/pepper/connect?ip=${ip}&port=${port}`);
        const data = await res.json();

        if (data.connected) {
          setPepperConnected(true);

          try {
            await fetch(`${baseUrl}/memory/set_server_ip`, { method: 'POST' });
            await fetch(`${baseUrl}/memory/subscribe_resultats`, { method: 'POST' });
            await fetch(`${baseUrl}/memory/subscribe_slam_map`, { method: 'POST' });
          } catch (err) {
            console.warn("Erreur lors de l'initialisation Pepper :", err);
          }

          setToastMessage('Connecté à Pepper ✅');

          intervalRef.current = setInterval(async () => {
            try {
              const statusRes = await fetch(`${baseUrl}/pepper/status`);
              const status = await statusRes.json();
              setPepperConnected(status.connected);
            } catch (err) {
              console.error('[PING error]', err);
              setPepperConnected(false);
            }
          }, 2000);
        } else {
          setToastMessage(data.error || 'Erreur de connexion à Pepper.');
        }
      }
    } catch (err) {
      console.error('[toggleConnection error]', err);
      setToastMessage('Erreur de communication avec le serveur.');
    } finally {
      setLoading(false);
      setShowToast(true);
      setTimeout(() => setShowToast(false), 4000);
    }
  };

  const handleAutonomyChange = async (e) => {
    const selectedMode = e.target.value;
    setAutonomyMode(selectedMode);

    const baseUrl = getBaseUrl();
    try {
      const res = await fetch(`${baseUrl}/pepper/autonomy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: selectedMode })
      });
      const data = await res.json();
      if (data.success) {
        setToastMessage(`Mode autonomie : ${selectedMode}`);
        setShowToast(true);
        setTimeout(() => setShowToast(false), 4000);
      } else {
        console.error("Erreur changement autonomie :", data.error);
      }
    } catch (err) {
      console.error("Erreur réseau :", err);
    }
  };

  const handleVolumeChange = async (newVolume) => {
    setVolume(newVolume);
    const baseUrl = getBaseUrl();
    try {
      await fetch(`${baseUrl}/pepper/set-volume`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ volume: newVolume }),
      });
    } catch (err) {
      console.error('[setVolume error]', err);
    }
  };

  const toggleVolumeSlider = () => {
    setShowVolumeSlider(!showVolumeSlider);
  };

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return (
    <div className="d-flex">
      <Sidebar />
      <div className="flex-grow-1">
        <header className="bg-light py-3 px-4 border-bottom d-flex justify-content-between align-items-center position-relative">
          <h2 className="m-0">Mon Super Dashboard</h2>

          <div className="d-flex align-items-center gap-4 position-relative">
            <div className="d-flex align-items-center gap-2">
              <select
                className="form-select form-select-sm"
                style={{ width: '140px', cursor: pepperConnected ? 'pointer' : 'not-allowed', opacity: pepperConnected ? 1 : 0.5 }}
                disabled={!pepperConnected}
                value={autonomyMode}
                onChange={handleAutonomyChange}
              >
                <option value="interactive">Interactive</option>
                <option value="solitary">Solitary</option>
                <option value="disabled">Disabled</option>
              </select>
            </div>

            <div className="position-relative" style={{ cursor: 'pointer' }}>
              <Volume2 size={24} onClick={toggleVolumeSlider} title="Ajuster le volume" />
              {showVolumeSlider && (
                <div
                  className="position-absolute d-flex flex-column align-items-center"
                  style={{ top: '30px', left: '50%', transform: 'translateX(-50%)', backgroundColor: 'transparent', padding: '4px', zIndex: 1000, height: '120px' }}
                >
                  <Slider
                    vertical
                    min={0}
                    max={100}
                    value={volume}
                    onChange={handleVolumeChange}
                    disabled={!pepperConnected}
                    trackStyle={{ backgroundColor: '#0d6efd', width: 6 }}
                    handleStyle={{ borderColor: '#0d6efd', height: 16, width: 16, marginLeft: -5, marginTop: -8, backgroundColor: '#0d6efd' }}
                    railStyle={{ backgroundColor: '#ddd', width: 6 }}
                  />
                  <div className="mt-2 small">{volume}%</div>
                </div>
              )}
            </div>

            <div
              className="position-relative"
              onClick={toggleConnection}
              title={pepperConnected ? 'Déconnecter Pepper' : 'Connecter Pepper'}
              style={{ cursor: loading ? 'wait' : 'pointer' }}
            >
              <Bot size={24} />
              <span
                className="position-absolute top-0 start-100 translate-middle p-1 border border-light rounded-circle"
                style={{ backgroundColor: pepperConnected ? 'green' : 'red', width: '10px', height: '10px' }}
              ></span>
            </div>
          </div>
        </header>

        <main className="p-4">
          {children}
        </main>

        {showToast && (
          <div className="toast show position-fixed bottom-0 end-0 m-4" role="alert" style={{ zIndex: 9999, minWidth: '250px' }}>
            <div className={`toast-header ${pepperConnected ? 'bg-success' : 'bg-danger'} text-white`}>
              <strong className="me-auto">Message Pepper</strong>
              <button type="button" className="btn-close" onClick={() => setShowToast(false)} />
            </div>
            <div className="toast-body">{toastMessage}</div>
          </div>
        )}
      </div>
    </div>
  );
}
