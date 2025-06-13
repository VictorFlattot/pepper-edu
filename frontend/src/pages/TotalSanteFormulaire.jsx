import React, { useEffect, useState } from 'react';
import { Form, Button, Row, Col, Alert } from 'react-bootstrap';
import { useNavigate, useSearchParams } from 'react-router-dom';

export default function TotalSanteFormulaire() {
  const [prenom, setPrenom] = useState('');
  const [formData, setFormData] = useState({});
  const [message, setMessage] = useState(null);

  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const prenomQuery = searchParams.get("prenom");

  useEffect(() => {
    if (!prenomQuery) return;

    const fetchParticipant = async () => {
      try {
        const res = await fetch(`http://${localStorage.getItem("flask_ip") || "localhost:5000"}/memory/get_resultats_total_sante`);
        const data = await res.json();
        if (data[prenomQuery]) {
          setPrenom(prenomQuery);
          setFormData(data[prenomQuery]);
        }
      } catch (err) {
        console.error("Erreur chargement participant :", err);
      }
    };

    fetchParticipant();
  }, [prenomQuery]);

  const handleChange = (key, value) => {
    setFormData(prev => {
      const updated = {
        ...prev,
        [key]: { valeur: value }
      };
      return applyBarème(updated);
    });
  };

  const applyBarème = (data) => {
    const get = (v) => parseFloat(data[v]?.valeur || "");
    const valTension = get("tension");
    const valLDL = get("ldl");
    const valChol = get("chol");
    const valHDL = get("hdl");
    const valTG = get("tg");
    const valHBA = get("hba1c");
    const valGly = get("gly");
    const valTT = get("tt");
    const valTabac = (data.tabac?.valeur || "").toLowerCase();

    const points = {};

    if (!isNaN(valTension)) {
      if (valTension < 13) points.tension = 10;
      else if (valTension < 14) points.tension = 8;
      else if (valTension < 15) points.tension = 6;
      else if (valTension < 16) points.tension = 4;
      else if (valTension < 17) points.tension = 3;
      else if (valTension < 18) points.tension = 2;
      else points.tension = 0;
    }

    if (!isNaN(valLDL) || !isNaN(valChol)) {
      if ((valLDL < 1.0) || (valChol < 1.6)) points.ldl = 10;
      else if ((valLDL < 1.3) || (valChol < 1.99)) points.ldl = 8;
      else if ((valLDL < 1.6) || (valChol < 2.39)) points.ldl = 6;
      else if ((valLDL < 1.9) || (valChol < 2.59)) points.ldl = 4;
      else if ((valLDL < 2.2) || (valChol < 2.99)) points.ldl = 2;
      else points.ldl = 0;
    }

    if (!isNaN(valHDL) || !isNaN(valTG)) {
      if (valHDL >= 0.6 || valTG < 1) points.hdl = 10;
      else if (valHDL >= 0.55 || valTG < 1.5) points.hdl = 8;
      else if (valHDL >= 0.5 || valTG < 2) points.hdl = 6;
      else if (valHDL >= 0.45 || valTG < 2.5) points.hdl = 4;
      else if (valHDL >= 0.4 || valTG < 3) points.hdl = 3;
      else if (valHDL >= 0.35 || valTG < 4) points.hdl = 2;
      else points.hdl = 0;
    }

    if (!isNaN(valHBA) || !isNaN(valGly)) {
      if (valHBA < 6 || valGly < 1.10) points.hba1c = 10;
      else if (valHBA < 7 || valGly < 1.26) points.hba1c = 8;
      else if (valHBA < 8 || valGly < 1.61) points.hba1c = 6;
      else if (valHBA < 9 || valGly < 2.21) points.hba1c = 4;
      else if (valHBA < 10 || valGly < 2.61) points.hba1c = 2;
      else points.hba1c = 0;
    }

    if (!isNaN(valTT)) {
      if (valTT < 85) points.tt = 10;
      else if (valTT <= 90) points.tt = 8;
      else if (valTT <= 95) points.tt = 6;
      else if (valTT <= 100) points.tt = 4;
      else if (valTT <= 105) points.tt = 2;
      else points.tt = 0;
    }

    if (valTabac === "non") points.tabac = 10;
    else if (valTabac === "oui") points.tabac = 0;

    const updated = { ...data };
    Object.keys(points).forEach(k => {
      if (!updated[k]) updated[k] = {};
      updated[k].points = points[k];
    });

    setFormData(updated);
    return updated;
  };

  const total = Object.values(formData).reduce((sum, v) => {
    const p = parseInt(v.points || 0);
    return sum + (isNaN(p) ? 0 : p);
  }, 0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prenom) return alert("Merci de renseigner un prénom.");

    const payload = {
      [prenom]: {
        ...formData,
        total: total
      }
    };

    try {
      const res = await fetch(`http://${localStorage.getItem("flask_ip") || "localhost:5000"}/memory/set_resultat_total_sante`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const result = await res.json();
      if (result.status === "ok") {
        navigate(-1); // retour à la page précédente
      } else {
        setMessage("❌ Erreur : " + (result.message || "inconnue"));
      }
    } catch (err) {
      console.error("Erreur réseau :", err);
      setMessage("❌ Erreur réseau");
    }
  };

  return (
    <div className="container mt-4">
      <h3 className="mb-4 text-center">Formulaire Total Santé</h3>
      {message && <Alert variant="info">{message}</Alert>}

      <div className="mb-3 text-start">
        <button className="btn btn-secondary" type="button" onClick={() => navigate(-1)}>
          ⬅️ Retour
        </button>
      </div>

      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-4">
          <Form.Label>Prénom</Form.Label>
          <Form.Control type="text" value={prenom} onChange={e => setPrenom(e.target.value)} required />
        </Form.Group>

        {/* Groupes affichés */}
        <Row className="mb-3">
          <Col md={4}><Form.Label>Tension</Form.Label></Col>
          <Col md={4}><Form.Control value={formData.tension?.valeur || ""} onChange={e => handleChange("tension", e.target.value)} /></Col>
          <Col md={4} className="d-flex align-items-center"><strong>{formData.tension?.points || 0} pts</strong></Col>
        </Row>

        <Row className="mb-3">
          <Col md={4}><Form.Label>LDL / Cholestérol</Form.Label></Col>
          <Col md={2}><Form.Control placeholder="LDL" value={formData.ldl?.valeur || ""} onChange={e => handleChange("ldl", e.target.value)} /></Col>
          <Col md={2}><Form.Control placeholder="CHOL" value={formData.chol?.valeur || ""} onChange={e => handleChange("chol", e.target.value)} /></Col>
          <Col md={4} className="d-flex align-items-center"><strong>{formData.ldl?.points || 0} pts</strong></Col>
        </Row>

        <Row className="mb-3">
          <Col md={4}><Form.Label>HDL / Triglycérides</Form.Label></Col>
          <Col md={2}><Form.Control placeholder="HDL" value={formData.hdl?.valeur || ""} onChange={e => handleChange("hdl", e.target.value)} /></Col>
          <Col md={2}><Form.Control placeholder="TG" value={formData.tg?.valeur || ""} onChange={e => handleChange("tg", e.target.value)} /></Col>
          <Col md={4} className="d-flex align-items-center"><strong>{formData.hdl?.points || 0} pts</strong></Col>
        </Row>

        <Row className="mb-3">
          <Col md={4}><Form.Label>HbA1c / Glycémie</Form.Label></Col>
          <Col md={2}><Form.Control placeholder="HbA1c" value={formData.hba1c?.valeur || ""} onChange={e => handleChange("hba1c", e.target.value)} /></Col>
          <Col md={2}><Form.Control placeholder="Gly" value={formData.gly?.valeur || ""} onChange={e => handleChange("gly", e.target.value)} /></Col>
          <Col md={4} className="d-flex align-items-center"><strong>{formData.hba1c?.points || 0} pts</strong></Col>
        </Row>

        <Row className="mb-3">
          <Col md={4}><Form.Label>Tour de taille</Form.Label></Col>
          <Col md={4}><Form.Control value={formData.tt?.valeur || ""} onChange={e => handleChange("tt", e.target.value)} /></Col>
          <Col md={4} className="d-flex align-items-center"><strong>{formData.tt?.points || 0} pts</strong></Col>
        </Row>

        <Row className="mb-3">
          <Col md={4}><Form.Label>Tabac</Form.Label></Col>
          <Col md={4}>
            <Form.Select value={formData.tabac?.valeur || ""} onChange={e => handleChange("tabac", e.target.value)}>
              <option value="">–</option>
              <option value="non">non</option>
              <option value="oui">oui</option>
            </Form.Select>
          </Col>
          <Col md={4} className="d-flex align-items-center"><strong>{formData.tabac?.points || 0} pts</strong></Col>
        </Row>

        <h5 className="text-end mt-4">Total : {total} pts</h5>

        <div className="text-center mt-4">
          <Button type="submit" variant="primary">💾 Enregistrer</Button>
        </div>
      </Form>
    </div>
  );
}
