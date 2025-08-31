import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// French class names
const CLASSES = [
  "Salle 2", "Salle 5", "Salle 6", "Salle 7", "Salle 8", "Salle 9", 
  "Salle 10", "Salle 11", "Salle 12", "Salle 13", "Salle 14", "Salle 16", "Salle 18",
  "Nuage", "Soleil", "Arc-en-ciel", "Lune", "Étoile"
];

const MOTIFS = {
  "M": "Maladie",
  "RDV": "Rendez-vous médical", 
  "F": "Familial",
  "A": "Autre"
};

const Home = () => {
  return (
    <div className="home-container">
      <div className="header">
        <h1>📚 Suivi des Absences Scolaires</h1>
        <p>Application collaborative pour le suivi des absences des élèves</p>
      </div>
      
      <div className="instructions">
        <h2>Instructions d'utilisation</h2>
        <div className="instruction-grid">
          <div className="instruction-card">
            <h3>1. Sélectionner une classe</h3>
            <p>Cliquez sur l'onglet de votre classe parmi les 18 disponibles</p>
          </div>
          <div className="instruction-card">
            <h3>2. Ajouter une absence</h3>
            <p>Remplissez le formulaire avec les informations de l'élève absent</p>
          </div>
          <div className="instruction-card">
            <h3>3. Consulter l'historique</h3>
            <p>Visualisez toutes les absences enregistrées pour votre classe</p>
          </div>
          <div className="instruction-card">
            <h3>4. Statistiques</h3>
            <p>Accédez au tableau de bord pour voir les statistiques globales</p>
          </div>
        </div>
      </div>

      <div className="legend">
        <h2>Légende des codes</h2>
        <div className="legend-grid">
          <div className="legend-section">
            <h3>Motifs d'absence</h3>
            <ul>
              <li><strong>M</strong> - Maladie</li>
              <li><strong>RDV</strong> - Rendez-vous médical</li>
              <li><strong>F</strong> - Familial</li>
              <li><strong>A</strong> - Autre</li>
            </ul>
          </div>
          <div className="legend-section">
            <h3>Justification</h3>
            <ul>
              <li><strong>O</strong> - Oui (justifié)</li>
              <li><strong>N</strong> - Non (non justifié)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

const AbsenceForm = ({ classe, onAbsenceAdded }) => {
  const [formData, setFormData] = useState({
    date: new Date().toLocaleDateString('fr-FR'),
    nom: '',
    prenom: '',
    motif: 'M',
    justifie: 'O',
    remarques: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await axios.post(`${API}/absences`, {
        classe,
        ...formData
      });
      
      // Reset form
      setFormData({
        date: new Date().toLocaleDateString('fr-FR'),
        nom: '',
        prenom: '',
        motif: 'M',
        justifie: 'O',
        remarques: ''
      });
      
      onAbsenceAdded();
      alert('Absence ajoutée avec succès !');
    } catch (error) {
      console.error('Erreur:', error);
      alert('Erreur lors de l\'ajout de l\'absence');
    }
    
    setLoading(false);
  };

  return (
    <div className="absence-form">
      <h3>Ajouter une absence - {classe}</h3>
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label>Date (DD/MM/YYYY)</label>
            <input
              type="text"
              value={formData.date}
              onChange={(e) => setFormData({...formData, date: e.target.value})}
              placeholder="01/01/2024"
              required
            />
          </div>
          
          <div className="form-group">
            <label>Nom de famille</label>
            <input
              type="text"
              value={formData.nom}
              onChange={(e) => setFormData({...formData, nom: e.target.value})}
              required
            />
          </div>
          
          <div className="form-group">
            <label>Prénom</label>
            <input
              type="text"
              value={formData.prenom}
              onChange={(e) => setFormData({...formData, prenom: e.target.value})}
              required
            />
          </div>
          
          <div className="form-group">
            <label>Motif</label>
            <select
              value={formData.motif}
              onChange={(e) => setFormData({...formData, motif: e.target.value})}
            >
              {Object.entries(MOTIFS).map(([code, label]) => (
                <option key={code} value={code}>{code} - {label}</option>
              ))}
            </select>
          </div>
          
          <div className="form-group">
            <label>Justifié</label>
            <select
              value={formData.justifie}
              onChange={(e) => setFormData({...formData, justifie: e.target.value})}
            >
              <option value="O">O - Oui</option>
              <option value="N">N - Non</option>
            </select>
          </div>
          
          <div className="form-group full-width">
            <label>Remarques (optionnel)</label>
            <textarea
              value={formData.remarques}
              onChange={(e) => setFormData({...formData, remarques: e.target.value})}
              rows="2"
            />
          </div>
        </div>
        
        <button type="submit" disabled={loading} className="submit-btn">
          {loading ? 'Ajout...' : 'Ajouter l\'absence'}
        </button>
      </form>
    </div>
  );
};

const AbsenceList = ({ classe, absences, onDelete, onExport }) => {
  const classAbsences = absences.filter(a => a.classe === classe);

  return (
    <div className="absence-list">
      <div className="list-header">
        <h3>Absences - {classe} ({classAbsences.length})</h3>
        <div className="export-buttons">
          <button onClick={() => onExport(classe)} className="export-btn">
            📊 Exporter cette classe
          </button>
          <button onClick={() => onExport()} className="export-btn">
            📋 Exporter toutes les classes
          </button>
        </div>
      </div>
      
      {classAbsences.length === 0 ? (
        <p className="no-absences">Aucune absence enregistrée pour cette classe.</p>
      ) : (
        <div className="table-container">
          <table className="absence-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Nom</th>
                <th>Prénom</th>
                <th>Motif</th>
                <th>Justifié</th>
                <th>Remarques</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {classAbsences.map(absence => (
                <tr key={absence.id} className={absence.justifie === 'N' ? 'unjustified' : ''}>
                  <td>{absence.date}</td>
                  <td>{absence.nom}</td>
                  <td>{absence.prenom}</td>
                  <td>{absence.motif} - {MOTIFS[absence.motif]}</td>
                  <td>{absence.justifie === 'O' ? 'Oui' : 'Non'}</td>
                  <td>{absence.remarques}</td>
                  <td>
                    <button 
                      onClick={() => onDelete(absence.id)}
                      className="delete-btn"
                      title="Supprimer"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

const Dashboard = ({ stats }) => {
  const totalAbsences = stats.reduce((sum, stat) => sum + stat.total_absences, 0);
  const totalUnjustified = stats.reduce((sum, stat) => sum + stat.absences_non_justifiees, 0);
  const totalRecent = stats.reduce((sum, stat) => sum + stat.absences_recentes, 0);

  return (
    <div className="dashboard">
      <h2>📊 Tableau de bord</h2>
      
      <div className="global-stats">
        <div className="stat-card">
          <h3>{totalAbsences}</h3>
          <p>Total des absences</p>
        </div>
        <div className="stat-card unjustified">
          <h3>{totalUnjustified}</h3>
          <p>Absences non justifiées</p>
        </div>
        <div className="stat-card">
          <h3>{totalRecent}</h3>
          <p>Absences récentes (7 jours)</p>
        </div>
      </div>

      <div className="class-stats">
        <h3>Statistiques par classe</h3>
        <div className="table-container">
          <table className="stats-table">
            <thead>
              <tr>
                <th>Classe</th>
                <th>Total</th>
                <th>Non justifiées</th>
                <th>Récentes (7j)</th>
              </tr>
            </thead>
            <tbody>
              {stats.map(stat => (
                <tr key={stat.classe}>
                  <td>{stat.classe}</td>
                  <td>{stat.total_absences}</td>
                  <td className={stat.absences_non_justifiees > 0 ? 'unjustified' : ''}>
                    {stat.absences_non_justifiees}
                  </td>
                  <td>{stat.absences_recentes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [absences, setAbsences] = useState([]);
  const [stats, setStats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [absencesRes, statsRes] = await Promise.all([
        axios.get(`${API}/absences`),
        axios.get(`${API}/stats`)
      ]);
      
      setAbsences(absencesRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Erreur lors du chargement:', error);
    }
    setLoading(false);
  };

  const handleAbsenceAdded = () => {
    loadData(); // Reload data after adding absence
  };

  const handleDelete = async (absenceId) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette absence ?')) {
      try {
        await axios.delete(`${API}/absences/${absenceId}`);
        loadData(); // Reload data after deletion
        alert('Absence supprimée avec succès !');
      } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de la suppression');
      }
    }
  };

  const handleExport = (classe = null) => {
    const url = classe ? `${API}/export/excel?classe=${encodeURIComponent(classe)}` : `${API}/export/excel`;
    window.open(url, '_blank');
  };

  if (loading) {
    return <div className="loading">Chargement...</div>;
  }

  return (
    <div className="App">
      <nav className="nav-tabs">
        <button 
          className={activeTab === 'home' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('home')}
        >
          🏠 Accueil
        </button>
        <button 
          className={activeTab === 'dashboard' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('dashboard')}
        >
          📊 Tableau de bord
        </button>
        {CLASSES.map(classe => (
          <button
            key={classe}
            className={activeTab === classe ? 'tab active' : 'tab'}
            onClick={() => setActiveTab(classe)}
          >
            {classe}
          </button>
        ))}
      </nav>

      <div className="tab-content">
        {activeTab === 'home' && <Home />}
        {activeTab === 'dashboard' && <Dashboard stats={stats} />}
        {CLASSES.includes(activeTab) && (
          <div className="class-view">
            <AbsenceForm 
              classe={activeTab} 
              onAbsenceAdded={handleAbsenceAdded} 
            />
            <AbsenceList 
              classe={activeTab} 
              absences={absences}
              onDelete={handleDelete}
              onExport={handleExport}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;