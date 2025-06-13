import React, { useState, useEffect } from 'react';

export default function Settings() {
  const [ip, setIp] = useState('');
  const [port, setPort] = useState('');
  const [backendIP, setBackendIP] = useState('');
  const [visionIP, setVisionIP] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const savedIp = localStorage.getItem('pepper_ip');
    const savedPort = localStorage.getItem('pepper_port');
    const savedBackend = localStorage.getItem('flask_ip');
    const savedVision = localStorage.getItem('vision_ip');

    if (savedIp) setIp(savedIp);
    if (savedPort) setPort(savedPort);
    if (savedBackend) setBackendIP(savedBackend);
    if (savedVision) setVisionIP(savedVision);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    localStorage.setItem('pepper_ip', ip);
    localStorage.setItem('pepper_port', port);
    localStorage.setItem('flask_ip', backendIP);
    localStorage.setItem('vision_ip', visionIP);

    fetch(`http://${backendIP}:5000/generate_config_js`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ip: backendIP, port: 5000 })  // ou dynamique
    })
      .then(res => res.json())
      .then(data => {
        if (!data.success) {
          console.warn("⚠️ Erreur génération config.js :", data.error);
        }
      });

    setMessage(`✔️ Adresses enregistrées :
Pepper → ${ip}:${port}
Flask → ${backendIP}
Vision → ${visionIP}`);
  };

  return (
    <div>
      <h2>⚙️ Paramètres</h2>

      <form onSubmit={handleSubmit} className="mt-4">
        <div className="mb-3">
          <label htmlFor="ip" className="form-label">Adresse IP de Pepper</label>
          <input
            type="text"
            className="form-control"
            id="ip"
            value={ip}
            onChange={(e) => setIp(e.target.value)}
          />
        </div>

        <div className="mb-3">
          <label htmlFor="port" className="form-label">Port</label>
          <input
            type="text"
            className="form-control"
            id="port"
            value={port}
            onChange={(e) => setPort(e.target.value)}
          />
        </div>

        <div className="mb-3">
          <label htmlFor="backend" className="form-label">Adresse du serveur Flask (Pepper)</label>
          <input
            type="text"
            className="form-control"
            id="backend"
            value={backendIP}
            onChange={(e) => setBackendIP(e.target.value)}
            placeholder="ex: localhost:5000"
          />
        </div>

        <div className="mb-3">
          <label htmlFor="vision" className="form-label">Adresse du serveur Vision (Python 3)</label>
          <input
            type="text"
            className="form-control"
            id="vision"
            value={visionIP}
            onChange={(e) => setVisionIP(e.target.value)}
            placeholder="ex: localhost:6000"
          />
        </div>

        <button type="submit" className="btn btn-primary">Enregistrer</button>
      </form>

      {message && (
        <div className="alert alert-success mt-3" style={{ whiteSpace: 'pre-wrap' }}>
          {message}
        </div>
      )}
    </div>
  );
}
