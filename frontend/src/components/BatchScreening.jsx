import React, { useState, useEffect } from 'react';
import { 
  Upload, FileText, CheckCircle, AlertTriangle, 
  Trash2, Play, Download, RefreshCw, Sparkles 
} from 'lucide-react';

export default function BatchScreening() {
  const [jobs, setJobs] = useState([]);
  const [jobMode, setJobMode] = useState('preset'); // 'preset' | 'manual'
  const [selectedJobId, setSelectedJobId] = useState('J_000000');
  
  // Manual Job Description State
  const [manualJob, setManualJob] = useState({
    job_title: 'Senior Software Engineer',
    required_skills: 'Python, SQL, Machine Learning, Git',
    preferred_skills: 'Docker, AWS, FastAPI',
    job_text: 'We are seeking a Senior Software Engineer with strong problem-solving skills to build scalable pipelines. Responsibilities include designing database models, building APIs in Python, and deploying containerized applications.',
  });
  const [isUploadingJd, setIsUploadingJd] = useState(false);

  const [uploadedResumes, setUploadedResumes] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isScreening, setIsScreening] = useState(false);
  const [results, setResults] = useState([]);

  useEffect(() => {
    fetch('/api/jobs?limit=50')
      .then(res => res.json())
      .then(data => {
        setJobs(data.jobs || []);
        if (data.jobs && data.jobs.length > 0) {
          setSelectedJobId(data.jobs[0].job_id);
        }
      });
  }, []);

  const handleJdFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploadingJd(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/upload-job', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!data.error) {
        setManualJob({
          job_title: data.job_title || file.name.replace(/\.[^/.]+$/, ""),
          required_skills: (data.required_skills || []).join(', '),
          preferred_skills: (data.preferred_skills || []).join(', '),
          job_text: data.raw_text || '',
        });
        setJobMode('manual');
      }
    } catch (err) {
      console.error("Job description upload failed:", err);
    } finally {
      setIsUploadingJd(false);
    }
  };

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;

    setIsUploading(true);
    for (const file of files) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const res = await fetch('/api/upload-resume', {
          method: 'POST',
          body: formData,
        });
        const data = await res.json();
        if (!data.error) {
          setUploadedResumes(prev => [...prev, {
            id: `UPLOAD_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`,
            filename: data.filename,
            char_count: data.char_count,
            word_count: data.word_count,
            skills: data.skills,
            raw_text: data.raw_text,
          }]);
        }
      } catch (err) {
        console.error("Upload failed for", file.name, err);
      }
    }
    setIsUploading(false);
  };

  const handleRunScreening = async () => {
    if (!uploadedResumes.length) return;
    setIsScreening(true);

    const payloadJob = jobMode === 'preset' 
      ? { job_id: selectedJobId }
      : {
          custom_job: {
            job_id: 'CUSTOM_JOB',
            job_title: manualJob.job_title || 'Custom Job Position',
            required_skills: manualJob.required_skills.split(',').map(s => s.trim()).filter(Boolean),
            preferred_skills: manualJob.preferred_skills.split(',').map(s => s.trim()).filter(Boolean),
            job_text: manualJob.job_text || `${manualJob.job_title}. Required: ${manualJob.required_skills}. Preferred: ${manualJob.preferred_skills}.`,
          }
        };

    const screened = [];
    for (const resume of uploadedResumes) {
      try {
        const res = await fetch('/api/deep-match', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            custom_candidate: {
              candidate_id: resume.filename,
              role: 'Uploaded Resume',
              skills: resume.skills,
              resume_text: resume.raw_text,
            },
            ...payloadJob,
          })
        });
        const match = await res.json();
        screened.push({
          filename: resume.filename,
          skills: resume.skills,
          overall_score: match.overall_score,
          skill_score: match.skill_score,
          text_score: match.text_similarity_score,
          classification: match.classification,
          matched_skills: match.gap_analysis?.all_matched_skills || [],
          missing_required: match.gap_analysis?.missing_required || [],
        });
      } catch (err) {
        console.error("Screening failed for", resume.filename, err);
      }
    }

    screened.sort((a, b) => b.overall_score - a.overall_score);
    setResults(screened);
    setIsScreening(false);
  };

  const removeResume = (index) => {
    setUploadedResumes(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div>
      <div className="section-title-wrap">
        <div>
          <h2 className="section-title">
            <Upload size={22} color="#3b82f6" />
            Batch Resume Screening & Parsing
          </h2>
          <p className="section-subtitle">
            Upload candidate resumes (PDF, DOCX, TXT) and automatically rank them against target job descriptions (preset or manually entered).
          </p>
        </div>
        {uploadedResumes.length > 0 && (
          <button 
            className="btn-primary"
            onClick={handleRunScreening}
            disabled={isScreening}
            style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #10b981 100%)', color: '#090d16' }}
          >
            {isScreening ? <RefreshCw className="animate-spin" size={16} /> : <Play size={16} />}
            Screen {uploadedResumes.length} Resumes
          </button>
        )}
      </div>

      {/* Target Job Definition (Preset vs Manual Mode) */}
      <div className="panel" style={{ background: '#0a0f19', border: '1px solid #1e293b' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.8rem' }}>
          <div>
            <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#38bdf8' }}>Target Job Description</span>
            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Select a benchmark job or type/upload your custom requirements</div>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', background: '#050811', padding: '3px', borderRadius: '8px', border: '1px solid #1e293b' }}>
            <button
              className={`pill ${jobMode === 'preset' ? 'pill-matched' : 'pill-neutral'}`}
              style={{ cursor: 'pointer', border: 'none', padding: '5px 12px', fontSize: '0.75rem', fontWeight: 600 }}
              onClick={() => setJobMode('preset')}
            >
              Select Benchmark Job
            </button>
            <button
              className={`pill ${jobMode === 'manual' ? 'pill-matched' : 'pill-neutral'}`}
              style={{ cursor: 'pointer', border: 'none', padding: '5px 12px', fontSize: '0.75rem', fontWeight: 600 }}
              onClick={() => setJobMode('manual')}
            >
              Enter JD Manually
            </button>
          </div>
        </div>

        {jobMode === 'preset' ? (
          <div>
            <label className="input-label" style={{ color: '#94a3b8' }}>Select Target Job Posting</label>
            <select 
              className="input-select"
              value={selectedJobId}
              onChange={(e) => setSelectedJobId(e.target.value)}
            >
              {jobs.map(j => (
                <option key={j.job_id} value={j.job_id}>
                  {j.job_id} — {j.job_title} ({j.industry})
                </option>
              ))}
            </select>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.8rem', color: '#a78bfa', fontWeight: 600 }}>Manual Job Description & Requirements</span>
              <div>
                <input 
                  type="file" 
                  accept=".pdf,.docx,.txt"
                  id="batch-jd-file-upload"
                  style={{ display: 'none' }}
                  onChange={handleJdFileUpload}
                />
                <label 
                  htmlFor="batch-jd-file-upload"
                  className="btn-secondary"
                  style={{ fontSize: '0.72rem', padding: '4px 10px', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '5px' }}
                >
                  <FileText size={13} /> {isUploadingJd ? 'Extracting JD...' : 'Upload JD Document (.PDF / .DOCX / .TXT)'}
                </label>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.8rem' }}>
              <div>
                <label className="input-label" style={{ color: '#94a3b8' }}>Job Title</label>
                <input 
                  type="text"
                  className="input-text"
                  placeholder="e.g. Senior Machine Learning Engineer"
                  value={manualJob.job_title}
                  onChange={(e) => setManualJob(prev => ({ ...prev, job_title: e.target.value }))}
                />
              </div>
              <div>
                <label className="input-label" style={{ color: '#34d399' }}>Must-Have Required Skills (comma-separated)</label>
                <input 
                  type="text"
                  className="input-text"
                  placeholder="e.g. Python, SQL, Machine Learning"
                  value={manualJob.required_skills}
                  onChange={(e) => setManualJob(prev => ({ ...prev, required_skills: e.target.value }))}
                />
              </div>
              <div>
                <label className="input-label" style={{ color: '#fbbf24' }}>Nice-To-Have Preferred Skills (comma-separated)</label>
                <input 
                  type="text"
                  className="input-text"
                  placeholder="e.g. Docker, AWS, PyTorch"
                  value={manualJob.preferred_skills}
                  onChange={(e) => setManualJob(prev => ({ ...prev, preferred_skills: e.target.value }))}
                />
              </div>
            </div>

            <div>
              <label className="input-label" style={{ color: '#94a3b8' }}>Job Description / Responsibilities Text</label>
              <textarea 
                className="input-text"
                rows={3}
                placeholder="Paste the full job description or responsibilities here..."
                value={manualJob.job_text}
                onChange={(e) => setManualJob(prev => ({ ...prev, job_text: e.target.value }))}
                style={{ resize: 'vertical', fontFamily: 'inherit' }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Upload Dropzone */}
      <div 
        className="panel"
        style={{
          border: '2px dashed #23334d',
          background: '#090e18',
          textAlign: 'center',
          padding: '2.5rem 1.5rem',
          cursor: 'pointer',
        }}
      >
        <Upload size={36} color="#38bdf8" style={{ margin: '0 auto 1rem auto' }} />
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#ffffff', marginBottom: '0.4rem' }}>
          Upload Candidate Resumes
        </h3>
        <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '1.2rem' }}>
          Supports PDF, DOCX, and plain TXT files. Automatic text extraction and skill lexicon matching.
        </p>
        <input 
          type="file" 
          multiple 
          accept=".pdf,.docx,.txt"
          onChange={handleFileUpload}
          style={{ display: 'none' }}
          id="resume-upload-input"
        />
        <label 
          htmlFor="resume-upload-input" 
          className="btn-primary"
          style={{ cursor: 'pointer' }}
        >
          {isUploading ? 'Extracting & Parsing...' : 'Select Files to Upload'}
        </label>
      </div>

      {/* Uploaded Queue */}
      {uploadedResumes.length > 0 && (
        <div className="panel">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff' }}>
              Uploaded Queue ({uploadedResumes.length} Documents)
            </h3>
            <button 
              className="btn-secondary" 
              onClick={() => { setUploadedResumes([]); setResults([]); }}
              style={{ fontSize: '0.75rem', padding: '4px 10px' }}
            >
              Clear Queue
            </button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '0.8rem' }}>
            {uploadedResumes.map((r, i) => (
              <div 
                key={r.id}
                style={{
                  background: '#080c14',
                  border: '1px solid #1a2538',
                  borderRadius: '8px',
                  padding: '0.8rem 1rem',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                }}
              >
                <div>
                  <div style={{ fontWeight: 700, color: '#ffffff', fontSize: '0.9rem' }}>{r.filename}</div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                    {r.word_count} words • {r.skills.length} skills detected
                  </div>
                  <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginTop: '6px' }}>
                    {r.skills.slice(0, 4).map((s, idx) => (
                      <span key={idx} className="pill pill-matched" style={{ fontSize: '0.68rem' }}>{s}</span>
                    ))}
                    {r.skills.length > 4 && (
                      <span className="pill pill-neutral" style={{ fontSize: '0.68rem' }}>+{r.skills.length - 4}</span>
                    )}
                  </div>
                </div>
                <button 
                  onClick={() => removeResume(i)}
                  style={{ background: 'transparent', border: 'none', color: '#fb7185', cursor: 'pointer', padding: '4px' }}
                >
                  <Trash2 size={15} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Screened Batch Results */}
      {results.length > 0 && (
        <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid #1c273d' }}>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#ffffff' }}>
              Batch Screening Results (Ranked by Compatibility)
            </h3>
          </div>
          <table className="results-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Resume Filename</th>
                <th>Classification</th>
                <th>Overall Match</th>
                <th>Skill Score</th>
                <th>Text Similarity</th>
                <th>Missing Critical Skills</th>
              </tr>
            </thead>
            <tbody>
              {results.map((r, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 800, color: '#94a3b8', fontFamily: 'var(--font-mono)' }}>#{i + 1}</td>
                  <td style={{ fontWeight: 700, color: '#ffffff' }}>{r.filename}</td>
                  <td>
                    <span className="pill pill-neutral">{r.classification}</span>
                  </td>
                  <td>
                    <span className={`score-badge ${r.overall_score >= 70 ? 'score-high' : r.overall_score < 45 ? 'score-low' : 'score-mid'}`}>
                      {r.overall_score}%
                    </span>
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', color: '#a78bfa', fontWeight: 600 }}>{r.skill_score}%</td>
                  <td style={{ fontFamily: 'var(--font-mono)', color: '#38bdf8', fontWeight: 600 }}>{r.text_score}%</td>
                  <td>
                    <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                      {r.missing_required.length > 0 ? (
                        r.missing_required.map((s, idx) => (
                          <span key={idx} className="pill pill-missing-req" style={{ fontSize: '0.7rem' }}>{s}</span>
                        ))
                      ) : (
                        <span style={{ fontSize: '0.75rem', color: '#34d399' }}>Full match</span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
