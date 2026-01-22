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
    <div className="h-screen flex flex-col bg-gradient-to-br from-umbanda-light via-white to-blue-50">
      {/* Progress Bar */}
      {isLoading && (
        <div className="fixed top-0 left-0 right-0 h-1 bg-umbanda-primary z-50 progress-bar" />
      )}

      {/* Header Fixo */}
      <div className="flex-shrink-0 border-b-2 border-umbanda-secondary bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-umbanda-primary">
            Aiye
          </h1>
          <p className="text-sm text-umbanda-secondary">
            Espaço dedicado ao estudo da Umbanda, do Espiritismo e Afins
          </p>
        </div>
      </div>

      {/* Área de Mensagens com Scroll */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6">
          {/* Status do Backend */}
          {!isBackendOnline && (
            <div className="mb-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg flex items-start gap-3">
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
                  Inicie o servidor: <code className="bg-red-200 px-2 py-1 rounded">
                    uvicorn backend.main:app --reload --port 8000
                  </code>
                </p>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-6 bg-orange-100 border border-orange-400 text-orange-700 px-4 py-3 rounded-lg">
              <p className="font-semibold">⚠️ Erro</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
          )}

          {/* Empty State com perguntas sugeridas */}
          {chatHistory.length === 0 && (
            <div className="py-10 space-y-6">
              <div className="bg-white border-2 border-umbanda-secondary rounded-lg p-6 shadow-lg max-w-2xl mx-auto">
                <ChatBox onSubmit={handleAsk} isLoading={isLoading} value={pendingQuestion} />
              </div>
              
              {/* Perguntas Sugeridas */}
              <div className="max-w-2xl mx-auto">
                <p className="text-sm font-semibold text-umbanda-secondary mb-3 px-2">
                  💡 Sugestões de perguntas:
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {SUGGESTED_QUESTIONS.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => handleAsk(question)}
                      disabled={isLoading}
                      className="text-left p-4 bg-white border-2 border-umbanda-light rounded-lg hover:border-umbanda-primary hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
                    >
                      <span className="text-sm text-umbanda-dark group-hover:text-umbanda-primary font-medium">
                        {question}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Histórico de Conversas */}
          {chatHistory.map((message, index) => (
            <div 
              key={index} 
              className="mb-8"
              ref={index === chatHistory.length - 1 ? lastMessageRef : null}
            >
              <AnswerCard
                answer={message.response.answer}
                latencyMs={message.response.meta.latency_ms}
                question={message.question}
                sources={message.response.sources}
                isLoading={isLoading && index === chatHistory.length - 1}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Input Fixo no Bottom – DEPOIS de existir histórico (mantém durante loading) */}
      {chatHistory.length > 0 && (
        <div className="flex-shrink-0 bg-white shadow-lg">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <ChatBox onSubmit={handleAsk} isLoading={isLoading} value={pendingQuestion} />
          </div>
        </div>
      )}

      {/* Footer Fixo */}
      <div className="flex-shrink-0 bg-white border-t border-umbanda-light">
        <div className="max-w-4xl mx-auto px-4 py-2 text-center text-xs text-umbanda-accent">
          <p>
            Desenvolvido com ❤️ por{" "}
            <a
              href="https://github.com/dev-mateus"
              target="_blank"
              rel="noopener noreferrer"
              className="text-umbanda-primary hover:underline font-semibold"
            >
              Mateus
            </a>
          </p>
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
