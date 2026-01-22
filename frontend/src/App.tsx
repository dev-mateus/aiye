/**
 * Componente principal da aplicação
 */

import { useState, useEffect, useRef } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Analytics } from "@vercel/analytics/react";
import { SpeedInsights } from "@vercel/speed-insights/react";
import { ChatBox } from "./components/ChatBox";
import { AnswerCard } from "./components/AnswerCard";
import AdminPage from "./components/AdminPage";
import { ask, healthCheck, AskResponse } from "./api";
import "./styles.css";

interface ChatMessage {
  question: string;
  response: AskResponse;
}

// Perguntas sugeridas para empty state
const SUGGESTED_QUESTIONS = [
  "O que é Umbanda?",
  "Quais são os Orixás principais?",
  "Como funciona uma gira de Umbanda?",
  "Qual a diferença entre Umbanda e Candomblé?",
];

function ChatPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isBackendOnline, setIsBackendOnline] = useState(true);
  const [pendingQuestion, setPendingQuestion] = useState<string>("");
  const lastMessageRef = useRef<HTMLDivElement>(null);

  // Verifica saúde do backend ao montar
  useEffect(() => {
    const checkBackend = async () => {
      const online = await healthCheck();
      setIsBackendOnline(online);
      if (!online) {
        setError(
          "⚠️ Backend não está disponível. Certifique-se que o servidor está rodando em http://localhost:8000"
        );
      }
    };
    checkBackend();
  }, []);

  // Auto-scroll quando nova mensagem é adicionada
  useEffect(() => {
    if (chatHistory.length > 0 && lastMessageRef.current) {
      setTimeout(() => {
        lastMessageRef.current?.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'start' 
        });
      }, 100);
    }
  }, [chatHistory.length]);

  const handleAsk = async (question: string) => {
    if (!isBackendOnline) {
      setError("Backend não está disponível");
      return;
    }

    setIsLoading(true);
    setError(null);
    setPendingQuestion(question);

    try {
      // Converte histórico para o formato esperado pelo backend
      const history = chatHistory.map(msg => ({
        question: msg.question,
        answer: msg.response.answer
      }));
      
      const result = await ask(question, history);
      // Adiciona a nova mensagem ao histórico
      setChatHistory(prev => [...prev, { question, response: result }]);
      // Limpa a pendingQuestion para resetar o input
      setPendingQuestion("");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Erro ao comunicar com o servidor"
      );
      setPendingQuestion("");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-umbanda-bg">
      {/* Progress Bar */}
      {isLoading && (
        <div className="fixed top-0 left-0 right-0 h-1 bg-gradient-to-r from-umbanda-primary via-umbanda-forest to-umbanda-accent z-50 progress-bar" />
      )}

      {/* Header Minimalista */}
      <div className="flex-shrink-0 border-b border-umbanda-border bg-umbanda-dark/95 backdrop-blur-sm shadow-lg">
        <div className="max-w-4xl mx-auto px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-umbanda-gold to-umbanda-amber flex items-center justify-center shadow-lg">
              <span className="text-lg">🕯️</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-umbanda-text">
                Aiye
              </h1>
              <p className="text-xs text-umbanda-text-muted">
                Sabedoria da Umbanda
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Área de Mensagens com Scroll */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-6">
          {/* Status do Backend */}
          {!isBackendOnline && (
            <div className="mb-6 bg-red-900/20 border border-red-700/50 text-red-300 px-4 py-3 rounded-xl flex items-start gap-3">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div>
                <p className="font-semibold">Backend Offline</p>
                <p className="text-sm mt-1">
                  Inicie o servidor: <code className="bg-red-950/50 px-2 py-1 rounded">
                    uvicorn backend.main:app --reload --port 8000
                  </code>
                </p>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-6 bg-orange-900/20 border border-orange-700/50 text-orange-300 px-4 py-3 rounded-xl">
              <p className="font-semibold">⚠️ Erro</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
          )}

          {/* Empty State com perguntas sugeridas */}
          {chatHistory.length === 0 && (
            <div className="py-12 space-y-8">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-umbanda-gold to-umbanda-amber mb-4 shadow-lg">
                  <span className="text-3xl">✨</span>
                </div>
                <h2 className="text-2xl font-bold text-umbanda-text mb-2">
                  Como posso ajudar?
                </h2>
                <p className="text-umbanda-text-muted">
                  Pergunte sobre Umbanda, Orixás, rituais e ensinamentos
                </p>
              </div>
              
              {/* Perguntas Sugeridas */}
              <div className="max-w-2xl mx-auto">
                <div className="grid grid-cols-1 gap-3">
                  {SUGGESTED_QUESTIONS.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => handleAsk(question)}
                      disabled={isLoading}
                      className="text-left p-4 bg-umbanda-card border border-umbanda-border rounded-xl hover:border-umbanda-primary hover:bg-umbanda-dark hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-xl">💬</span>
                        <span className="text-sm text-umbanda-text group-hover:text-umbanda-forest font-medium">
                          {question}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Histórico de Conversas - Estilo ChatGPT */}
          {chatHistory.map((message, index) => (
            <div key={index} className="space-y-4 mb-6">
              {/* Pergunta do Usuário */}
              <div className="flex gap-3 justify-end">
                <div className="max-w-[80%] bg-umbanda-card border border-umbanda-border rounded-2xl rounded-tr-sm px-4 py-3 shadow-md">
                  <p className="text-umbanda-text">
                    {message.question}
                  </p>
                </div>
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-umbanda-primary to-umbanda-forest flex items-center justify-center shadow-lg">
                  <span className="text-white text-sm">👤</span>
                </div>
              </div>
              
              {/* Resposta da IA */}
              <div 
                className="flex gap-3"
                ref={index === chatHistory.length - 1 ? lastMessageRef : null}
              >
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-umbanda-gold to-umbanda-amber flex items-center justify-center shadow-lg">
                  <span className="text-lg">🕯️</span>
                </div>
                <div className="flex-1 max-w-[85%]">
                  <AnswerCard
                    answer={message.response.answer}
                    latencyMs={message.response.meta.latency_ms}
                    question=""
                    sources={message.response.sources}
                    isLoading={isLoading && index === chatHistory.length - 1}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Input Fixo no Bottom - Sempre Visível */}
      <div className="flex-shrink-0 border-t border-umbanda-border bg-umbanda-dark/95 backdrop-blur-sm shadow-2xl">
        <div className="max-w-3xl mx-auto px-4 py-4">
          <ChatBox onSubmit={handleAsk} isLoading={isLoading} value={pendingQuestion} />
        </div>
      </div>
    </div>
  );
}

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ChatPage />} />
        <Route path="/admin" element={<AdminPage />} />
      </Routes>
      <Analytics />
      <SpeedInsights />
    </BrowserRouter>
  );
};
