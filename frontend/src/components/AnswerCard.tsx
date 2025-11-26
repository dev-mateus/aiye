/**
 * Componente AnswerCard
 * Exibe a resposta gerada com aviso ético
 */

import React from "react";
import RatingWidget from "./RatingWidget";

interface AnswerCardProps {
  answer: string;
  latencyMs: number;
  question?: string; // Adicionado para o sistema de avaliação
}

export const AnswerCard: React.FC<AnswerCardProps> = ({ answer, latencyMs, question }) => {
  return (
    <div className="animate-fade-in bg-white border-2 border-umbanda-secondary rounded-lg p-6 shadow-lg hover:shadow-xl transition-shadow">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-umbanda-primary">Resposta</h2>
        <span className="text-xs text-umbanda-accent font-medium">
          {latencyMs.toFixed(0)}ms
        </span>
      </div>

      <div className="answer-text text-umbanda-dark whitespace-pre-wrap leading-relaxed">
        {answer}
      </div>

      {/* Sistema de avaliação */}
      {question && (
        <RatingWidget question={question} answer={answer} />
      )}
    </div>
  );
};
