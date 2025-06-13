import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Overview from './pages/Overview';
import Settings from './pages/Settings';
import Behaviors from './pages/Behaviors';
import Quiz from './pages/Quiz';
import Move from './pages/Move';
import Video from './pages/Video';
import Dialog from "./pages/Dialog";
import TotalSante from './pages/TotalSante';
import TotalSanteFormulaire from './pages/TotalSanteFormulaire';
import SlamSelector from './pages/Slam'; 

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout><Overview /></Layout>} />
        <Route path="/behaviors" element={<Layout><Behaviors /></Layout>} />
        <Route path="/quiz" element={<Layout><Quiz /></Layout>} />
        <Route path="/move" element={<Layout><Move /></Layout>} />
        <Route path="/video" element={<Layout><Video /></Layout>} /> {/* 👈 Ajout de la route pour Vidéo */}
        <Route path="/settings" element={<Layout><Settings /></Layout>} />
        <Route path="/dialog" element={<Layout><Dialog /></Layout>} />
        <Route path="/totalSante" element={<Layout><TotalSante/></Layout>} />
        <Route path="/formulaire-total-sante" element={<Layout><TotalSanteFormulaire /></Layout>} />
        <Route path="/slam" element={<Layout><SlamSelector /></Layout>} />
      </Routes>
    </Router>
  );
}