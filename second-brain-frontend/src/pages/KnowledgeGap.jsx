import { useEffect, useRef, useState } from 'react';
import { api } from '../api';
import Layout from '../components/Layout';

const POLL_INTERVAL_MS = 3000;

export default function KnowledgeGap() {
  // 'idle' | 'running' | 'done' | 'error'
  const [status, setStatus] = useState('idle');
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const pollRef = useRef(null);

  // Stop any in-flight polling if the user navigates away
  useEffect(() => {
    return () => clearTimeout(pollRef.current);
  }, []);

  async function pollStatus(jobId) {
    try {
      const data = await api.getKnowledgeGapStatus(jobId);

      if (data.status === 'done') {
        setResult(data.result);
        setStatus('done');
        return;
      }

      if (data.status === 'error') {
        setErrorMessage(data.error || 'Analysis failed.');
        setStatus('error');
        return;
      }

      // still running — poll again after a delay
      pollRef.current = setTimeout(() => pollStatus(jobId), POLL_INTERVAL_MS);
    } catch (err) {
      setErrorMessage(err.message);
      setStatus('error');
    }
  }

  async function handleRunAnalysis() {
    setStatus('running');
    setErrorMessage('');
    setResult(null);
    try {
      const { job_id } = await api.startKnowledgeGapJob();
      pollStatus(job_id);
    } catch (err) {
      setErrorMessage(err.message);
      setStatus('error');
    }
  }

  return (
    <Layout>
      <div className="kg-header">
        <h1 className="kg-title">Knowledge Gap Dashboard</h1>
        <p className="kg-subtitle">
          Clusters, blind spots, contradictions, and stale notes across your Second Brain.
        </p>
      </div>

      {status === 'idle' && (
        <button className="btn-primary" style={{ maxWidth: 220 }} onClick={handleRunAnalysis}>
          Run analysis
        </button>
      )}

      {status === 'running' && (
        <div className="kg-card" style={{ maxWidth: 420 }}>
          <div className="kg-card-title">Analyzing your notes…</div>
          <p className="kg-card-desc">
            This runs clustering and several LLM calls, so it can take anywhere from
            30 seconds to a couple of minutes depending on how many notes you have.
          </p>
        </div>
      )}

      {status === 'error' && (
        <div className="error-banner" style={{ maxWidth: 420 }}>
          {errorMessage}
        </div>
      )}

      {status === 'done' && result && (
        <>
          <div style={{ marginBottom: 20 }}>
            <button className="logout-btn" onClick={handleRunAnalysis}>
              Re-run analysis
            </button>
          </div>

          <h2 className="kg-section-title">Topic clusters</h2>
          <div className="kg-grid">
            {result.clusters.map((c, i) => (
              <div className="kg-card" key={i}>
                <div className="kg-card-label">{c.chunk_count} chunks</div>
                <h3 className="kg-card-title">{c.name}</h3>
                <p className="kg-card-desc">{c.sources.join(', ')}</p>
              </div>
            ))}
          </div>

          <h2 className="kg-section-title">Blind spots</h2>
          <div className="kg-grid">
            {result.blind_spots.map((b, i) => (
              <div className="kg-card" key={i}>
                <h3 className="kg-card-title">{b.topic}</h3>
                <p className="kg-card-desc">{b.description}</p>
              </div>
            ))}
          </div>

          <h2 className="kg-section-title">Contradictions</h2>
          <div style={{ marginBottom: 32 }}>
            {result.contradictions.length === 0 && (
              <p className="kg-card-desc">None detected.</p>
            )}
            {result.contradictions.map((c, i) => (
              <div className="kg-card" key={i} style={{ marginBottom: 12 }}>
                <div className="kg-card-label">
                  {c.source_1} vs {c.source_2}
                </div>
                <p className="kg-card-desc">{c.reason}</p>
              </div>
            ))}
          </div>

          <h2 className="kg-section-title">Stale notes</h2>
          <div>
            {result.stale_notes.map((note, i) => (
              <div className="kg-list-item" key={i}>
                <span>{note.title}</span>
                <span className="kg-tag stale">{note.age_days}d stale</span>
              </div>
            ))}
          </div>
        </>
      )}
    </Layout>
  );
}
