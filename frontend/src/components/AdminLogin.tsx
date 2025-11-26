import { useState } from 'react';

interface AdminLoginProps {
  onLogin: () => void;
}

export default function AdminLogin({ onLogin }: AdminLoginProps) {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Senha simples por enquanto (pode ser melhorada com hash/backend futuramente)
  const ADMIN_PASSWORD = import.meta.env.VITE_ADMIN_PASSWORD || 'aiye2024';

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    // Simular pequeno delay de autenticação
    setTimeout(() => {
      if (password === ADMIN_PASSWORD) {
        // Salvar no sessionStorage para manter login durante a sessão
        sessionStorage.setItem('admin_authenticated', 'true');
        onLogin();
      } else {
        setError('Senha incorreta');
        setPassword('');
      }
      setIsLoading(false);
    }, 500);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-umbanda-light via-white to-blue-50 flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-lg shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-umbanda-primary mb-2">
              Aiye Admin
            </h1>
            <p className="text-umbanda-secondary text-sm">
              Área administrativa - Acesso restrito
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Senha de Administrador
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-umbanda-primary focus:border-umbanda-primary transition-colors"
                placeholder="Digite a senha"
                required
                disabled={isLoading}
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-umbanda-primary text-white py-3 px-4 rounded-lg hover:bg-opacity-90 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                  Autenticando...
                </span>
              ) : (
                'Entrar'
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-gray-200 text-center">
            <a
              href="/"
              className="text-sm text-umbanda-accent hover:text-umbanda-primary transition-colors"
            >
              ← Voltar para o chat
            </a>
          </div>
        </div>

        {/* Info adicional */}
        <div className="mt-6 text-center text-xs text-gray-500">
          <p>Acesso seguro via sessionStorage</p>
        </div>
      </div>
    </div>
  );
}
