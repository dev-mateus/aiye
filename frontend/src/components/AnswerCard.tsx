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
      <div className="animate-fade-in bg-umbanda-card backdrop-blur-sm rounded-2xl p-5 shadow-md border border-umbanda-border">
        <div className="animate-pulse space-y-3">
          <div className="h-3 bg-umbanda-border rounded w-full"></div>
          <div className="h-3 bg-umbanda-border rounded w-11/12"></div>
          <div className="h-3 bg-umbanda-border rounded w-4/5"></div>
          <div className="h-3 bg-umbanda-border rounded w-full"></div>
          <div className="h-3 bg-umbanda-border rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <div className="bg-umbanda-dark backdrop-blur-sm rounded-2xl p-5 shadow-md border border-umbanda-primary/30 hover:shadow-lg hover:border-umbanda-primary/50 transition-all">
        <div className="mb-3 flex items-center justify-between">
          <span className="text-xs text-umbanda-text-muted font-medium">
            {latencyMs.toFixed(0)}ms
          </span>
          <button
            onClick={handleCopy}
            className="text-xs px-3 py-1 rounded-lg border border-umbanda-border hover:bg-umbanda-dark hover:border-umbanda-primary transition-colors flex items-center gap-1.5 text-umbanda-text"
            title="Copiar resposta"
          >
            {copySuccess ? (
              <>
                <span className="text-umbanda-forest">✓</span>
                <span className="text-umbanda-forest">Copiado</span>
              </>
            ) : (
              <>
                <span>📋</span>
                <span>Copiar</span>
              </>
            )}
          </button>
        </div>

        <div className="answer-text text-white/95 leading-relaxed">
          {/* Detecta erro de quota e mostra aviso especial */}
          {answer.includes('Limite de requisições atingido') || answer.toLowerCase().includes('quota') ? (
            <div className="bg-yellow-900/20 border border-yellow-700/50 rounded-xl p-4">
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]}
                components={{
                  strong: ({node, ...props}) => <strong className="font-bold text-yellow-400" {...props} />,
                  p: ({node, ...props}) => <p className="my-2 text-yellow-300" {...props} />,
                }}
              >
                {answer}
              </ReactMarkdown>
            </div>
          ) : (
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              strong: ({node, ...props}) => <strong className="font-bold text-umbanda-accent" {...props} />,
              em: ({node, ...props}) => <em className="italic text-umbanda-text-muted" {...props} />,
              ul: ({node, ...props}) => <ul className="list-disc ml-6 my-2 space-y-1" {...props} />,
              ol: ({node, ...props}) => <ol className="list-decimal ml-6 my-2 space-y-1" {...props} />,
              li: ({node, ...props}) => <li className="ml-1" {...props} />,
              p: ({node, ...props}) => <p className="my-2" {...props} />,
              h1: ({node, ...props}) => <h1 className="text-2xl font-bold my-3 text-umbanda-accent" {...props} />,
              h2: ({node, ...props}) => <h2 className="text-xl font-bold my-2 text-umbanda-accent" {...props} />,
              h3: ({node, ...props}) => <h3 className="text-lg font-bold my-2 text-umbanda-accent" {...props} />,
            }}
          >
            {answer}
          </ReactMarkdown>
            )}
        </div>

        {/* Sistema de avaliação */}
        {question && (
          <RatingWidget question={question} answer={answer} />
        )}

        {/* Documentos Consultados */}
        {sources && sources.length > 0 && (
          <div className="mt-5 pt-5 border-t border-umbanda-border">
            <button
              onClick={() => setIsSourcesExpanded(!isSourcesExpanded)}
              className="w-full flex items-center justify-between hover:bg-umbanda-dark transition-colors rounded-lg p-2 -mx-2"
            >
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-umbanda-accent">
                  📚 Fontes Consultadas
                </span>
                <span className="text-xs px-2 py-0.5 bg-umbanda-primary/20 text-umbanda-accent rounded-full font-medium">
                  {sources.length}
                </span>
              </div>
              <svg
                className={`w-4 h-4 text-umbanda-forest transition-transform duration-200 ${
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
              <div className="space-y-2 mt-3">
                {sources.map((source, index) => (
                  <div
                    key={index}
                    className="border-l-2 border-umbanda-gold bg-umbanda-dark/50 p-3 rounded-r-lg hover:bg-umbanda-dark transition-colors"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <span className="text-sm font-semibold text-umbanda-accent break-words">
                          {source.title}
                        </span>
                        <p className="text-xs text-umbanda-text-muted mt-1">
                          {source.page_end === source.page_start 
                            ? `Página ${source.page_start}`
                            : `Páginas ${source.page_start}–${source.page_end}`
                          }
                        </p>
                        {source.score !== undefined && (
                          <p className="text-xs text-umbanda-accent mt-1 font-medium">
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
    </div>
  );
};
