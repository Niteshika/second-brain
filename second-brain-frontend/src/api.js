// Base URL of your FastAPI backend.
// Change this if your backend runs on a different port.
const API_BASE = 'http://127.0.0.1:8000';

function getToken() {
  return localStorage.getItem('token');
}

async function request(path, { method = 'GET', body, auth = false } = {}) {
  const headers = { 'Content-Type': 'application/json' };

  if (auth) {
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  let data = null;
  try {
    data = await response.json();
  } catch {
    // no JSON body, that's fine for some responses
  }

  if (!response.ok) {
    const message = data?.detail || 'Something went wrong. Please try again.';
    throw new Error(typeof message === 'string' ? message : JSON.stringify(message));
  }

  return data;
}

export const api = {
  signup: (email, password) =>
    request('/signup', { method: 'POST', body: { email, password } }),

  login: (email, password) =>
    request('/login', { method: 'POST', body: { email, password } }),

  chat: (message) =>
    request('/chat', { method: 'POST', body: { message }, auth: true }),

  // Kicks off the background analysis job, returns { job_id }
  startKnowledgeGapJob: () =>
    request('/knowledge-gap/run', { method: 'POST', auth: true }),

  // Checks a job's status: { status: 'running'|'done'|'error', result, error }
  getKnowledgeGapStatus: (jobId) =>
    request(`/knowledge-gap/status/${jobId}`, { method: 'GET', auth: true }),

  // Streaming chat — calls onChunk(text) every time a new piece arrives
  chatStream: async (message, onChunk) => {
    const token = getToken();
    const response = await fetch(`${API_BASE}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok || !response.body) {
      throw new Error('Streaming request failed.');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const text = decoder.decode(value, { stream: true });
      onChunk(text);
    }
  },
};
