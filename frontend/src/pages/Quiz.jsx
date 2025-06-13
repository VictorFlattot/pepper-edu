import React, { useEffect, useState } from 'react';

export default function Quiz() {
  const [quizState, setQuizState] = useState(null);
  const [loading, setLoading] = useState(false);

  const getBaseUrl = () => {
    return `http://${localStorage.getItem('flask_ip') || 'localhost:5000'}`;
  };

  const fetchQuizState = async () => {
    try {
      const res = await fetch(`${getBaseUrl()}/quiz/state`);
      const data = await res.json();
      setQuizState(data);
    } catch (err) {
      console.error('Erreur chargement état du quiz :', err);
    }
  };

  const startQuiz = async () => {
    setLoading(true);
    try {
      await fetch(`${getBaseUrl()}/quiz/start`, { method: 'POST' });
      await fetchQuizState();
    } finally {
      setLoading(false);
    }
  };

  const nextQuestion = async () => {
    setLoading(true);
    try {
      await fetch(`${getBaseUrl()}/quiz/next`, { method: 'POST' });
      await fetchQuizState();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuizState();
  }, []);

  return (
    <div className="container py-4">
      <h2>🎓 Quiz – Présentateur</h2>

      <div className="my-3 d-flex gap-2">
        <button
          className="btn btn-primary"
          onClick={startQuiz}
          disabled={loading || quizState?.status === 'running' || quizState?.status === 'finished'}
        >
          ▶️ Lancer le quiz
        </button>

        {quizState?.status === 'running' && (
          <button
            className="btn btn-success"
            onClick={nextQuestion}
            disabled={loading}
          >
            ⏭️ Question suivante
          </button>
        )}
      </div>

      {quizState?.status === 'running' && (
        <div className="border rounded p-3 bg-light">
          <h5>Question {quizState.current_index + 1}/10</h5>
          <p className="fs-5"><strong>{quizState.question}</strong></p>

          <ul className="list-group">
            {quizState.choices.map((choice, i) => {
              const label = String.fromCharCode(65 + i);
              return (
                <li key={i} className="list-group-item">
                  <strong>{label}.</strong> {choice}
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {quizState?.status === 'finished' && (
        <div className="alert alert-info mt-3 text-center">
          ✅ Le quiz est terminé
          <br />
          <button
            className="btn btn-outline-secondary mt-3"
            onClick={startQuiz}
            disabled={loading}
          >
            🔄 Réinitialiser
          </button>
        </div>
      )}
    </div>
  );
}
