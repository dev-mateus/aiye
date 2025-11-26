import { useState } from 'react';

interface RatingWidgetProps {
  question: string;
  answer: string;
  onSubmit?: () => void;
}

export default function RatingWidget({ question, answer, onSubmit }: RatingWidgetProps) {
  const [rating, setRating] = useState<number>(0);
  const [hover, setHover] = useState<number>(0);
  const [comment, setComment] = useState<string>('');
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);

  const handleSubmit = async () => {
    if (rating === 0) {
      alert('Por favor, selecione uma avaliação de 1 a 5 estrelas');
      return;
    }

    setSubmitting(true);
    try {
      const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
      const response = await fetch(`${API_BASE}/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question,
          answer,
          rating,
          comment: comment.trim() || null,
        }),
      });

      if (response.ok) {
        setSubmitted(true);
        if (onSubmit) onSubmit();
      } else {
        throw new Error('Erro ao enviar feedback');
      }
    } catch (error) {
      console.error('Erro ao enviar feedback:', error);
      alert('Erro ao enviar feedback. Tente novamente.');
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
        <p className="text-sm text-green-700">
          ✓ Obrigado pela sua avaliação! Seu feedback nos ajuda a melhorar.
        </p>
      </div>
    );
  }

  return (
    <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg">
      <p className="text-sm font-medium text-gray-700 mb-2">
        Esta resposta foi útil?
      </p>
      
      {/* Estrelas */}
      <div className="flex gap-1 mb-3">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => setRating(star)}
            onMouseEnter={() => setHover(star)}
            onMouseLeave={() => setHover(0)}
            disabled={submitting}
            className="text-2xl transition-transform hover:scale-110 focus:outline-none disabled:opacity-50"
            aria-label={`${star} estrela${star > 1 ? 's' : ''}`}
          >
            <span
              className={
                star <= (hover || rating)
                  ? 'text-yellow-400'
                  : 'text-gray-300'
              }
            >
              ★
            </span>
          </button>
        ))}
        {rating > 0 && (
          <span className="ml-2 text-sm text-gray-600 self-center">
            {rating} de 5
          </span>
        )}
      </div>

      {/* Comentário opcional */}
      {rating > 0 && (
        <>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Comentário opcional (máx. 500 caracteres)"
            maxLength={500}
            disabled={submitting}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            rows={2}
          />
          <div className="flex justify-between items-center mt-2">
            <span className="text-xs text-gray-500">
              {comment.length}/500 caracteres
            </span>
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {submitting ? 'Enviando...' : 'Enviar Avaliação'}
            </button>
          </div>
        </>
      )}
    </div>
  );
}
