import React, { useState } from 'react';
import { Container, Card, Button, Spinner } from 'react-bootstrap';

export default function Overview() {
  const [loading, setLoading] = useState(false);

  const getBaseUrl = () => {
    return `http://${localStorage.getItem('flask_ip') || 'localhost:5000'}`;
  };

  const startSession = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${getBaseUrl()}/behavior/run?id=menu-f6a1ea/seance-diabete`, {
        method: 'POST'
      });
      const data = await res.json();
      console.log('✅ Behavior lancé :', data);
    } catch (err) {
      console.error('❌ Erreur :', err);
    }
    setLoading(false);
  };

  return (
    <Container className="mt-5 text-center">
      <h1 className="mb-4">Vue d’ensemble</h1>

      <Card className="mb-4 text-start">
        <Card.Body>
          <Card.Title>But de la séance</Card.Title>
          <Card.Text>
            Cette interface vous accompagne dans l’animation d’une séance éducative sur le risque cardiovasculaire.
            Pepper interagit avec les participants pour recueillir leurs données, présenter les actions possibles,
            et favoriser l’engagement dans une démarche de santé.
          </Card.Text>
        </Card.Body>
      </Card>

      <Button onClick={startSession} disabled={loading}>
        {loading ? <Spinner animation="border" size="sm" /> : 'Lancer la seance'}
      </Button>
    </Container>
  );
}
