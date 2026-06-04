import { useState, useEffect, useRef } from 'react';
import { chatApi, ChatSession, ChatMessage } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Header } from '../components/Header';
import { formatDate } from '../lib/utils';
import { Send, MessageCircle, Plus, Loader2 } from 'lucide-react';

export function ChatPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    if (currentSession) {
      loadMessages(currentSession.id);
    }
  }, [currentSession]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadSessions = async () => {
    try {
      const res = await chatApi.listSessions();
      setSessions(res.data);
      if (res.data.length > 0 && !currentSession) {
        setCurrentSession(res.data[0]);
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const loadMessages = async (sessionId: number) => {
    setLoading(true);
    try {
      const res = await chatApi.getMessages(sessionId);
      setMessages(res.data);
    } catch (error) {
      console.error('Failed to load messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || sending) return;

    const userMessage = input.trim();
    setInput('');
    setSending(true);

    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        role: 'user',
        content: userMessage,
        session_id: currentSession?.id || 0,
        token_count: 0,
        created_at: new Date().toISOString(),
      },
    ]);

    try {
      const res = await chatApi.sendMessage({
        message: userMessage,
        session_id: currentSession?.id,
        use_history: true,
      });

      if (!currentSession) {
        const sessionsRes = await chatApi.listSessions();
        setSessions(sessionsRes.data);
        setCurrentSession(sessionsRes.data[0]);
      }

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: res.data.message,
          session_id: res.data.session_id,
          token_count: res.data.token_count,
          created_at: new Date().toISOString(),
        },
      ]);

      await loadSessions();
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setSending(false);
    }
  };

  const handleNewChat = async () => {
    try {
      const res = await chatApi.createSession({ title: 'New Chat' });
      setSessions([res.data, ...sessions]);
      setCurrentSession(res.data);
      setMessages([]);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="container mx-auto py-8 px-4">
        <div className="grid grid-cols-4 gap-6 h-[calc(100vh-12rem)]">
          <div className="col-span-1 bg-white rounded-lg shadow p-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-semibold">对话列表</h2>
              <Button size="sm" variant="ghost" onClick={handleNewChat}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            <div className="space-y-2">
              {sessions.map((session) => (
                <button
                  key={session.id}
                  className={`w-full text-left p-2 rounded-md text-sm transition-colors ${
                    currentSession?.id === session.id
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-gray-100'
                  }`}
                  onClick={() => setCurrentSession(session)}
                >
                  {session.title || 'New Chat'}
                </button>
              ))}
            </div>
          </div>

          <div className="col-span-3 bg-white rounded-lg shadow flex flex-col">
            <div className="p-4 border-b">
              <h2 className="font-semibold">
                {currentSession?.title || '新对话'}
              </h2>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 && !loading && (
                <div className="text-center text-muted-foreground py-12">
                  <MessageCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>开始一个新对话吧</p>
                </div>
              )}

              {loading && (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin" />
                </div>
              )}

              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] rounded-lg px-4 py-2 ${
                      msg.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-gray-100'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                    <p className={`text-xs mt-1 ${
                      msg.role === 'user' ? 'text-primary-foreground/70' : 'text-muted-foreground'
                    }`}>
                      {formatDate(msg.created_at)}
                    </p>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            <div className="p-4 border-t">
              <form onSubmit={handleSend} className="flex gap-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="输入问题..."
                  disabled={sending}
                />
                <Button type="submit" disabled={sending || !input.trim()}>
                  {sending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}