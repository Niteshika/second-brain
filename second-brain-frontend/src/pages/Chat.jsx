import { useEffect, useRef, useState } from 'react';
import { api } from '../api';
import Layout from '../components/Layout';

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const historyRef = useRef(null);

  useEffect(() => {
    if (historyRef.current) {
      historyRef.current.scrollTop = historyRef.current.scrollHeight;
    }
  }, [messages, sending]);

  async function handleSend(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text || sending) return;

    setMessages((prev) => [...prev, { role: 'human', content: text }]);
    setInput('');
    setSending(true);

    // Add an empty AI bubble that we'll fill in as chunks arrive
    setMessages((prev) => [...prev, { role: 'ai', content: '' }]);
  
    try {
      await api.chatStream(text, (chunk) => {
        setMessages((prev) => {
          const updated = [...prev];
          const lastIndex = updated.length - 1;
          updated[lastIndex] = {
            ...updated[lastIndex],
            content: updated[lastIndex].content + chunk,
          };
          return updated;
        });
      });
    } catch (err) {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = { role: 'ai', content: `Error: ${err.message}` };
        return updated;
      });
    } finally {
      setSending(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  }

  return (
    <Layout>
      <div className="chat-page">
        <div className="chat-history" ref={historyRef}>
          {messages.length === 0 && (
            <div className="chat-empty">
              <div className="chat-empty-title">Ask your notes something</div>
              <div>Your Second Brain remembers past turns in this conversation.</div>
            </div>
          )}

          {messages.map((m, i) => (
            <div key={i} className={`bubble-row ${m.role}`}>
              <div className={`bubble ${m.role}`}>{m.content}</div>
            </div>
          ))}

          {sending && (
            <div className="bubble-row ai">
              <div className="bubble ai pending">thinking…</div>
            </div>
          )}
        </div>

        <form className="chat-input-row" onSubmit={handleSend}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your notes… (Enter to send, Shift+Enter for new line)"
            rows={1}
          />
          <button className="send-btn" type="submit" disabled={sending || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </Layout>
  );
}
