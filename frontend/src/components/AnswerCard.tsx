/**
 * Componente AnswerCard
 * Exibe a resposta gerada com aviso ético
 */

import React from "react";

interface AnswerCardProps {
  answer: string;
  latencyMs: number;
}

export const AnswerCard: React.FC<AnswerCardProps> = ({ answer, latencyMs }) => {
  return (
    <div className="animate-fade-in bg-white border-2 border-umbanda-secondary rounded-lg p-6 shadow-lg hover:shadow-xl transition-shadow">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-umbanda-primary">Resposta</h2>
        <span className="text-xs text-umbanda-accent font-medium">
          {latencyMs.toFixed(0)}ms
        </span>
      </div>

      <div className="answer-text mb-6 text-umbanda-dark whitespace-pre-wrap leading-relaxed">
        {answer}
      </div>

      <div className="border-t-2 border-umbanda-light pt-4">
        <div className="flex gap-2">
          <div className="flex-shrink-0">
            <svg
              className="h-5 w-5 text-umbanda-primary"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="text-sm text-umbanda-primary">
            <p className="font-semibold">Nota Importante</p>
            <p className="mt-1 text-umbanda-dark">
              As tradições da Umbanda variam entre terreiros. Esta resposta é
              baseada no acervo disponível e não substitui a orientação de um
              dirigente. Sempre consulte seu mãe ou pai de santo para questões
              específicas sobre sua prática.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
