/**
 * Componente SourceList
 * Lista as fontes citadas na resposta
 */

import React from "react";
import { Source } from "../api";

interface SourceListProps {
  sources: Source[];
}

export const SourceList: React.FC<SourceListProps> = ({ sources }) => {
  if (sources.length === 0) {
    return null;
  }

  return (
    <div className="animate-fade-in bg-white border-2 border-umbanda-secondary rounded-lg p-6 shadow-lg hover:shadow-xl transition-shadow">
      <h2 className="text-lg font-semibold text-umbanda-primary mb-4">📚 Fontes</h2>

      <div className="space-y-3">
        {sources.map((source, index) => (
          <div
            key={index}
            className="border-l-4 border-umbanda-primary bg-umbanda-light p-4 rounded hover:bg-opacity-75 transition-colors"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <a
                  href={source.uri}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-semibold text-umbanda-primary hover:underline break-words"
                >
                  {source.title}
                </a>
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
              <a
                href={source.uri}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-shrink-0 text-umbanda-primary hover:text-umbanda-accent transition-colors"
                title="Abrir PDF"
              >
                <svg
                  className="w-5 h-5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM15.657 14.243a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM11 17a1 1 0 102 0v-1a1 1 0 10-2 0v1zM5.757 15.657a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM2 10a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.757 4.343a1 1 0 00-1.414 1.414l.707.707a1 1 0 001.414-1.414l-.707-.707z" />
                </svg>
              </a>
            </div>
          </div>
        ))}
      </div>

      <p className="text-xs text-umbanda-accent mt-4 pt-4 border-t-2 border-umbanda-light font-medium">
        {sources.length} fonte{sources.length !== 1 ? "s" : ""} citada
        {sources.length !== 1 ? "s" : ""}
      </p>
    </div>
  );
};
