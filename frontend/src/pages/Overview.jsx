import React, { useState } from 'react';
import { Button, Spinner } from 'react-bootstrap';

export default function Overview() {
  const [mapImage, setMapImage] = useState(null);
  const [loadingMap, setLoadingMap] = useState(false);

  const getBaseUrl = () => {
    return `http://${localStorage.getItem('flask_ip') || 'localhost:5000'}`;
  };

  const fetchMap = async () => {
    setLoadingMap(true);
    setMapImage(null);
    try {
      const res = await fetch(`${getBaseUrl()}/nav/map`);
      const data = await res.json();
      if (data.success) {
        setMapImage(`data:image/png;base64,${data.image}`);
      } else {
        console.error("Erreur récupération carte :", data.error);
      }
    } catch (err) {
      console.error("Erreur réseau récupération carte :", err);
    } finally {
      setLoadingMap(false);
    }
  };

  return (
    <div className="container text-center">
      <h3 className="mb-4">Tableau de bord</h3>

      <div className="mb-3">
        <Button variant="primary" onClick={fetchMap} disabled={loadingMap}>
          {loadingMap ? <Spinner size="sm" animation="border" /> : '🗺️ Afficher la carte SLAM'}
        </Button>
      </div>

      {mapImage && (
        <div className="mt-4">
          <h5>Carte générée par Pepper</h5>
          <img
            src={mapImage}
            alt="Carte SLAM"
            style={{
              width: '300px',
              maxWidth: '50%',
              border: '2px solid #ccc',
              borderRadius: '8px',
              marginTop: '1rem',
              boxShadow: '0 0 10px rgba(0,0,0,0.15)'
            }}
          />
        </div>
      )}
    </div>
  );
}
