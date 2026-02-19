import React, { useState } from 'react';
import { api } from '../lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatPanelProps {
  sessionId: string;
}

/**
 * If the reply is JSON with assistant_reply, return only that for display.
 * Otherwise return the original content (e.g. plain text or error messages).
 */
function getDisplayContent(content: string): string {
  if (content == null || typeof content !== 'string') return String(content ?? '');
  const trimmed = content.trim();
  if (!trimmed) return content;
  try {
    const parsed = JSON.parse(trimmed) as unknown;
    if (parsed && typeof parsed === 'object' && 'assistant_reply' in parsed) {
      const reply = (parsed as { assistant_reply: unknown }).assistant_reply;
      if (typeof reply === 'string') return reply;
    }
  } catch {
    // Not JSON or invalid; show as-is
  }
  return content;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ sessionId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMessage: Message = { role: 'user', content: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    try {
      setLoading(true);
      const resp = await api.post('/chat', {
        user_id: null,
        message: userMessage.content,
        session_id: sessionId
      });
      const data = resp.data as { reply: string };
      setMessages((prev) => [...prev, { role: 'assistant', content: data.reply }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, something went wrong talking to AROMI.'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown: React.KeyboardEventHandler<HTMLTextAreaElement> = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      void sendMessage();
    }
  };

  return (
    <div className="glass-card h-full flex flex-col">
      <div className="p-4 border-b border-white/5">
        <div className="text-sm font-semibold">AROMI AI Coach</div>
        <div className="text-xs text-muted-foreground mt-1">
          Ask about workouts, recovery, or nutrition. AROMI may call tools under the hood to
          tailor answers.
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`max-w-[80%] px-3 py-2 rounded-2xl text-sm ${
              m.role === 'user'
                ? 'ml-auto bg-primary text-primary-foreground'
                : 'mr-auto bg-muted text-foreground'
            }`}
          >
            {m.role === 'assistant' ? getDisplayContent(m.content) : m.content}
          </div>
        ))}
        {messages.length === 0 && (
          <div className="text-xs text-muted-foreground">
            Start a conversation with AROMI to get a personalized fitness guidance.
          </div>
        )}
      </div>

      <div className="p-3 border-t border-white/5">
        <div className="flex gap-2">
          <textarea
            className="flex-1 resize-none rounded-xl bg-muted/80 border border-white/5 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/70"
            rows={2}
            placeholder="Type your question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button
            type="button"
            onClick={() => void sendMessage()}
            disabled={loading}
            className="self-end px-4 py-2 rounded-xl bg-primary text-primary-foreground text-sm font-medium disabled:opacity-60"
          >
            {loading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
};

