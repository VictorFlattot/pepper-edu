import React, { useEffect, useState } from 'react';
import { Table, Spinner, Alert, Form, Dropdown } from 'react-bootstrap';
import html2pdf from 'html2pdf.js';
import { useNavigate } from 'react-router-dom';
import { Pencil, Trash2, RefreshCcw, Settings, Download, Upload, Plus } from 'lucide-react';
import '../styles/TotalSante.css';

export default function TotalSanteComparatif() {
  const [donnees, setDonnees] = useState(null);
  const [loading, setLoading] = useState(true);
  const [choix, setChoix] = useState({});
  const [cartes, setCartes] = useState([]);

  const getBaseUrl = () => `http://${localStorage.getItem('flask_ip') || 'localhost:5000'}`;

  const navigate = useNavigate();

  const fetchDonnees = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${getBaseUrl()}/memory/get_resultats_total_sante`);
      const json = await res.json();
      setDonnees(json);
    } catch (err) {
      console.error("❌ Erreur fetch :", err);
      setDonnees(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchCartes = async () => {
    try {
      const res = await fetch(`${getBaseUrl()}/card/list`);
      const json = await res.json();
      setCartes(json);
    } catch (err) {
      console.error("❌ Erreur fetch cartes :", err);
    }
  };

  const groupesVariables = [
    { key: "tension", label: "TENSION" },
    { key: "ldl_chol", label: "LDL / Cholestérol", includes: ["ldl", "chol"] },
    { key: "hdl_tg", label: "HDL / Triglycérides", includes: ["hdl", "tg"] },
    { key: "hba1c_gly", label: "HbA1c / Glycémie", includes: ["hba1c", "gly"] },
    { key: "tt", label: "TOUR TAILLE" },
    { key: "tabac", label: "TABAC" },
    { key: "total", label: "TOTAL" },
    { key: "choix_alim", label: "Choix Alim." },
    { key: "choix_autre", label: "Choix Autre" },
    { key: "total_bonifie", label: "Total Bonifié" }
  ];

  const optionsAlim = [
    ["–", "–"],
    ["1", "1. Manger moins salé"],
    ["2", "2. Légumes + 1 fruit/repas"],
    ["3", "3. Réduire sucreries / grignotage"],
    ["4", "4. Repas équilibrés"],
    ["5", "5. Limiter les graisses"]
  ];

  const optionsAutre = [
    ["–", "–"],
    ["6", "6. Marcher 3x/semaine"],
    ["7", "7. Marcher chaque jour"],
    ["8", "8. Limiter l’alcool"],
    ["9", "9. Prendre ses médicaments"],
    ["10", "10. Arrêter de fumer"]
  ];

  const handleSelectChange = (prenom, type, value) => {
    setChoix(prev => ({
      ...prev,
      [prenom]: {
        ...prev[prenom],
        [type]: value
      }
    }));
  };

  const getBonusMap = (prenom) => {
    const c = choix[prenom] || {};
    const nums = [c.choix_alim, c.choix_autre].filter(v => v && v !== "–").map(Number);
    const bonusParVar = {};

    nums.forEach(n => {
      const carte = cartes.find(c => c.numero === n);
      if (carte && carte.bonus) {
        Object.entries(carte.bonus).forEach(([varName, pts]) => {
          const actuel = parseInt(donnees[prenom]?.[varName]?.points || 0);
          const ajoute = Math.max(0, Math.min(10, actuel + pts) - actuel);
          if (ajoute > 0) {
            bonusParVar[varName] = (bonusParVar[varName] || 0) + ajoute;
          }
        });
      }
    });

    return bonusParVar;
  };

  const calculBonifie = (prenom, total) => {
    const bonusMap = getBonusMap(prenom);
    const totalBonus = Object.values(bonusMap).reduce((a, b) => a + b, 0);
    return total + totalBonus;
  };

  const exporterCSV = () => {
    if (!donnees) return;

    const variables = ["tension", "ldl", "chol", "hdl", "tg", "hba1c", "gly", "tt", "tabac"];
    const entetes = ["Prénom"];

    // Génère colonnes : valeur ; points ; bonus
    variables.forEach(v => {
      entetes.push(`${v.toUpperCase()}`, `${v}_pts`, `${v}_bonus`);
    });

    entetes.push("TOTAL", "Choix Alim.", "Choix Autre", "Total Bonifié");

    const lignes = [entetes.join(";")];

    Object.entries(donnees).forEach(([prenom, data]) => {
      const bonusMap = getBonusMap(prenom);
      const base = parseInt(data.total || 0);
      const bonifie = calculBonifie(prenom, base);
      const choixAlim = choix[prenom]?.choix_alim || "–";
      const choixAutre = choix[prenom]?.choix_autre || "–";

      const ligne = [prenom];

      variables.forEach(v => {
        ligne.push(
          data[v]?.valeur || "",
          data[v]?.points || "",
          bonusMap[v] || 0
        );
      });

      ligne.push(base, choixAlim, choixAutre, bonifie);
      lignes.push(ligne.join(";"));
    });

    const today = new Date().toISOString().split("T")[0];
    const blob = new Blob([lignes.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `total_sante_resultats_${today}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const exporterPDF = () => {
    const element = document.getElementById("pdf-table-container");
    const options = {
      margin: 0.5,
      filename: `total_sante_resultats_${new Date().toISOString().split("T")[0]}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'in', format: 'a4', orientation: 'landscape' }
    };
    html2pdf().set(options).from(element).save();
  };


  const importerCSV = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target.result;
      const lignes = text.trim().split("\n");
      const entetes = lignes[0].split(";");

      const newDonnees = {};
      const newChoix = {};

      lignes.slice(1).forEach(l => {
        const cols = l.split(";");
        const obj = {};
        const prenom = cols[0];

        const map = {};
        entetes.forEach((col, i) => {
          map[col] = cols[i];
        });

        const vars = ["tension", "ldl", "chol", "hdl", "tg", "hba1c", "gly", "tt", "tabac"];
        vars.forEach(v => {
          obj[v] = {
            valeur: map[v.toUpperCase()] || "",
            points: parseInt(map[`${v}_pts`] || 0)
          };
        });

        obj["total"] = parseInt(map["TOTAL"] || 0);
        newDonnees[prenom] = obj;

        newChoix[prenom] = {
          choix_alim: map["Choix Alim."] || "–",
          choix_autre: map["Choix Autre"] || "–"
        };
      });

      setDonnees(newDonnees);
      setChoix(newChoix);
    };

    reader.readAsText(file, "UTF-8");
  };

  const supprimerParticipant = async (prenom) => {
    if (!window.confirm(`Supprimer ${prenom} ?`)) return;

    try {
      const res = await fetch(`${getBaseUrl()}/memory/delete_resultat_total_sante/${prenom}`, {
        method: "DELETE"
      });
      const result = await res.json();
      if (result.status === "ok") {
        fetchDonnees(); // recharge la liste
      } else {
        alert("Erreur : " + result.message);
      }
    } catch (err) {
      console.error("Erreur suppression :", err);
      alert("Erreur réseau.");
    }
  };


  useEffect(() => {
    fetchDonnees();
    fetchCartes();
  }, []);

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h3 className="mb-0 mx-auto">Comparatif des participants (Total Santé)</h3>
        <button
          className="btn btn-sm"
          onClick={fetchDonnees}
          title="Recharger"
          style={{ position: "absolute", right: "1rem" }}
        >
          <RefreshCcw size={20} />
        </button>
      </div>

      <div className="d-flex justify-content-end mb-3 position-relative">
        <Dropdown align="end">
          <Dropdown.Toggle variant="outline-dark" size="sm">
            <Settings size={18} />
          </Dropdown.Toggle>

          <Dropdown.Menu>
            <Dropdown.Item onClick={() => navigate('/formulaire-total-sante')}>
              <Plus size={16} className="me-2" />
              Ajouter un participant
            </Dropdown.Item>

            <Dropdown.Divider />
            {/* Exporter avec sous-menu */}

            <Dropdown.Item as="label" htmlFor="csvInput">
              <Upload size={16} className="me-2" />
              Importer
            </Dropdown.Item>

            <div className="dropdown-submenu">
              <span className="dropdown-item dropdown-submenu-toggle d-flex justify-content-between align-items-center">
                <span><Download size={16} className="me-2" />Exporter</span>
                <span>▶</span>
              </span>
              <div className="dropdown-submenu-content">
                <Dropdown.Item onClick={exporterCSV}>CSV</Dropdown.Item>
                <Dropdown.Item onClick={exporterPDF}>PDF</Dropdown.Item>
              </div>
            </div>

          </Dropdown.Menu>
        </Dropdown>

        <input
          type="file"
          id="csvInput"
          accept=".csv"
          style={{ display: "none" }}
          onChange={(e) => importerCSV(e)}
        />
      </div>



      {loading ? (
        <div className="text-center"><Spinner animation="border" /></div>
      ) : !donnees ? (
        <Alert variant="warning">Aucune donnée disponible.</Alert>
      ) : (
        <div id="pdf-table-container">
          <Table striped bordered hover responsive>
            <thead className="table-dark text-center">
              <tr>
                <th>Prénom</th>
                {groupesVariables.map(({ key, label, style }) => (
                  <th key={key} style={style || {}}>{label}</th>
                ))}
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {Object.entries(donnees).map(([prenom, data], idx) => {
                const bonusMap = getBonusMap(prenom);
                return (
                  <tr key={idx}>
                    <td className="fw-bold">{prenom}</td>
                    {groupesVariables.map(({ key, includes, style }) => {
                      if (key === "total") {
                        return (
                          <td key={key} className="fw-bold text-center">{data.total || "–"}</td>
                        );
                      } else if (key === "total_bonifie") {
                        const base = parseInt(data.total || 0);
                        const bonifie = calculBonifie(prenom, base);
                        return (
                          <td key={key} className="fw-bold text-center">{bonifie}</td>
                        );
                      } else if (key === "choix_alim" || key === "choix_autre") {
                        const options = key === "choix_alim" ? optionsAlim : optionsAutre;
                        const selected = choix[prenom]?.[key] || "–";
                        const label = options.find(([val]) => val === selected)?.[1] || "";

                        return (
                          <td key={key} className="text-center" title={label}>
                            <div style={{ position: "relative", display: "inline-block", width: "40px" }}>
                              <span style={{ fontWeight: "bold", cursor: "pointer" }}>
                                {selected}
                              </span>
                              <Form.Select
                                value={selected}
                                onChange={e => handleSelectChange(prenom, key, e.target.value)}
                                style={{
                                  position: "absolute",
                                  top: 0,
                                  left: 0,
                                  opacity: 0,
                                  width: "100%",
                                  height: "100%",
                                  cursor: "pointer"
                                }}
                              >
                                {options.map(([val, label], j) => (
                                  <option key={j} value={val}>{label}</option>
                                ))}
                              </Form.Select>
                            </div>
                          </td>
                        );
                      } else if (includes) {
                        const vals = includes.map(v => data[v]?.valeur || "–");
                        const points = includes.map(v => data[v]?.points).find(p => p);
                        const totalBonus = includes.map(v => bonusMap[v] || 0).reduce((a, b) => a + b, 0);
                        return (
                          <td key={key} style={style || {}}>
                            {vals.join(" / ")}<br />
                            <small className="text-muted">
                              {points ? `${points}` : ""}
                              {totalBonus > 0 && (
                                <span style={{ color: 'green', fontWeight: 'bold', marginLeft: 4 }}>
                                  +{totalBonus}
                                </span>
                              )}
                            </small>
                          </td>
                        );
                      } else {
                        const points = data[key]?.points;
                        const bonus = bonusMap[key] || 0;
                        return (
                          <td key={key} style={style || {}}>
                            {data[key]?.valeur || "–"}<br />
                            <small className="text-muted">
                              {points ? `${points}` : ""}
                              {bonus > 0 && (
                                <span style={{ color: 'green', fontWeight: 'bold', marginLeft: 4 }}>
                                  +{bonus}
                                </span>
                              )}
                            </small>
                          </td>
                        );
                      }
                    })}

                    {/* 🛠 Actions */}
                    <td className="text-center" style={{ width: "100px" }}>
                      <button
                        className="btn btn-sm me-2"
                        title="Modifier"
                        onClick={() => navigate(`/formulaire-total-sante?prenom=${prenom}`)}
                      >
                        <Pencil size={16} color="black" />
                      </button>

                      <button
                        className="btn btn-sm t"
                        title="Supprimer"
                        onClick={() => supprimerParticipant(prenom)}
                      >
                        <Trash2 size={16} color="black" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </Table>

        </div>
      )}
    </div>
  );
}
