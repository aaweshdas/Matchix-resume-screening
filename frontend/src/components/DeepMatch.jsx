import React, { useState, useEffect } from 'react';
import { 
  Search, CheckCircle, XCircle, AlertTriangle, User, 
  Briefcase, Award, Zap, Sliders, RefreshCw, Sparkles, Upload, FileText 
} from 'lucide-react';

export default function DeepMatch({ initialCandidateId, initialJobId }) {
  const [candidateMode, setCandidateMode] = useState('preset'); // 'upload' | 'preset'
  const [jobMode, setJobMode] = useState('preset'); // 'upload' | 'preset'

  const [candidateId, setCandidateId] = useState(initialCandidateId || 'R_000000');
  const [jobId, setJobId] = useState(initialJobId || 'J_000000');

  // Custom Uploaded Candidate State
  const [customCand, setCustomCand] = useState({
    filename: 'Sample_Resume.pdf',
    role: 'Senior Software Engineer',
    skills: ['Python', 'SQL', 'Databases', 'Docker', 'Git'],
    raw_text: 'Experienced Software Engineer with 6+ years building backend microservices in Python and SQL databases. Strong experience in Docker, CI/CD, Git, and automated testing.',
  });
  const [isUploadingResume, setIsUploadingResume] = useState(false);

  // Custom Uploaded / Typed Job State
  const [customJob, setCustomJob] = useState({
    filename: 'Job_Description.pdf',
    job_title: 'Full Stack Engineer',
    required_skills: 'Python, SQL, Git, Docker',
    preferred_skills: 'AWS, CI/CD, Machine Learning',
    job_text: 'We are hiring a Full Stack Engineer to lead web infrastructure and backend microservices. Required skills: Python, SQL, Git, Docker. Preferred: AWS, CI/CD, Machine Learning.',
  });
  const [isUploadingJob, setIsUploadingJob] = useState(false);

  const [loading, setLoading] = useState(false);
  const [matchResult, setMatchResult] = useState(null);

  const [candidateList, setCandidateList] = useState([]);
  const [jobList, setJobList] = useState([]);

  useEffect(() => {
    fetch('/api/candidates?limit=100')
      .then(res => res.json())
      .then(data => setCandidateList(data.candidates || []));

    fetch('/api/jobs?limit=100')
      .then(res => res.json())
      .then(data => setJobList(data.jobs || []));
  }, []);

  const handleResumeFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploadingResume(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/upload-resume', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!data.error) {
        setCustomCand({
          filename: data.filename,
          role: file.name.replace(/\.[^/.]+$/, "").replace(/_/g, ' '),
          skills: data.skills || [],
          raw_text: data.raw_text || '',
        });
        setCandidateMode('upload');
      }
    } catch (err) {
      console.error("Resume upload failed:", err);
    } finally {
      setIsUploadingResume(false);
    }
  };

  const handleJobFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploadingJob(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/upload-job', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!data.error) {
        setCustomJob({
          filename: data.filename,
          job_title: data.job_title || file.name.replace(/\.[^/.]+$/, "").replace(/_/g, ' '),
          required_skills: (data.required_skills || []).join(', '),
          preferred_skills: (data.preferred_skills || []).join(', '),
          job_text: data.raw_text || '',
        });
        setJobMode('upload');
      }
    } catch (err) {
      console.error("Job upload failed:", err);
    } finally {
      setIsUploadingJob(false);
    }
  };

  const runDeepMatch = async () => {
    setLoading(true);
    try {
      const payload = {};
      if (candidateMode === 'preset') {
        payload.candidate_id = candidateId;
      } else {
        payload.custom_candidate = {
          candidate_id: customCand.filename || 'Uploaded_Resume',
          role: customCand.role || 'Candidate',
          skills: customCand.skills || [],
          resume_text: customCand.raw_text || '',
        };
      }

      if (jobMode === 'preset') {
        payload.job_id = jobId;
      } else {
        const reqArr = typeof customJob.required_skills === 'string'
          ? customJob.required_skills.split(',').map(s => s.trim()).filter(Boolean)
          : customJob.required_skills;
        const prefArr = typeof customJob.preferred_skills === 'string'
          ? customJob.preferred_skills.split(',').map(s => s.trim()).filter(Boolean)
          : customJob.preferred_skills;

        payload.custom_job = {
          job_id: 'CUSTOM_JOB',
          job_title: customJob.job_title || 'Custom Job Position',
          required_skills: reqArr,
          preferred_skills: prefArr,
          job_text: customJob.job_text || `${customJob.job_title}. Required: ${reqArr.join(', ')}. Preferred: ${prefArr.join(', ')}.`,
        };
      }

      const res = await fetch('/api/deep-match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      setMatchResult(data);
    } catch (err) {
      console.error("Deep match error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runDeepMatch();
  }, [candidateId, jobId, candidateMode, jobMode]);

  return (
    <div>
      <div className="section-title-wrap">
        <div>
          <h2 className="section-title">
            <Search size={22} color="#06b6d4" />
            1-on-1 Deep Match & Skill Gap Analysis
          </h2>
          <p className="section-subtitle">
            Compare candidate resumes against job descriptions (upload files, enter text, or select benchmark profiles).
          </p>
        </div>
        <button 
          className="btn-primary"
          onClick={runDeepMatch}
          disabled={loading || isUploadingResume || isUploadingJob}
          style={{ background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)', color: '#ffffff' }}
        >
          {loading ? <RefreshCw className="animate-spin" size={16} /> : <Zap size={16} />}
          Run 1-on-1 Deep Match
        </button>
      </div>

      {/* Selectors & Upload Panels Bar */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.2rem', marginBottom: '1.5rem' }}>
        
        {/* Candidate Profile Box */}
        <div className="panel" style={{ background: '#0a0f19', border: '1px solid #1e293b', marginBottom: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.8rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#38bdf8' }}>Candidate Resume</span>
            <div style={{ display: 'flex', gap: '4px', background: '#050811', padding: '2px', borderRadius: '6px' }}>
              <button
                className={`pill ${candidateMode === 'preset' ? 'pill-matched' : 'pill-neutral'}`}
                style={{ cursor: 'pointer', border: 'none', padding: '3px 8px', fontSize: '0.7rem' }}
                onClick={() => setCandidateMode('preset')}
              >
                Benchmark Profile
              </button>
              <button
                className={`pill ${candidateMode === 'upload' ? 'pill-matched' : 'pill-neutral'}`}
                style={{ cursor: 'pointer', border: 'none', padding: '3px 8px', fontSize: '0.7rem' }}
                onClick={() => setCandidateMode('upload')}
              >
                Upload / Text
              </button>
            </div>
          </div>

          {candidateMode === 'preset' ? (
            <div>
              <label className="input-label" style={{ color: '#94a3b8' }}>Select Benchmark Candidate Profile</label>
              <select 
                className="input-select"
                value={candidateId}
                onChange={(e) => setCandidateId(e.target.value)}
              >
                {candidateList.map(c => (
                  <option key={c.candidate_id} value={c.candidate_id}>
                    {c.candidate_id} — {c.role} ({c.seniority} | {c.years_experience} yrs)
                  </option>
                ))}
              </select>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.7rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <input 
                  type="file" 
                  accept=".pdf,.docx,.txt"
                  id="deep-resume-upload"
                  style={{ display: 'none' }}
                  onChange={handleResumeFileUpload}
                />
                <label 
                  htmlFor="deep-resume-upload"
                  className="btn-secondary"
                  style={{ fontSize: '0.72rem', padding: '5px 10px', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '5px' }}
                >
                  <Upload size={13} /> {isUploadingResume ? 'Extracting Resume...' : 'Upload Resume File (.PDF / .DOCX / .TXT)'}
                </label>
                {customCand.filename && (
                  <span style={{ fontSize: '0.7rem', color: '#64748b' }}>{customCand.filename}</span>
                )}
              </div>
              <div>
                <label className="input-label" style={{ color: '#94a3b8' }}>Resume Text / Narrative</label>
                <textarea 
                  className="input-text"
                  rows={4}
                  placeholder="Paste candidate resume text here..."
                  value={customCand.raw_text}
                  onChange={(e) => setCustomCand(prev => ({ ...prev, raw_text: e.target.value }))}
                  style={{ resize: 'vertical', fontFamily: 'inherit', fontSize: '0.8rem' }}
                />
              </div>
              {customCand.skills && customCand.skills.length > 0 && (
                <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                  {customCand.skills.map((s, idx) => (
                    <span key={idx} className="pill pill-matched" style={{ fontSize: '0.68rem' }}>{s}</span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Target Job Box */}
        <div className="panel" style={{ background: '#0a0f19', border: '1px solid #1e293b', marginBottom: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.8rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#34d399' }}>Target Job Description</span>
            <div style={{ display: 'flex', gap: '4px', background: '#050811', padding: '2px', borderRadius: '6px' }}>
              <button
                className={`pill ${jobMode === 'preset' ? 'pill-matched' : 'pill-neutral'}`}
                style={{ cursor: 'pointer', border: 'none', padding: '3px 8px', fontSize: '0.7rem' }}
                onClick={() => setJobMode('preset')}
              >
                Benchmark Job
              </button>
              <button
                className={`pill ${jobMode === 'upload' ? 'pill-matched' : 'pill-neutral'}`}
                style={{ cursor: 'pointer', border: 'none', padding: '3px 8px', fontSize: '0.7rem' }}
                onClick={() => setJobMode('upload')}
              >
                Upload / Text
              </button>
            </div>
          </div>

          {jobMode === 'preset' ? (
            <div>
              <label className="input-label" style={{ color: '#94a3b8' }}>Select Benchmark Job Posting</label>
              <select 
                className="input-select"
                value={jobId}
                onChange={(e) => setJobId(e.target.value)}
              >
                {jobList.map(j => (
                  <option key={j.job_id} value={j.job_id}>
                    {j.job_id} — {j.job_title} ({j.industry})
                  </option>
                ))}
              </select>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.7rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <input 
                  type="file" 
                  accept=".pdf,.docx,.txt"
                  id="deep-job-upload"
                  style={{ display: 'none' }}
                  onChange={handleJobFileUpload}
                />
                <label 
                  htmlFor="deep-job-upload"
                  className="btn-secondary"
                  style={{ fontSize: '0.72rem', padding: '5px 10px', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '5px' }}
                >
                  <Upload size={13} /> {isUploadingJob ? 'Extracting JD...' : 'Upload JD File (.PDF / .DOCX / .TXT)'}
                </label>
                {customJob.job_title && (
                  <span style={{ fontSize: '0.7rem', color: '#64748b' }}>{customJob.job_title}</span>
                )}
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.6rem' }}>
                <div>
                  <label className="input-label" style={{ color: '#34d399', fontSize: '0.72rem' }}>Required Skills</label>
                  <input 
                    type="text"
                    className="input-text"
                    placeholder="e.g. Python, SQL"
                    value={customJob.required_skills}
                    onChange={(e) => setCustomJob(prev => ({ ...prev, required_skills: e.target.value }))}
                    style={{ fontSize: '0.78rem', padding: '0.45rem' }}
                  />
                </div>
                <div>
                  <label className="input-label" style={{ color: '#fbbf24', fontSize: '0.72rem' }}>Preferred Skills</label>
                  <input 
                    type="text"
                    className="input-text"
                    placeholder="e.g. Docker, AWS"
                    value={customJob.preferred_skills}
                    onChange={(e) => setCustomJob(prev => ({ ...prev, preferred_skills: e.target.value }))}
                    style={{ fontSize: '0.78rem', padding: '0.45rem' }}
                  />
                </div>
              </div>
              <div>
                <label className="input-label" style={{ color: '#94a3b8' }}>Job Description Text</label>
                <textarea 
                  className="input-text"
                  rows={2}
                  placeholder="Paste job description here..."
                  value={customJob.job_text}
                  onChange={(e) => setCustomJob(prev => ({ ...prev, job_text: e.target.value }))}
                  style={{ resize: 'vertical', fontFamily: 'inherit', fontSize: '0.8rem' }}
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Deep Match Report */}
      {loading ? (
        <div style={{ padding: '4rem', textAlign: 'center', color: '#94a3b8' }}>
          <RefreshCw className="animate-spin" size={32} style={{ margin: '0 auto 1rem auto', display: 'block', color: '#06b6d4' }} />
          Computing TF-IDF cosine projection and skill coverage vectors...
        </div>
      ) : matchResult ? (
        <div>
          {/* Main Score Hero Card */}
          <div className="panel" style={{ background: 'linear-gradient(135deg, #0e1726 0%, #111a2e 100%)', borderColor: '#23334d' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1.5rem', marginBottom: '1.5rem' }}>
              <div>
                <span className="pill" style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', border: '1px solid rgba(56, 189, 248, 0.3)' }}>
                  {matchResult.classification}
                </span>
                <h3 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#ffffff', marginTop: '6px' }}>
                  {matchResult.candidate.role} ↔ {matchResult.job.job_title}
                </h3>
                <span style={{ fontSize: '0.8rem', color: '#64748b', fontFamily: 'var(--font-mono)' }}>
                  Pair: {matchResult.candidate.candidate_id} vs {matchResult.job.job_id}
                </span>
              </div>

              {/* Score Badges */}
              <div style={{ display: 'flex', gap: '1.2rem', alignItems: 'center' }}>
                <div style={{ textAlign: 'center', background: '#090e18', padding: '0.8rem 1.4rem', borderRadius: '12px', border: '1px solid #10b981' }}>
                  <div style={{ fontSize: '0.72rem', color: '#34d399', fontWeight: 700 }}>OVERALL MATCH</div>
                  <div style={{ fontSize: '2.4rem', fontWeight: 900, color: '#ffffff', fontFamily: 'var(--font-display)', lineHeight: 1.1 }}>
                    {matchResult.overall_score}%
                  </div>
                </div>

                <div style={{ textAlign: 'center', background: '#090e18', padding: '0.8rem 1.2rem', borderRadius: '12px', border: '1px solid #1c273d' }}>
                  <div style={{ fontSize: '0.72rem', color: '#a78bfa', fontWeight: 700 }}>SKILL MATCH</div>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#a78bfa', fontFamily: 'var(--font-display)', lineHeight: 1.1 }}>
                    {matchResult.skill_score}%
                  </div>
                </div>

                <div style={{ textAlign: 'center', background: '#090e18', padding: '0.8rem 1.2rem', borderRadius: '12px', border: '1px solid #1c273d' }}>
                  <div style={{ fontSize: '0.72rem', color: '#38bdf8', fontWeight: 700 }}>TEXT SIMILARITY</div>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#38bdf8', fontFamily: 'var(--font-display)', lineHeight: 1.1 }}>
                    {matchResult.text_similarity_score}%
                  </div>
                </div>
              </div>
            </div>

            {/* Score Breakdown Bar */}
            <div style={{ width: '100%', height: '8px', background: '#1e293b', borderRadius: '4px', overflow: 'hidden', display: 'flex' }}>
              <div style={{ width: `${matchResult.overall_score}%`, background: 'linear-gradient(90deg, #10b981, #06b6d4)', transition: 'width 0.5s' }} />
            </div>
          </div>

          {/* 3-Column Skill Gap Visualizer */}
          <div className="section-title-wrap">
            <h3 className="section-title">
              <Award size={18} color="#f59e0b" /> Skill Gap Visualizer
            </h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.2rem', marginBottom: '2rem' }}>
            {/* Column 1: Matched Skills */}
            <div className="panel" style={{ borderTop: '3px solid #10b981' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem' }}>
                <CheckCircle size={18} color="#34d399" />
                <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff' }}>
                  Matched Skills ({matchResult.gap_analysis.all_matched_skills.length})
                </h4>
              </div>
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {matchResult.gap_analysis.all_matched_skills.length > 0 ? (
                  matchResult.gap_analysis.all_matched_skills.map((s, i) => (
                    <span key={i} className="pill pill-matched">{s}</span>
                  ))
                ) : (
                  <span style={{ fontSize: '0.85rem', color: '#64748b' }}>No direct skill overlaps.</span>
                )}
              </div>
            </div>

            {/* Column 2: Missing Required Skills (Critical Gap) */}
            <div className="panel" style={{ borderTop: '3px solid #f43f5e' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem' }}>
                <XCircle size={18} color="#fb7185" />
                <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff' }}>
                  Critical Gap: Missing Required ({matchResult.gap_analysis.missing_required.length})
                </h4>
              </div>
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {matchResult.gap_analysis.missing_required.length > 0 ? (
                  matchResult.gap_analysis.missing_required.map((s, i) => (
                    <span key={i} className="pill pill-missing-req">{s}</span>
                  ))
                ) : (
                  <span style={{ fontSize: '0.85rem', color: '#34d399' }}>
                    🎉 Full Coverage! All required skills matched.
                  </span>
                )}
              </div>
            </div>

            {/* Column 3: Missing Preferred Skills (Desirable Gap) */}
            <div className="panel" style={{ borderTop: '3px solid #f59e0b' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem' }}>
                <AlertTriangle size={18} color="#fbbf24" />
                <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff' }}>
                  Desirable Gap: Missing Preferred ({matchResult.gap_analysis.missing_preferred.length})
                </h4>
              </div>
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {matchResult.gap_analysis.missing_preferred.length > 0 ? (
                  matchResult.gap_analysis.missing_preferred.map((s, i) => (
                    <span key={i} className="pill pill-missing-pref">{s}</span>
                  ))
                ) : (
                  <span style={{ fontSize: '0.85rem', color: '#fbbf24' }}>
                    All preferred skills matched.
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Side by Side Profile vs Job Text */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.2rem' }}>
            <div className="panel">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.8rem' }}>
                <User size={18} color="#38bdf8" />
                <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff' }}>Candidate Narrative</h4>
              </div>
              <div style={{ background: '#080c14', padding: '1rem', borderRadius: '8px', fontSize: '0.85rem', color: '#cbd5e1', lineHeight: 1.6, maxHeight: '250px', overflowY: 'auto' }}>
                {matchResult.candidate.resume_text}
              </div>
            </div>

            <div className="panel">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.8rem' }}>
                <Briefcase size={18} color="#34d399" />
                <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff' }}>Job Specification</h4>
              </div>
              <div style={{ background: '#080c14', padding: '1rem', borderRadius: '8px', fontSize: '0.85rem', color: '#cbd5e1', lineHeight: 1.6, maxHeight: '250px', overflowY: 'auto' }}>
                {matchResult.job.job_text}
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
