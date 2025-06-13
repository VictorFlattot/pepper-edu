// src/main.jsx
import React from 'react'
import ReactDOM from 'react-dom/client'

// Import du CSS de Bootstrap
import 'bootstrap/dist/css/bootstrap.min.css'

import App from './App'
// import './styles.css' // Votre éventuelle feuille de style perso

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
