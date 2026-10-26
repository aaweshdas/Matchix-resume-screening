import React, { useState } from 'react';
import { 
  LayoutDashboard, Target, GitCompare, FolderKanban, 
  Workflow, Play 
} from 'lucide-react';

import Dashboard from './components/Dashboard';
import DeepMatch from './components/DeepMatch';
import BatchScreening from './components/BatchScreening';
import PipelineArchitecture from './components/PipelineArchitecture';
import BenchmarkAnalytics from './components/BenchmarkAnalytics';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [deepMatchParams, setDeepMatchParams] = useState({ candidateId: 'R_000000', jobId: 'J_000000' });

  const handleSelectJob = (jobId) => {
    setDeepMatchParams(prev => ({ ...prev, jobId }));
    setActiveTab('deep');
  };

  const handleSelectCandidateForDeep = (candidateId, jobId) => {
    setDeepMatchParams({ candidateId, jobId: jobId || 'J_000000' });
    setActiveTab('deep');
  };

  return (
    <div className="app-container">
      {/* Top Navigation Header matching Sentimix */}
      <header className="top-header">
        <div className="brand-section">
          <div className="brand-logo-badge">SX</div>
          <div className="brand-text-block">
            <h1>
              MATCHIX <span className="brand-ver">v3.0</span>
            </h1>
            <div className="brand-tagline">
              Dual-Branch Skill & TF-IDF Matching Engine
            </div>
          </div>
        </div>

        {/* Navigation Tabs matching Sentimix layout */}
        <nav className="nav-tab-group">
          <button 
            className={`nav-tab-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard size={15} /> Dashboard
          </button>

          <button 
            className={`nav-tab-item ${activeTab === 'batch' ? 'active' : ''}`}
            onClick={() => setActiveTab('batch')}
          >
            <FolderKanban size={15} /> Batch Screening
          </button>

          <button 
            className={`nav-tab-item ${activeTab === 'deep' ? 'active' : ''}`}
            onClick={() => setActiveTab('deep')}
          >
            <Target size={15} /> 1-on-1 Deep Match
          </button>

          <button 
            className={`nav-tab-item ${activeTab === 'benchmark' ? 'active' : ''}`}
            onClick={() => setActiveTab('benchmark')}
          >
            <GitCompare size={15} /> Model Comparison
          </button>

          <button 
            className={`nav-tab-item ${activeTab === 'pipeline' ? 'active' : ''}`}
            onClick={() => setActiveTab('pipeline')}
          >
            <Workflow size={15} /> Pipeline Architecture
          </button>
        </nav>

        {/* Right CTA Button matching Sentimix screenshot */}
        <div>
          <button 
            className="header-cta-btn"
            onClick={() => setActiveTab('batch')}
          >
            <Play size={14} fill="#080a0f" color="#080a0f" /> Batch Screening
          </button>
        </div>
      </header>

      {/* Main Content View */}
      <main className="main-wrapper">
        {activeTab === 'dashboard' && (
          <Dashboard 
            setActiveTab={setActiveTab} 
            onSelectJobForRank={handleSelectJob}
          />
        )}

        {activeTab === 'batch' && (
          <BatchScreening />
        )}

        {activeTab === 'deep' && (
          <DeepMatch 
            initialCandidateId={deepMatchParams.candidateId}
            initialJobId={deepMatchParams.jobId}
          />
        )}

        {activeTab === 'benchmark' && (
          <BenchmarkAnalytics />
        )}

        {activeTab === 'pipeline' && (
          <PipelineArchitecture />
        )}
      </main>

      {/* Sleek Minimalist Footer */}
      <footer style={{ borderTop: '1px solid var(--border-subtle)', padding: '1.4rem 2.5rem', textAlign: 'center', fontSize: '0.78rem', color: '#64748b' }}>
        <p>
          MATCHIX v3.0 • Dual-Branch Resume Screening & Candidate Classification System • Evaluated on 75,000 Ground-Truth Relationships
        </p>
      </footer>
    </div>
  );
}
