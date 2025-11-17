/**
 * Componente ChatBox
 * Textarea para entrada de perguntas e botão de envio
 */

import React, { useState } from "react";

interface ChatBoxProps {
  onSubmit: (question: string) => void;
  isLoading: boolean;
}

export const ChatBox: React.FC<ChatBoxProps> = ({ onSubmit, isLoading }) => {
  const [question, setQuestion] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = question.trim();
    if (trimmed.length >= 3) {
      onSubmit(trimmed);
      // Não limpa a pergunta - mantém no input
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Ctrl+Enter or Cmd+Enter para enviar
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      handleSubmit(e as any);
    }
  };

  const isValid = question.trim().length >= 3;

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex flex-col gap-3">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Faça sua pergunta sobre Umbanda... (mínimo 3 caracteres)"
          disabled={isLoading}
          rows={4}
          className="w-full px-4 py-3 border-2 border-umbanda-secondary rounded-lg focus:outline-none focus:ring-2 focus:ring-umbanda-primary focus:border-umbanda-primary disabled:bg-umbanda-light disabled:cursor-not-allowed resize-none text-umbanda-dark placeholder-umbanda-accent"
        />

        <div className="flex items-center justify-between">
          <div className="text-sm text-umbanda-accent">
            {question.length} caracteres
            {question.length >= 3 && (
              <span className="ml-2 text-umbanda-primary font-semibold">✓ Pronto para enviar</span>
            )}
          </div>

          <button
            type="submit"
            disabled={!isValid || isLoading}
            className={`px-6 py-2 rounded-lg font-medium transition-all ${
              isValid && !isLoading
                ? "bg-umbanda-primary text-white hover:bg-umbanda-accent active:scale-95 cursor-pointer shadow-md hover:shadow-lg"
                : "bg-umbanda-light text-umbanda-accent cursor-not-allowed"
            }`}
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-umbanda-primary border-t-transparent"></span>
                Buscando...
              </span>
            ) : (
              "Perguntar"
            )}
          </button>
        </div>
      </div>
    </form>
  );
};
