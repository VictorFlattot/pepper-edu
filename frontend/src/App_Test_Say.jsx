import React, { useState } from 'react';

function App() {
  const [message, setMessage] = useState('');
  const [sayText, setSayText] = useState('');

  const handleSay = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/say', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: sayText })
      });
      // Nous pouvons directement tenter de parser la réponse
      const data = await response.json();
      if (data.status === 'success') {
        setMessage(data.message);
      } else {
        setMessage(`Erreur : ${data.error}`);
      }
    } catch (error) {
      setMessage(`Erreur réseau ou JSON : ${error.message}`);
    }
  };

  return (
    <div style={{ padding: '1rem' }}>
      <h1>Contrôle NAOqi (React + Flask)</h1>
      <div style={{ marginBottom: '1rem' }}>
        <label>Phrase à dire : </label>
        <input
          type="text"
          value={sayText}
          onChange={(e) => setSayText(e.target.value)}
          style={{ marginLeft: '0.5rem' }}
        />
        <button onClick={handleSay} style={{ marginLeft: '0.5rem' }}>
          Parler
        </button>
      </div>
      {message && <p><strong>Résultat :</strong> {message}</p>}
    </div>
  );
}

export default App;
