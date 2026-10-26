import React, { useState, useEffect } from 'react';
import { 
  Database, Trophy, Target, Zap, ArrowUpRight, Cpu, 
  Layers, Sparkles, FileText, CheckCircle2, ShieldCheck, ArrowRight, TrendingUp
} from 'lucide-react';

export default function Dashboard({ setActiveTab, onSelectJobForRank }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quickJobs, setQuickJobs] = useState([]);

  useEffect(() => {
    fetch('/api/stats')
      .then(res => res.json())
      .then(data => {
        setStats(data);
        setLoading(false);
      })
      .catch(err => console.error("Error fetching stats:", err));

    fetch('/api/jobs?limit=4')
      .then(res => res.json())
      .then(data => setQuickJobs(data.jobs || []))
      .catch(err => console.error("Error fetching sample jobs:", err));
  }, []);

  return (
    <div>
      {/* Synthetic Dataset Notice */}
      <div className="synthetic-banner">
        <ShieldCheck size={18} color="#f59e0b" />
        <div>
          <strong>MIRRA Resume-Job Matching Dataset (CSV):</strong> Configured with {stats ? stats.total_candidates.toLocaleString() : '10,000'} raw & processed candidate resumes, {stats ? stats.total_jobs.toLocaleString() : '2,500'} jobs, and {stats?.ground_truth_pairs ? stats.ground_truth_pairs.toLocaleString() : '75,000'} ground-truth relationships completely in CSV format.
        </div>
      </div>

      {/* Hero Container matching Sentimix screenshot */}
      <div className="hero-container">
        <div className="hero-pill-badge">
          <Zap size={14} color="#a78bfa" /> Machine Learning & Dual-Branch Matching System
        </div>
        <h1 className="hero-title-text">
          Resume Screening & Candidate Classification System
        </h1>
        <p className="hero-sub-text">
          Comprehensive evaluation comparing Skill Lexicon Coverage and Sublinear TF-IDF Cosine Similarity trained on candidate-job relationships from the MIRRA benchmark corpus.
        </p>
        <div className="hero-button-row">
          <button 
            className="btn-white-pill"
            onClick={() => setActiveTab('batch')}
          >
            Launch Batch Screening <ArrowUpRight size={16} />
          </button>
          <button 
            className="btn-dark-pill"
            onClick={() => setActiveTab('benchmark')}
          >
            Full Model Benchmark
          </button>
        </div>
      </div>

      {/* 5 KPI Cards Grid with Dynamic Benchmark Metrics */}
      <div className="kpi-cards-grid">
        {/* Card 1: DATASET RECORDS */}
        <div className="kpi-card-box">
          <div className="kpi-top-row">
            <span className="kpi-title-label">Dataset Records</span>
            <div className="kpi-corner-icon">
              <Database size={16} color="#94a3b8" />
            </div>
          </div>
          <div className="kpi-huge-number">
            {stats ? stats.total_candidates.toLocaleString() : '10,000'}
          </div>
          <div className="kpi-bottom-caption">
            MIRRA Dataset (Raw & Processed CSV)
          </div>
        </div>

        {/* Card 2: TOP CLASSIFIER */}
        <div className="kpi-card-box" onClick={() => setActiveTab('benchmark')} style={{ cursor: 'pointer' }}>
          <div className="kpi-top-row">
            <span className="kpi-title-label">Top Classifier</span>
            <div className="kpi-corner-icon">
              <Trophy size={16} color="#fbbf24" />
            </div>
          </div>
          <div className="kpi-huge-number" style={{ fontSize: '1.75rem', color: '#a78bfa' }}>
            {stats?.top_model?.model_name || 'Random Forest'}
          </div>
          <div className="kpi-bottom-caption">
            {stats?.top_model?.model_type || 'Bagging'} Paradigm Winner
          </div>
        </div>

        {/* Card 3: TOP F1-SCORE */}
        <div className="kpi-card-box" onClick={() => setActiveTab('benchmark')} style={{ cursor: 'pointer' }}>
          <div className="kpi-top-row">
            <span className="kpi-title-label">Top F1-Score</span>
            <div className="kpi-corner-icon">
              <Target size={16} color="#34d399" />
            </div>
          </div>
          <div className="kpi-huge-number" style={{ color: '#34d399' }}>
            {stats?.top_model?.f1_score ? `${stats.top_model.f1_score}%` : '89.32%'}
          </div>
          <div className="kpi-bottom-caption">
            Harmonic mean on 80/20 test split
          </div>
        </div>

        {/* Card 4: TOP ACCURACY */}
        <div className="kpi-card-box" onClick={() => setActiveTab('benchmark')} style={{ cursor: 'pointer' }}>
          <div className="kpi-top-row">
            <span className="kpi-title-label">Top Accuracy</span>
            <div className="kpi-corner-icon">
              <Zap size={16} color="#38bdf8" />
            </div>
          </div>
          <div className="kpi-huge-number" style={{ color: '#38bdf8' }}>
            {stats?.top_model?.accuracy ? `${stats.top_model.accuracy}%` : '88.92%'}
          </div>
          <div className="kpi-bottom-caption">
            Test set classification accuracy
          </div>
        </div>

        {/* Card 5: TOP ROC-AUC */}
        <div className="kpi-card-box" onClick={() => setActiveTab('benchmark')} style={{ cursor: 'pointer' }}>
          <div className="kpi-top-row">
            <span className="kpi-title-label">Top ROC-AUC</span>
            <div className="kpi-corner-icon">
              <TrendingUp size={16} color="#fbbf24" />
            </div>
          </div>
          <div className="kpi-huge-number" style={{ color: '#fbbf24' }}>
            {stats?.top_model?.auc ? stats.top_model.auc.toFixed(4) : '0.9330'}
          </div>
          <div className="kpi-bottom-caption">
            Area Under ROC Curve ({stats?.top_model?.auc ? (stats.top_model.auc * 100).toFixed(1) : '93.3'}%)
          </div>
        </div>
      </div>

      {/* Model Architecture Summary Cards matching Sentimix screenshot */}
      <div className="section-headline-bar">
        <div className="section-icon-chip">
          <Cpu size={16} />
        </div>
        <h2 className="section-main-heading">
          Model Architecture Summary Cards
        </h2>
      </div>

      <div className="model-summary-grid">
        {/* Card 1 */}
        <div className="model-summary-card">
          <div>
            <div className="model-summary-header">
              <span className="model-tag tag-blue">Baseline Cleaner</span>
              <FileText size={18} color="#60a5fa" />
            </div>
            <div className="model-summary-title">NLP Preprocessing Engine</div>
            <p className="model-summary-desc">
              Normalizes raw resumes and job postings. Eliminates email headers, web URLs, non-alphanumeric artifacts, digits, and filters custom stop-words for high-signal extraction.
            </p>
          </div>
          <div className="model-summary-footer">
            <span>Features: Lowercase & Regex</span>
            <span>Latency: &lt; 2ms / doc</span>
          </div>
        </div>

        {/* Card 2 */}
        <div className="model-summary-card">
          <div>
            <div className="model-summary-header">
              <span className="model-tag tag-emerald">Selected • Lexicon</span>
              <Sparkles size={18} color="#34d399" />
            </div>
            <div className="model-summary-title">Skill Extraction Branch</div>
            <p className="model-summary-desc">
              Performs boundary regex matching over the 73-skill taxonomy. Computes weighted coverage dividing required skills into Must-Have (75% weight) and Nice-To-Have (25% weight).
            </p>
          </div>
          <div className="model-summary-footer">
            <span>Lexicon: 73 Curated Skills</span>
            <span>Weight: 60% default</span>
          </div>
        </div>

        {/* Card 3 */}
        <div className="model-summary-card">
          <div>
            <div className="model-summary-header">
              <span className="model-tag tag-purple">TF-IDF Embedding</span>
              <Layers size={18} color="#a78bfa" />
            </div>
            <div className="model-summary-title">Semantic Text Embedding</div>
            <p className="model-summary-desc">
              Maps candidate narrative bullets and job descriptions into a 5,000-dimensional sublinear TF-IDF vector space with unigrams and bigrams, calculating pairwise cosine distance.
            </p>
          </div>
          <div className="model-summary-footer">
            <span>Vectorizer: Sublinear TF-IDF</span>
            <span>Weight: 40% default</span>
          </div>
        </div>

        {/* Card 4 */}
        <div className="model-summary-card">
          <div>
            <div className="model-summary-header">
              <span className="model-tag tag-cyan">Composite Core</span>
              <Target size={18} color="#38bdf8" />
            </div>
            <div className="model-summary-title">Dual-Branch Matching Engine</div>
            <p className="model-summary-desc">
              Fuses skill coverage and semantic embeddings through configurable multi-objective blending: S_overall = w_skill · S_skill + w_text · S_text with automated skill gap diagnosis.
            </p>
          </div>
          <div className="model-summary-footer">
            <span>Fusion: Multi-Objective</span>
            <span>Ground Truth: 75k Pairs</span>
          </div>
        </div>
      </div>

      {/* Fast-Start Benchmark Jobs */}
      <div className="panel">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.2rem' }}>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#ffffff' }}>
              🎯 Fast-Start Benchmark Jobs
            </h3>
            <p style={{ fontSize: '0.8rem', color: '#64748b' }}>
              Select a benchmark job to screen all 10,000 candidates instantly
            </p>
          </div>
          <button 
            className="btn-dark-pill"
            onClick={() => setActiveTab('batch')}
            style={{ fontSize: '0.8rem', padding: '0.45rem 1rem' }}
          >
            Launch Batch Screening →
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
          {quickJobs.map(job => (
            <div 
              key={job.job_id}
              style={{
                background: '#0b0f16',
                border: '1px solid #1a2230',
                borderRadius: '12px',
                padding: '1.1rem',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
              onClick={() => {
                if (onSelectJobForRank) onSelectJobForRank(job.job_id);
                setActiveTab('batch');
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.72rem', color: '#60a5fa', fontFamily: 'var(--font-mono)' }}>{job.job_id}</span>
                <span className="pill pill-neutral" style={{ fontSize: '0.7rem' }}>{job.seniority || 'Mid'}</span>
              </div>
              <div style={{ fontWeight: 700, color: '#ffffff', fontSize: '0.95rem', marginBottom: '0.3rem' }}>
                {job.job_title}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.8rem' }}>
                Industry: {job.industry}
              </div>
              <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                {job.required_skills.slice(0, 3).map((s, idx) => (
                  <span key={idx} className="pill pill-matched" style={{ fontSize: '0.7rem' }}>{s}</span>
                ))}
                {job.required_skills.length > 3 && (
                  <span className="pill pill-neutral" style={{ fontSize: '0.7rem' }}>+{job.required_skills.length - 3}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
