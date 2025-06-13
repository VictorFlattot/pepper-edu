import React, { useEffect, useState } from 'react';
import {
  Container, ListGroup, Form, Spinner, Modal, Image
} from 'react-bootstrap';
import { Map, Pencil, Trash2, Eye } from 'lucide-react';
import '../styles/Nav.css';

export default function SlamSelector() {
  const [maps, setMaps] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState(null);
  const [editedLabel, setEditedLabel] = useState("");
  const [showPreview, setShowPreview] = useState(false);
  const [previewMap, setPreviewMap] = useState(null);

  const getBaseUrl = () => {
    return `http://${localStorage.getItem('flask_ip') || 'localhost:5000'}`;
  };

  const fetchMaps = async () => {
    try {
      const res = await fetch(`${getBaseUrl()}/nav/slam/maps`);
      const data = await res.json();
      if (Array.isArray(data)) {
        setMaps(data);
      } else {
        setMaps([]);
      }
    } catch (e) {
      console.error("Erreur récupération des cartes :", e);
    }
  };

  const selectMap = async (map) => {
    setLoading(true);
    setSelected(map.name);
    try {
      await fetch(`${getBaseUrl()}/nav/slam/select`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ map: map.name })
      });
    } catch (e) {
      console.error("Erreur lors de la sélection :", e);
    } finally {
      setLoading(false);
    }
  };

  const updateLabel = async (map) => {
    try {
      await fetch(`${getBaseUrl()}/nav/slam/maps/label`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: map.name, label: editedLabel })
      });
      setEditing(null);
      fetchMaps();
    } catch (e) {
      console.error("Erreur mise à jour label :", e);
    }
  };

  const deleteMap = async (map) => {
    const confirm = window.confirm(`🗑️ Supprimer la carte "${map.label || map.name}" ?`);
    if (!confirm) return;
    try {
      await fetch(`${getBaseUrl()}/nav/slam/maps/delete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: map.name })
      });
      fetchMaps();
    } catch (e) {
      console.error("Erreur suppression carte :", e);
    }
  };

  const showMapPreview = (map) => {
    setPreviewMap(map);
    setShowPreview(true);
  };

  useEffect(() => {
    fetchMaps();
  }, []);

  return (
    <Container className="mt-5">
      <h3 className="mb-4 text-center">
        <Map className="me-2" size={28} /> Choix de la carte SLAM
      </h3>

      <ListGroup className="mb-4">
        {maps.map((map, idx) => (
          <ListGroup.Item
            key={idx}
            active={selected === map.name}
            className="d-flex justify-content-between align-items-center"
            style={{ cursor: "pointer" }}
            onClick={() => selectMap(map)}
          >
            <div style={{ flexGrow: 1 }}>
              {editing === map.name ? (
                <Form.Control
                  type="text"
                  size="sm"
                  value={editedLabel}
                  onChange={(e) => setEditedLabel(e.target.value)}
                  onBlur={() => updateLabel(map)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") updateLabel(map);
                    if (e.key === "Escape") setEditing(null);
                  }}
                  autoFocus
                />
              ) : (
                <>
                  <strong>{map.label || "Sans label"}</strong> — <code>{map.name}</code>
                </>
              )}
            </div>

            {editing !== map.name && (
              <div className="d-flex align-items-center">
                <button
                  className="btn btn-sm me-2"
                  title="Aperçu"
                  onClick={(e) => {
                    e.stopPropagation();
                    showMapPreview(map);
                  }}
                >
                  <Eye size={16} color="black" />
                </button>

                <button
                  className="btn btn-sm me-2"
                  title="Modifier"
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditing(map.name);
                    setEditedLabel(map.label || "");
                  }}
                >
                  <Pencil size={16} color="black" />
                </button>

                <button
                  className="btn btn-sm"
                  title="Supprimer"
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteMap(map);
                  }}
                >
                  <Trash2 size={16} color="black" />
                </button>
              </div>
            )}
          </ListGroup.Item>
        ))}
      </ListGroup>

      {loading && (
        <div className="text-center">
          <Spinner animation="border" />
        </div>
      )}

      {/* Aperçu Modal */}
      <Modal show={showPreview} onHide={() => setShowPreview(false)} centered size="lg">
        <Modal.Header closeButton>
          <Modal.Title>{previewMap?.label || previewMap?.name}</Modal.Title>
        </Modal.Header>
        <Modal.Body className="text-center">
          {previewMap ? (
            <Image
              src={`${getBaseUrl()}/nav/slam/image/${previewMap.name}`}
              fluid
              alt="Carte SLAM"
              style={{ maxHeight: "80vh", objectFit: "contain" }}
            />
          ) : (
            <p>Chargement...</p>
          )}
        </Modal.Body>
      </Modal>
    </Container>
  );
}
