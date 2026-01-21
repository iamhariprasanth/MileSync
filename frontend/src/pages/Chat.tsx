import { useState, useRef, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import type { ChatMessage, ChatSession } from '../types/chat';
import * as chatApi from '../api/chat';

export default function Chat() {
  const [searchParams] = useSearchParams();
  const sessionIdParam = searchParams.get('session');

  const [session, setSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    initializeChat();
  }, [sessionIdParam]);

  async function initializeChat() {
    setIsInitializing(true);
    setError(null);

    try {
      if (sessionIdParam) {
        // Load existing session
        const data = await chatApi.getSession(parseInt(sessionIdParam));
        setSession(data.session);
        setMessages(data.messages);
      } else {
        // Start new session
        const data = await chatApi.startChat();
        setSession(data.session);
        setMessages([data.initial_message]);
        // Update URL with session ID without navigation
        window.history.replaceState(null, '', `/chat?session=${data.session.id}`);
      }
    } catch (err) {
      setError('Failed to initialize chat. Please try again.');
      console.error('Chat init error:', err);
    } finally {
      setIsInitializing(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || isLoading || !session) return;

    const userContent = input.trim();
    setInput('');
    setIsLoading(true);
    setError(null);

    // Optimistic update: add user message immediately
    const tempUserMessage: ChatMessage = {
      id: Date.now(),
      session_id: session.id,
      role: 'user',
      content: userContent,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMessage]);

    try {
      const response = await chatApi.sendMessage(session.id, { content: userContent });
      // Replace temp message with real one and add assistant response
      setMessages((prev) => [
        ...prev.slice(0, -1),
        response.user_message,
        response.assistant_message,
      ]);
    } catch (err) {
      setError('Failed to send message. Please try again.');
      // Remove the optimistic message on error
      setMessages((prev) => prev.slice(0, -1));
      console.error('Send message error:', err);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleFinalize() {
    if (!session) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await chatApi.finalizeSession(session.id);
      // Navigate to the created goal
      navigate(`/goals/${response.goal.id}`);
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to finalize chat. Please try again.';
      setError(message);
      console.error('Finalize error:', err);
      setIsLoading(false);
    }
  }

  function handleNewChat() {
    navigate('/chat');
    window.location.reload();
  }

  if (isInitializing) {
    return (
      <div className="max-w-4xl mx-auto h-[calc(100vh-4rem)] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Starting your coaching session...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-4rem)] flex flex-col">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">AI Goal Coach</h1>
          <p className="text-sm text-gray-500">
            {session?.title || 'Define your goal through conversation'}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleNewChat}
            className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
          >
            New Chat
          </button>
          {messages.length > 3 && session?.status === 'active' && (
            <button
              onClick={handleFinalize}
              disabled={isLoading}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium disabled:opacity-50"
            >
              Create Goal & Roadmap
            </button>
          )}
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="bg-red-50 border-b border-red-200 px-6 py-3">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((message) => (
          <ChatMessageBubble key={message.id} message={message} />
        ))}
        {isLoading && (
          <div className="flex items-start">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center mr-3">
              <span className="text-sm">AI</span>
            </div>
            <div className="bg-gray-100 rounded-2xl rounded-tl-none px-4 py-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: '0.1s' }}
                />
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: '0.2s' }}
                />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t px-6 py-4">
        {session?.status === 'active' ? (
          <form onSubmit={handleSubmit} className="flex space-x-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Tell me about your goal..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </form>
        ) : (
          <div className="text-center text-gray-500 py-2">
            This session has been finalized.{' '}
            <button onClick={handleNewChat} className="text-blue-600 hover:underline">
              Start a new chat
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function ChatMessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex items-start ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium ${
          isUser ? 'bg-blue-600 text-white ml-3' : 'bg-blue-100 text-blue-600 mr-3'
        }`}
      >
        {isUser ? 'You' : 'AI'}
      </div>
      <div
        className={`max-w-[70%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white rounded-tr-none'
            : 'bg-gray-100 text-gray-900 rounded-tl-none'
        }`}
      >
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
      </div>
    </div>
  );
}
