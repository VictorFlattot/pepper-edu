import React, { useState } from 'react';
import { Button, Spinner, Form, Container } from 'react-bootstrap';

export default function Dialog() {
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);

  const getBaseUrl = () => {
    return `http://${localStorage.getItem('flask_ip') || 'localhost:5000'}`;
  };

  const sendPrompt = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setResponse("");
    try {
      const res = await fetch(`${getBaseUrl()}/llm/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
      });
      const data = await res.json();
      setResponse(data.response || "❌ Aucune réponse.");
    } catch (err) {
      console.error("Erreur réseau :", err);
      setResponse("Erreur de communication avec Pepper.");
    } finally {
      setLoading(false);
    }
  };

  const launchVoiceChat = async () => {
    setListening(true);
    setResponse("");
    try {
      const res = await fetch(`${getBaseUrl()}/chat_vocal`, {
        method: "POST"
      });
      const data = await res.json();
      if (data.response) {
        setResponse(data.response);
      } else if (data.error) {
        setResponse(`❌ ${data.error}`);
      } else {
        setResponse("❌ Réponse inconnue.");
      }
    } catch (err) {
      console.error("Erreur réseau vocal :", err);
      setResponse("Erreur durant le chat vocal.");
    } finally {
      setListening(false);
    }
  };

  return (
    <Container className="text-center mt-5">
      <h3 className="mb-4">🗣️ Dialogue avec Pepper</h3>

      <Form.Group className="mb-3" controlId="questionInput">
        <Form.Control
          as="textarea"
          rows={3}
          placeholder="Pose ta question ici..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
      </Form.Group>

      <div className="mb-3 d-flex justify-content-center gap-3">
        <Button variant="primary" onClick={sendPrompt} disabled={loading}>
          {loading ? <Spinner size="sm" animation="border" /> : "💬 Envoyer à Pepper"}
        </Button>

        <Button variant="success" onClick={launchVoiceChat} disabled={listening}>
          {listening ? <Spinner size="sm" animation="border" /> : "🎤 Chat vocal"}
        </Button>
      </div>

      {response && (
        <div className="border rounded p-3 bg-light text-start mx-auto" style={{ maxWidth: "600px" }}>
          <strong>Réponse de Pepper :</strong>
          <div className="mt-2">{response}</div>
        </div>
      )}
    </Container>
  );
}
