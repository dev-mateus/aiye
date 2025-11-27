/**
 * Componente AnswerCard
 * Exibe a resposta gerada com aviso ético
 */

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import RatingWidget from "./RatingWidget";

interface AnswerCardProps {
  answer: string;
  latencyMs: number;
  question?: string; // Adicionado para o sistema de avaliação
}

export const AnswerCard: React.FC<AnswerCardProps> = ({ answer, latencyMs, question }) => {
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
        <span className="text-xs text-umbanda-accent font-medium">
          {latencyMs.toFixed(0)}ms
        </span>
      </div>

      <div className="answer-text text-umbanda-dark leading-relaxed">
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={{
            strong: ({node, ...props}) => <strong className="font-bold text-umbanda-primary" {...props} />,
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
    </div>
  );
};
