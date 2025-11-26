/**
 * Componente principal da aplicação
 */

import React, { useState, useEffect } from "react";
import { Analytics } from "@vercel/analytics/react";
import { ChatBox } from "./components/ChatBox";
import { AnswerCard } from "./components/AnswerCard";
import { SourceList } from "./components/SourceList";
import { ask, healthCheck, AskResponse } from "./api";
import "./styles.css";

export const App: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<AskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isBackendOnline, setIsBackendOnline] = useState(true);

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

  const handleAsk = async (question: string) => {
    if (!isBackendOnline) {
      setError("Backend não está disponível");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await ask(question);
      setResponse(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Erro ao comunicar com o servidor"
      );
      setResponse(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-umbanda-light via-white to-blue-50 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-umbanda-primary mb-2">
            Aiye
          </h1>
          <p className="text-umbanda-secondary">
            Espaço dedicado ao estudo da Umbanda, do Espiritismo e Afins
          </p>
        </div>

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

        {/* Chat Box */}
        <div className="mb-8 bg-white border-2 border-umbanda-secondary rounded-lg p-6 shadow-lg hover:shadow-xl transition-shadow">
          <ChatBox onSubmit={handleAsk} isLoading={isLoading} />
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-orange-100 border border-orange-400 text-orange-700 px-4 py-3 rounded-lg">
            <p className="font-semibold">⚠️ Erro</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        )}

        {/* Response */}
        {response && (
          <div className="space-y-6">
            <AnswerCard
              answer={response.answer}
              latencyMs={response.meta.latency_ms}
            />
            {response.sources.length > 0 && (
              <SourceList sources={response.sources} />
            )}
          </div>
        )}

        {/* Empty State */}
        {!response && !error && !isLoading && (
          <div className="text-center py-12">
            <p className="text-umbanda-secondary text-lg">
              Comece fazendo uma pergunta sobre Umbanda
            </p>
            <p className="text-umbanda-accent text-sm mt-2">
              Use Ctrl+Enter (Cmd+Enter no Mac) para enviar rapidamente
            </p>
          </div>
        )}

        {/* Footer */}
        <div className="mt-12 pt-8 border-t-2 border-umbanda-secondary text-center text-xs text-umbanda-accent">
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
      <Analytics />
    </div>
  );
};
