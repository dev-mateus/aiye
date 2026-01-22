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
            className="w-full px-4 py-3 border border-umbanda-clay/20 rounded-xl 
                     focus:outline-none focus:ring-2 focus:ring-umbanda-gold focus:border-transparent 
                     disabled:bg-umbanda-sand/50 disabled:cursor-not-allowed
                     resize-none overflow-y-auto
                     placeholder:text-umbanda-text/40
                     bg-white/80 backdrop-blur-sm"
            rows={1}
            style={{
              minHeight: '48px',
              maxHeight: '120px'
            }}
          />
        </div>
        
        <button
          type="submit"
          disabled={!isValid || isLoading}
          className="px-5 py-3 bg-gradient-to-r from-umbanda-gold to-umbanda-amber
                   text-white font-semibold rounded-xl
                   hover:shadow-md hover:scale-105
                   disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100
                   transition-all duration-200
                   flex items-center gap-2 h-12"
        >
          {isLoading ? (
            <span className="animate-spin">⏳</span>
          ) : (
            <span>✨</span>
          )}
          <span className="hidden sm:inline">Enviar</span>
        </button>
      </div>
    </form>
  );
};
