import React, { useEffect, useState } from 'react';
import { FaPlay, FaStop } from 'react-icons/fa';

export default function Behaviors() {
  const [behaviors, setBehaviors] = useState([]);
  const [runningList, setRunningList] = useState([]);
  const [pending, setPending] = useState(null); // { id: string, action: 'start' | 'stop' }

  const getBaseUrl = () => {
    return `http://${localStorage.getItem('flask_ip') || 'localhost:5000'}`;
  };

  useEffect(() => {
    const fetchBehaviors = async () => {
      try {
        const res = await fetch(`${getBaseUrl()}/behavior/get`);
        const data = await res.json();
        setBehaviors(data);
      } catch (err) {
        console.error('Erreur chargement comportements :', err);
      }
    };

    fetchBehaviors();
    fetchRunning();

    const interval = setInterval(fetchRunning, 2000);
    return () => clearInterval(interval);
  }, []);

  const fetchRunning = async () => {
    try {
      const res = await fetch(`${getBaseUrl()}/behavior/status`);
      const data = await res.json();
      if (Array.isArray(data.running)) {
        setRunningList(data.running);
      }
    } catch (err) {
      console.error('Erreur récupération comportements actifs :', err);
    }
  };

  const toggleBehavior = async (id, isRunning) => {
    const action = isRunning ? 'stop' : 'start';
    setPending({ id, action });

    try {
      const route = isRunning ? 'stop' : 'run';
      const res = await fetch(`${getBaseUrl()}/behavior/${route}?id=${id}`, { method: 'POST' });
      const data = await res.json();
      if (!data.success) alert(`Erreur : ${data.error}`);
      await fetchRunning();
    } catch (err) {
      alert('Erreur de communication');
    } finally {
      setPending(null);
    }
  };

  return (
    <div className="d-flex flex-column" style={{ height: 'calc(100vh - 150px)' }}>
      <h2>Comportements disponibles</h2>

      <div
        className="mt-3 overflow-auto"
        style={{
          flex: 1,
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))',
          gap: '1rem',
          paddingRight: '8px',
        }}
      >
        {behaviors.map((b) => {
          const isRunning = runningList.includes(b.id);
          const isPending = pending && pending.id === b.id;

          const allowClick =
            !pending ||
            pending.id !== b.id ||
            (pending.action === 'start' && isRunning) ||
            (pending.action === 'stop' && !isRunning);

          return (
            <div
              key={b.id}
              className="position-relative p-3 border rounded d-flex flex-column justify-content-between"
              style={{
                height: '200px',
                backgroundColor: '#f8f9fa',
              }}
            >
              {/* Bouton toggle en haut à droite */}
              <div style={{ position: 'absolute', top: 8, right: 8 }}>
                <button
                  className="btn"
                  style={{
                    padding: '0.2rem 0.4rem',
                    fontSize: '1rem',
                    background: 'none',
                    border: 'none',
                    color: isRunning ? '#dc3545' : '#0d6efd',
                    cursor: allowClick ? 'pointer' : 'wait',
                    opacity: allowClick ? 1 : 0.6,
                  }}
                  title={isRunning ? 'Arrêter' : 'Lancer'}
                  onClick={() => {
                    if (allowClick) toggleBehavior(b.id, isRunning);
                  }}
                >
                  {isRunning ? <FaStop /> : <FaPlay />}
                </button>
              </div>

              <div className="text-center">
                <div style={{ fontSize: '2rem' }}>{b.icon}</div>
                <h6 className="mt-2 mb-1">{b.name}</h6>
                <small
                  className="text-muted"
                  style={{
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    fontSize: '0.75rem',
                  }}
                  title={b.description}
                >
                  {b.description}
                </small>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
