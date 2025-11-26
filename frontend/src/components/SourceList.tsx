/**
 * Componente SourceList
 * Lista as fontes citadas na resposta - Colapsável por padrão
 */

import React, { useState } from "react";
import { Source } from "../api";

interface SourceListProps {
  sources: Source[];
}

export const SourceList: React.FC<SourceListProps> = ({ sources }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (sources.length === 0) {
    return null;
  }

  return (
    <div className="animate-fade-in bg-white border-2 border-umbanda-secondary rounded-lg shadow-lg hover:shadow-xl transition-shadow">
      {/* Header Clicável */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-umbanda-light transition-colors rounded-t-lg"
      >
        <div className="flex items-center gap-2">
          <span className="text-lg font-semibold text-umbanda-primary">
            📚 Documentos Consultados
          </span>
          <span className="text-sm text-umbanda-accent font-medium">
            ({sources.length})
          </span>
        </div>
        <svg
          className={`w-5 h-5 text-umbanda-primary transition-transform duration-200 ${
            isExpanded ? "rotate-180" : ""
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

      {/* Conteúdo Expansível */}
      {isExpanded && (
        <div className="px-6 pb-6 pt-2 border-t-2 border-umbanda-light">
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
                      Páginas {source.page_start}
                      {source.page_end !== source.page_start && `–${source.page_end}`}
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
        </div>
      )}
    </div>
  );
};
