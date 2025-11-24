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
      <h2 className="text-lg font-semibold text-umbanda-primary mb-4">📚 Documentos Consultados</h2>

      <div className="space-y-3">
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

      <p className="text-xs text-umbanda-accent mt-4 pt-4 border-t-2 border-umbanda-light font-medium">
        {sources.length} fonte{sources.length !== 1 ? "s" : ""} citada
        {sources.length !== 1 ? "s" : ""}
      </p>
    </div>
  );
};
