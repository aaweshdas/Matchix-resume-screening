import React, { useState, useEffect } from 'react';
import { 
  FileText, Cpu, Sparkles, Layers, ArrowDown, ArrowUp, CheckCircle, 
  AlertTriangle, RefreshCw, Play, Info, Check, ShieldAlert, Sliders
} from 'lucide-react';

export default function PipelineArchitecture() {
  const [resumeText, setResumeText] = useState(
    "Senior Machine Learning Engineer with 6 years experience in Python, PyTorch, Scikit-Learn, Docker, and NLP pipelines. Experienced in developing BERT transformers, vector search, and SQL databases. Bachelor's in Computer Science."
  );
  const [jobText, setJobText] = useState(
    "We are looking for an ML Engineer to lead model development and deployment. Required Skills: Python, Machine Learning, Deep Learning, SQL. Preferred Skills: Docker, NLP, AWS. Experience building production pipelines."
  );
  const [reqSkills, setReqSkills] = useState("Python, Machine Learning, Deep Learning, SQL");
  const [prefSkills, setPrefSkills] = useState("Docker, NLP, AWS");

  const [loading, setLoading] = useState(false);
  const [traceData, setTraceData] = useState(null);
  const [selectedNode, setSelectedNode] = useState('engine');
  const [autoSimulating, setAutoSimulating] = useState(false);

  const runTrace = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/pipeline/trace', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: resumeText,
          job_text: jobText,
          required_skills: reqSkills.split(',').map(s => s.trim()).filter(Boolean),
          preferred_skills: prefSkills.split(',').map(s => s.trim()).filter(Boolean),
        })
      });
      const data = await res.json();
      setTraceData(data);
    } catch (err) {
      console.error("Failed to run trace:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runTrace();
  }, []);

  return (
    <div>
      {/* Header */}
      <div className="section-title-wrap">
        <div>
          <h2 className="section-title">
            <Layers className="text-emerald-400" size={24} color="#10b981" />
            System Pipeline Architecture
          </h2>
          <p className="section-subtitle">
            Interactive visual simulation of the Dual-Branch Matching Engine with live node inspection.
          </p>
        </div>
        <button 
          onClick={runTrace} 
          disabled={loading}
          className="btn-primary"
          style={{ background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)', color: '#090d16' }}
        >
          {loading ? <RefreshCw className="animate-spin" size={16} /> : <Play size={16} />}
          Execute Pipeline Trace
        </button>
      </div>

      {/* Input Playground Box */}
      <div className="panel" style={{ background: '#0b111c', border: '1px solid #1c2a42' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Sliders size={16} /> LIVE PIPELINE INPUT DATA
          </span>
          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Edit inputs below to see live node transformations</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.2rem' }}>
          <div>
            <label className="input-label" style={{ color: '#34d399' }}>📄 Real Resume Input Text</label>
            <textarea
              className="input-textarea"
              rows={3}
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder="Paste candidate resume narrative..."
            />
          </div>
          <div>
            <label className="input-label" style={{ color: '#60a5fa' }}>📋 Job Description Input Text</label>
            <textarea
              className="input-textarea"
              rows={3}
              value={jobText}
              onChange={(e) => setJobText(e.target.value)}
              placeholder="Paste job posting text..."
            />
          </div>
        </div>
      </div>

      {/* Architecture Canvas */}
      <div className="pipeline-canvas">
        
        {/* NODE 1: REAL RESUME */}
        <div 
          className={`pipeline-node ${selectedNode === 'resume' ? 'active-node' : ''}`}
          onClick={() => setSelectedNode('resume')}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '4px' }}>
            <FileText size={18} color="#34d399" />
            <div className="pipeline-node-title">REAL RESUME</div>
          </div>
          <div className="pipeline-node-sub">Raw Candidate Narrative / PDF / DOCX</div>
        </div>

        {/* CONNECTOR */}
        <div className="pipeline-connector">
          <div className="connector-line"></div>
          <ArrowDown size={18} />
        </div>

        {/* NODE 2: NLP PREPROCESSING (RESUME) */}
        <div 
          className={`pipeline-node ${selectedNode === 'resume_nlp' ? 'active-node' : ''}`}
          onClick={() => setSelectedNode('resume_nlp')}
          style={{ borderColor: '#3b82f6' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '4px' }}>
            <Cpu size={18} color="#60a5fa" />
            <div className="pipeline-node-title">NLP PREPROCESSING</div>
          </div>
          <div className="pipeline-node-sub">Regex Cleaning • Stop-Word Removal • Lowercasing</div>
        </div>

        {/* SPLIT CONNECTOR */}
        <div className="pipeline-connector">
          <div className="connector-line"></div>
          <ArrowDown size={18} />
        </div>

        {/* DUAL PARALLEL BRANCHES (TOP) */}
        <div className="branch-split-box">
          {/* BRANCH A: SKILL EXTRACTION */}
          <div 
            className={`pipeline-node ${selectedNode === 'skill_extract' ? 'active-node' : ''}`}
            onClick={() => setSelectedNode('skill_extract')}
            style={{ flex: 1 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '4px' }}>
              <Sparkles size={18} color="#a78bfa" />
              <div className="pipeline-node-title">Skill Extraction</div>
            </div>
            <div className="pipeline-node-sub">73-Skill Lexicon Boundary Matching</div>
          </div>

          {/* BRANCH B: TEXT EMBEDDING */}
          <div 
            className={`pipeline-node ${selectedNode === 'resume_embed' ? 'active-node' : ''}`}
            onClick={() => setSelectedNode('resume_embed')}
            style={{ flex: 1 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '4px' }}>
              <Layers size={18} color="#38bdf8" />
              <div className="pipeline-node-title">Text Embedding</div>
            </div>
            <div className="pipeline-node-sub">Sublinear TF-IDF (Unigram + Bigram)</div>
          </div>
        </div>

        {/* DUAL CONNECTOR DOWN TO MATCHING ENGINE */}
        <div className="pipeline-connector">
          <div className="connector-line"></div>
          <ArrowDown size={18} />
        </div>

        {/* CENTRAL NODE: MATCHING ENGINE */}
        <div 
          className={`pipeline-node ${selectedNode === 'engine' ? 'active-node' : ''}`}
          onClick={() => setSelectedNode('engine')}
          style={{ 
            minWidth: '340px', 
            background: 'radial-gradient(circle, #1a2744 0%, #101826 100%)', 
            borderColor: '#10b981',
            boxShadow: '0 0 30px rgba(16, 185, 129, 0.25)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '6px' }}>
            <Cpu size={22} color="#10b981" />
            <div className="pipeline-node-title" style={{ fontSize: '1.25rem', letterSpacing: '1px' }}>
              MATCHING ENGINE
            </div>
          </div>
          <div className="pipeline-node-sub" style={{ color: '#34d399', fontWeight: 600 }}>
            Dual-Branch Blending: S_overall = w_skill·S_skill + w_text·S_text
          </div>
          {traceData && (
            <div style={{ marginTop: '8px', display: 'flex', justifyContent: 'center', gap: '15px', fontSize: '0.8rem' }}>
              <span style={{ color: '#94a3b8' }}>Overall Score: <b style={{ color: '#34d399' }}>{traceData.matching_engine.overall_match_score}%</b></span>
              <span style={{ color: '#94a3b8' }}>Skill: <b style={{ color: '#a78bfa' }}>{traceData.matching_engine.skill_score}%</b></span>
              <span style={{ color: '#94a3b8' }}>Text: <b style={{ color: '#38bdf8' }}>{traceData.matching_engine.text_similarity_score}%</b></span>
            </div>
          )}
        </div>

        {/* CONNECTOR UP FROM BOTTOM BRANCH */}
        <div className="pipeline-connector">
          <ArrowUp size={18} />
          <div className="connector-line"></div>
        </div>

        {/* DUAL PARALLEL BRANCHES (BOTTOM) */}
        <div className="branch-split-box">
          {/* BRANCH A: REQUIRED SKILLS */}
          <div 
            className={`pipeline-node ${selectedNode === 'job_skills' ? 'active-node' : ''}`}
            onClick={() => setSelectedNode('job_skills')}
            style={{ flex: 1 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '4px' }}>
              <CheckCircle size={18} color="#fbbf24" />
              <div className="pipeline-node-title">Required Skills</div>
            </div>
            <div className="pipeline-node-sub">Must-Have (75%) vs Nice-To-Have (25%)</div>
          </div>

          {/* BRANCH B: TEXT EMBEDDING (JOB) */}
          <div 
            className={`pipeline-node ${selectedNode === 'job_embed' ? 'active-node' : ''}`}
            onClick={() => setSelectedNode('job_embed')}
            style={{ flex: 1 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '4px' }}>
              <Layers size={18} color="#38bdf8" />
              <div className="pipeline-node-title">Text Embedding</div>
            </div>
            <div className="pipeline-node-sub">Job TF-IDF Vectorizer Transform</div>
          </div>
        </div>

        {/* CONNECTOR */}
        <div className="pipeline-connector">
          <ArrowUp size={18} />
          <div className="connector-line"></div>
        </div>

        {/* NODE: NLP PREPROCESSING (JOB) */}
        <div 
          className={`pipeline-node ${selectedNode === 'job_nlp' ? 'active-node' : ''}`}
          onClick={() => setSelectedNode('job_nlp')}
          style={{ borderColor: '#3b82f6' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '4px' }}>
            <Cpu size={18} color="#60a5fa" />
            <div className="pipeline-node-title">NLP PREPROCESSING</div>
          </div>
          <div className="pipeline-node-sub">Cleaning • Tokenization • Case Folding</div>
        </div>

        {/* CONNECTOR */}
        <div className="pipeline-connector">
          <ArrowUp size={18} />
          <div className="connector-line"></div>
        </div>

        {/* NODE: JOB DESCRIPTION */}
        <div 
          className={`pipeline-node ${selectedNode === 'job_desc' ? 'active-node' : ''}`}
          onClick={() => setSelectedNode('job_desc')}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '4px' }}>
            <FileText size={18} color="#60a5fa" />
            <div className="pipeline-node-title">JOB DESCRIPTION</div>
          </div>
          <div className="pipeline-node-sub">Title • Responsibilities • Requirements</div>
        </div>

      </div>

      {/* NODE INSPECTOR DRAWER */}
      {traceData && (
        <div className="inspector-panel">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', borderBottom: '1px solid #1e293b', paddingBottom: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Info size={20} color="#38bdf8" />
              <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#ffffff' }}>
                Node Inspector: <span style={{ color: '#38bdf8' }}>{selectedNode.toUpperCase()}</span>
              </h3>
            </div>
            <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Click any node in the diagram above to inspect state</span>
          </div>

          {/* INSPECTOR DETAILS BASED ON SELECTION */}
          {selectedNode === 'resume' && (
            <div>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '0.8rem' }}>
                Raw Resume document parsed from upload or database. Length: <b>{traceData.resume_branch.metrics.char_count} chars</b>, <b>{traceData.resume_branch.metrics.word_count} words</b>.
              </p>
              <div style={{ background: '#070b12', padding: '1rem', borderRadius: '8px', fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: '#cbd5e1' }}>
                {traceData.resume_branch.raw_text}
              </div>
            </div>
          )}

          {selectedNode === 'resume_nlp' && (
            <div>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '0.8rem' }}>
                Applies standard text normalization: strip URLs, remove email headers, eliminate digits, filter custom 34-word stop-word lexicon, and lowercase tokens.
              </p>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '1rem' }}>
                {traceData.resume_branch.nlp_preprocessing.sample_tokens.map((tok, i) => (
                  <span key={i} className="pill pill-neutral" style={{ fontFamily: 'var(--font-mono)' }}>{tok}</span>
                ))}
              </div>
              <div style={{ background: '#070b12', padding: '0.8rem', borderRadius: '8px', fontSize: '0.82rem', color: '#94a3b8' }}>
                Normalized output: <i>"{traceData.resume_branch.nlp_preprocessing.cleaned_text}"</i>
              </div>
            </div>
          )}

          {selectedNode === 'skill_extract' && (
            <div>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '0.8rem' }}>
                Scans normalized text against the <b>73-Skill Verified Lexicon</b> with word-boundary regex patterns <code>(?&lt;!\w)skill(?!\w)</code>:
              </p>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '1rem' }}>
                {traceData.resume_branch.skill_extraction.extracted_skills.map((s, i) => (
                  <span key={i} className="pill pill-matched">
                    <Check size={12} /> {s}
                  </span>
                ))}
              </div>
              <div style={{ fontSize: '0.82rem', color: '#64748b' }}>
                Extracted {traceData.resume_branch.skill_extraction.matched_count} skills out of 73 indexed tech skills.
              </div>
            </div>
          )}

          {selectedNode === 'resume_embed' && (
            <div>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '0.8rem' }}>
                Vectorized using fitted <b>Sublinear TF-IDF</b> (unigrams + bigrams) across a 5,000-dimensional shared feature space:
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '8px' }}>
                {traceData.resume_branch.text_embedding.top_features.map((item, i) => (
                  <div key={i} style={{ background: '#070b12', padding: '6px 10px', borderRadius: '6px', display: 'flex', justifyContent: 'space-between', fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>
                    <span style={{ color: '#38bdf8' }}>{item.term}</span>
                    <span style={{ color: '#94a3b8' }}>{item.weight}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {selectedNode === 'engine' && (
            <div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.2rem', marginBottom: '1.2rem' }}>
                <div style={{ background: '#070b12', padding: '1rem', borderRadius: '10px', border: '1px solid #1e293b' }}>
                  <div style={{ fontSize: '0.8rem', color: '#a78bfa', fontWeight: 700, marginBottom: '4px' }}>SKILL COVERAGE BRANCH</div>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#ffffff' }}>{traceData.matching_engine.skill_score}%</div>
                  <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Must-have (75%) + Nice-to-have (25%)</div>
                </div>

                <div style={{ background: '#070b12', padding: '1rem', borderRadius: '10px', border: '1px solid #1e293b' }}>
                  <div style={{ fontSize: '0.8rem', color: '#38bdf8', fontWeight: 700, marginBottom: '4px' }}>COSINE TEXT SIMILARITY</div>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#ffffff' }}>{traceData.matching_engine.text_similarity_score}%</div>
                  <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Cosine similarity of TF-IDF feature vectors</div>
                </div>

                <div style={{ background: '#070b12', padding: '1rem', borderRadius: '10px', border: '1px solid #10b981' }}>
                  <div style={{ fontSize: '0.8rem', color: '#34d399', fontWeight: 700, marginBottom: '4px' }}>OVERALL COMPOSITE MATCH</div>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#34d399' }}>{traceData.matching_engine.overall_match_score}%</div>
                  <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Weighted composite score</div>
                </div>
              </div>

              {/* Skill Gap Breakdown */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
                <div>
                  <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#34d399', marginBottom: '6px' }}>
                    ✅ Matched Skills ({traceData.matching_engine.gap_analysis.all_matched_skills.length})
                  </div>
                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                    {traceData.matching_engine.gap_analysis.all_matched_skills.map((s, i) => (
                      <span key={i} className="pill pill-matched">{s}</span>
                    ))}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#fb7185', marginBottom: '6px' }}>
                    ❌ Missing Required ({traceData.matching_engine.gap_analysis.missing_required.length})
                  </div>
                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                    {traceData.matching_engine.gap_analysis.missing_required.length > 0 ? (
                      traceData.matching_engine.gap_analysis.missing_required.map((s, i) => (
                        <span key={i} className="pill pill-missing-req">{s}</span>
                      ))
                    ) : (
                      <span style={{ fontSize: '0.8rem', color: '#64748b' }}>None! All matched.</span>
                    )}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#fbbf24', marginBottom: '6px' }}>
                    ⚠️ Missing Preferred ({traceData.matching_engine.gap_analysis.missing_preferred.length})
                  </div>
                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                    {traceData.matching_engine.gap_analysis.missing_preferred.length > 0 ? (
                      traceData.matching_engine.gap_analysis.missing_preferred.map((s, i) => (
                        <span key={i} className="pill pill-missing-pref">{s}</span>
                      ))
                    ) : (
                      <span style={{ fontSize: '0.8rem', color: '#64748b' }}>None! All matched.</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {selectedNode === 'job_skills' && (
            <div>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '0.8rem' }}>
                Job skill requirements partitioned into priority levels:
              </p>
              <div style={{ marginBottom: '0.8rem' }}>
                <span style={{ fontSize: '0.8rem', color: '#fb7185', fontWeight: 700, display: 'block', marginBottom: '4px' }}>Must-Have Skills (75% weight):</span>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {traceData.job_branch.required_skills.must_have.map((s, i) => (
                    <span key={i} className="pill pill-missing-req">{s}</span>
                  ))}
                </div>
              </div>
              <div>
                <span style={{ fontSize: '0.8rem', color: '#fbbf24', fontWeight: 700, display: 'block', marginBottom: '4px' }}>Nice-To-Have Skills (25% weight):</span>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {traceData.job_branch.required_skills.nice_to_have.map((s, i) => (
                    <span key={i} className="pill pill-missing-pref">{s}</span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {selectedNode === 'job_embed' && (
            <div>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '0.8rem' }}>
                Job description TF-IDF feature weights:
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '8px' }}>
                {traceData.job_branch.text_embedding.top_features.map((item, i) => (
                  <div key={i} style={{ background: '#070b12', padding: '6px 10px', borderRadius: '6px', display: 'flex', justifyContent: 'space-between', fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>
                    <span style={{ color: '#60a5fa' }}>{item.term}</span>
                    <span style={{ color: '#94a3b8' }}>{item.weight}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {selectedNode === 'job_nlp' && (
            <div>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '0.8rem' }}>
                Cleaned job description: <i>"{traceData.job_branch.nlp_preprocessing.cleaned_text}"</i>
              </p>
            </div>
          )}

          {selectedNode === 'job_desc' && (
            <div>
              <div style={{ background: '#070b12', padding: '1rem', borderRadius: '8px', fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: '#cbd5e1' }}>
                {traceData.job_branch.raw_text}
              </div>
            </div>
          )}

        </div>
      )}
    </div>
  );
}
