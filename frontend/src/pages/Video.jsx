import React, { useState, useEffect } from 'react';
import { Button, Spinner } from 'react-bootstrap';

export default function Video() {
  const [streamReady, setStreamReady] = useState(false);
  const [loadingStream, setLoadingStream] = useState(false);
  const [streamUrl, setStreamUrl] = useState('');
  const [loadingCount, setLoadingCount] = useState(false);

  const getBaseUrl = () => {
    return `http://${localStorage.getItem('flask_ip') || 'localhost:5000'}`;
  };

  const getVisionUrl = () => {
    return `http://${localStorage.getItem('vision_ip') || 'localhost:6000'}`;
  };

  const startStream = () => {
    setLoadingStream(true);
    setTimeout(() => {
      const timestamp = new Date().getTime();
      setStreamUrl(`${getBaseUrl()}/pepper/camera/stream?t=${timestamp}`);
      setStreamReady(true);
      setLoadingStream(false);
    }, 1000);
  };

  useEffect(() => {
    fetch(`${getVisionUrl()}/ping`)
      .then(res => res.json())
      .then(data => console.log("✅ Vision répond :", data))
      .catch(err => console.error("❌ Vision injoignable :", err));
  }, []);

  const captureCurrentFrame = () => {
    console.log("🎯 captureCurrentFrame appelé");

    return new Promise((resolve, reject) => {
      const videoElement = document.querySelector('img[alt="Flux caméra Pepper"]');

      if (!videoElement) {
        console.warn("⚠️ Aucune image de caméra trouvée !");
        return reject("Pas d'image vidéo trouvée");
      }

      const canvas = document.createElement('canvas');
      canvas.width = videoElement.naturalWidth || 640;
      canvas.height = videoElement.naturalHeight || 480;

      const ctx = canvas.getContext('2d');
      ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

      canvas.toBlob((blob) => {
        if (blob) {
          console.log("🧪 Image blob généré");
          resolve(blob);
        } else {
          reject("Impossible de convertir l'image en blob");
        }
      }, 'image/jpeg');
    });
  };

  const countFingers = async () => {
    console.log("📸 Bouton 'Compter les doigts' cliqué");
    setLoadingCount(true);
    try {
      const imageBlob = await captureCurrentFrame();
      const formData = new FormData();
      formData.append('image', imageBlob, 'frame.jpg');
      console.log(getVisionUrl())
      console.log("🚀 Envoi vers Vision avec : ", formData.get('image'));

      const res = await fetch(`${getVisionUrl()}/count-fingers`, {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      console.log("✅ Réponse serveur Vision :", data);

      if (data.success) {
        const fingers = data.fingers;
        let phrase = '';

        if (fingers === 0) phrase = "Je ne vois aucun doigt.";
        else if (fingers === 1) phrase = "Je vois un doigt.";
        else phrase = `Je vois ${fingers} doigts.`;

        await fetch(`${getBaseUrl()}/say`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: phrase }),
        });
      } else {
        console.error('Erreur Vision:', data.error);
      }
    } catch (err) {
      console.error('Erreur réseau ou capture:', err);
    } finally {
      setLoadingCount(false);
    }
  };

  return (
    <div className="container text-center">
      <h3 className="mb-4">Flux Vidéo Pepper 🎥</h3>

      <div className="d-flex justify-content-center gap-3 mb-4">
        <Button variant="primary" onClick={startStream} disabled={loadingStream}>
          {loadingStream ? <Spinner size="sm" animation="border" /> : '📷 Démarrer la caméra'}
        </Button>

        <Button variant="success" onClick={countFingers} disabled={loadingCount}>
          {loadingCount ? <Spinner size="sm" animation="border" /> : '✋ Compter les doigts'}
        </Button>
      </div>

      {streamReady && streamUrl && (
        <div className="mt-4 d-flex justify-content-center">
          <div
            style={{
              width: '100%',
              maxWidth: '800px',
              aspectRatio: '4/3',
              overflow: 'hidden',
              borderRadius: '12px',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
              border: '3px solid #0d6efd',
              backgroundColor: '#000',
            }}
          >
            <img
              src={streamUrl}
              alt="Flux caméra Pepper"
              crossOrigin="anonymous"
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                borderRadius: '12px',
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
