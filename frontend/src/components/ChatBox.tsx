/**
 * Componente ChatBox
 * Textarea para entrada de perguntas e botão de envio
 */

import React, { useState, useEffect } from "react";

interface ChatBoxProps {
  onSubmit: (question: string) => void;
  isLoading: boolean;
  value?: string; // Valor controlado externamente
}

export const ChatBox: React.FC<ChatBoxProps> = ({ onSubmit, isLoading, value = "" }) => {
  const [question, setQuestion] = useState(value);

  // Sincroniza com o valor externo (quando pai limpa, limpa aqui também)
  useEffect(() => {
    setQuestion(value);
  }, [value]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = question.trim();
    if (trimmed.length >= 3) {
      onSubmit(trimmed);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter para enviar (sem Shift)
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  const isValid = question.trim().length >= 3;
  const isDisabled = !isValid || isLoading;

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex gap-2 items-end">
        <div className="flex-1 relative">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Pergunte sobre Umbanda..."
            disabled={isLoading}
            className="w-full px-4 py-3 border border-umbanda-border rounded-xl 
                     focus:outline-none focus:ring-2 focus:ring-umbanda-primary focus:border-transparent 
                     disabled:bg-umbanda-darker disabled:cursor-not-allowed
                     resize-none overflow-y-auto
                     placeholder:text-umbanda-text-muted
                     bg-umbanda-card text-umbanda-text backdrop-blur-sm"
            rows={1}
            style={{
              minHeight: '48px',
              maxHeight: '120px'
            }}
          />
        </div>
        
        <button
          type="submit"
          disabled={isDisabled}
          className={`${isDisabled
            ? "bg-umbanda-border text-umbanda-text cursor-not-allowed"
            : "bg-umbanda-primary text-white hover:bg-umbanda-forest hover:shadow-lg hover:-translate-y-px"}
            px-5 py-3 font-semibold rounded-xl transition-all duration-200 flex items-center justify-center gap-2 h-12 focus:outline-none focus:ring-2 focus:ring-umbanda-primary focus:ring-offset-0`}
        >
          {isLoading ? "Enviando" : "Enviar"}
        </button>
      </div>
    </form>
  );
};
