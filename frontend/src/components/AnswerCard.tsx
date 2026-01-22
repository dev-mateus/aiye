/**
 * Componente AnswerCard
 * Exibe a resposta gerada com aviso ético
 */

import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import RatingWidget from "./RatingWidget";
import { Source } from "../api";

interface AnswerCardProps {
  answer: string;
  latencyMs: number;
  question?: string;
  sources?: Source[];
  isLoading?: boolean;
}

export const AnswerCard: React.FC<AnswerCardProps> = ({ answer, latencyMs, question, sources, isLoading }) => {
  const [isSourcesExpanded, setIsSourcesExpanded] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(answer);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Erro ao copiar:', err);
    }
  };
  
  // Skeleton loading durante carregamento
  if (isLoading) {
    return (
      <div className="animate-fade-in bg-white border-2 border-umbanda-secondary rounded-lg p-6 shadow-lg">
        {question && (
          <div className="mb-4 pb-4 border-b-2 border-umbanda-light">
            <p className="text-lg font-bold text-umbanda-dark">{question}</p>
          </div>
        )}
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-umbanda-primary">Resposta</h2>
        </div>
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-full"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          <div className="h-4 bg-gray-200 rounded w-4/6"></div>
          <div className="h-4 bg-gray-200 rounded w-full"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in bg-white border-2 border-umbanda-secondary rounded-lg p-6 shadow-lg hover:shadow-xl transition-shadow">
      {/* Pergunta em negrito no topo */}
      {question && (
        <div className="mb-4 pb-4 border-b-2 border-umbanda-light md:border-none md:pb-0 md:mb-2">
          <p className="text-lg font-bold text-umbanda-dark">
            {question}
          </p>
        </div>
      )}

      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-umbanda-primary">Resposta</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="text-xs px-3 py-1 rounded-md border border-umbanda-secondary hover:bg-umbanda-light transition-colors flex items-center gap-1"
            title="Copiar resposta"
          >
            {copySuccess ? (
              <>
                <span>✓</span>
                <span>Copiado!</span>
              </>
            ) : (
              <>
                <span>📋</span>
                <span>Copiar</span>
              </>
            )}
          </button>
          <span className="text-xs text-umbanda-accent font-medium">
            {latencyMs.toFixed(0)}ms
          </span>
        </div>
      </div>

      <div className="answer-text text-umbanda-dark leading-relaxed">
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={{
            strong: ({node, ...props}) => <strong className="font-bold text-umbanda-dark" {...props} />,
            em: ({node, ...props}) => <em className="italic" {...props} />,
            ul: ({node, ...props}) => <ul className="list-disc ml-6 my-2 space-y-1" {...props} />,
            ol: ({node, ...props}) => <ol className="list-decimal ml-6 my-2 space-y-1" {...props} />,
            li: ({node, ...props}) => <li className="ml-1" {...props} />,
            p: ({node, ...props}) => <p className="my-2" {...props} />,
            h1: ({node, ...props}) => <h1 className="text-2xl font-bold my-3" {...props} />,
            h2: ({node, ...props}) => <h2 className="text-xl font-bold my-2" {...props} />,
            h3: ({node, ...props}) => <h3 className="text-lg font-bold my-2" {...props} />,
          }}
        >
          {answer}
        </ReactMarkdown>
      </div>

      {/* Sistema de avaliação */}
      {question && (
        <RatingWidget question={question} answer={answer} />
      )}

      {/* Documentos Consultados */}
      {sources && sources.length > 0 && (
        <div className="mt-6 pt-6 border-t-2 border-umbanda-light">
          <button
            onClick={() => setIsSourcesExpanded(!isSourcesExpanded)}
            className="w-full flex items-center justify-between hover:bg-umbanda-light transition-colors rounded p-2 -mx-2"
          >
            <div className="flex items-center gap-2">
              <span className="text-base font-semibold text-umbanda-primary">
                📚 Documentos Consultados
              </span>
              <span className="text-sm text-umbanda-accent font-medium">
                ({sources.length})
              </span>
            </div>
            <svg
              className={`w-5 h-5 text-umbanda-primary transition-transform duration-200 ${
                isSourcesExpanded ? "rotate-180" : ""
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>

          {isSourcesExpanded && (
            <div className="space-y-3 mt-4">
              {sources.map((source, index) => (
                <div
                  key={index}
                  className="border-l-4 border-umbanda-primary bg-umbanda-light p-4 rounded hover:bg-opacity-75 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <span className="font-semibold text-umbanda-primary break-words">
                        {source.title}
                      </span>
                      <p className="text-sm text-umbanda-secondary mt-1">
                        {source.page_end === source.page_start 
                          ? `Página ${source.page_start}`
                          : `Páginas ${source.page_start}–${source.page_end}`
                        }
                      </p>
                      {source.score !== undefined && (
                        <p className="text-xs text-umbanda-accent mt-2 font-medium">
                          Relevância: {(source.score * 100).toFixed(0)}%
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
