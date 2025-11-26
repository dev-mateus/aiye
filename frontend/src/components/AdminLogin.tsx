import { useState } from 'react';

interface AdminLoginProps {
  onLogin: () => void;
}

export default function AdminLogin({ onLogin }: AdminLoginProps) {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Senha simples por enquanto (pode ser melhorada com hash/backend futuramente)
  const ADMIN_PASSWORD = import.meta.env.VITE_ADMIN_PASSWORD || 'Aiye@2024#';

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
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pr-12 px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-umbanda-primary focus:border-umbanda-primary transition-colors"
                  placeholder="Digite a senha"
                  required
                  disabled={isLoading}
                />
                <button
                  type="button"
                  aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-2 my-auto p-2 text-gray-500 hover:text-umbanda-primary focus:outline-none focus:ring-2 focus:ring-umbanda-primary rounded"
                  disabled={isLoading}
                >
                  {showPassword ? (
                    // Eye-off icon
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                      <path d="M3.53 2.47a.75.75 0 0 0-1.06 1.06l18 18a.75.75 0 1 0 1.06-1.06l-3.008-3.008a12.23 12.23 0 0 0 3.168-3.398.75.75 0 0 0 0-.692C19.924 8.02 16.223 5.25 12 5.25a8.72 8.72 0 0 0-3.71.82L3.53 2.47ZM7.06 6l1.77 1.77A6.737 6.737 0 0 1 12 7.5c3.5 0 6.674 2.239 8.51 5.25a10.73 10.73 0 0 1-2.663 3.105l-2.015-2.015A4.5 4.5 0 0 0 9.66 9.41L7.06 6Zm7.784 7.784l-1.542-1.542a1.5 1.5 0 1 1-1.542-1.542l-1.542-1.542A4.5 4.5 0 0 0 14.844 13.784Zm-4.27 4.27l-1.88-1.88A6.74 6.74 0 0 1 12 16.5c3.5 0 6.674-2.239 8.51-5.25a10.73 10.73 0 0 0-1.613-2.028l1.124-1.124a12.23 12.23 0 0 1 2.056 2.9.75.75 0 0 1 0 .692C19.924 15.98 16.223 18.75 12 18.75a8.72 8.72 0 0 1-4.426-1.196Z" />
                    </svg>
                  ) : (
                    // Eye icon
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                      <path d="M12 5.25c-4.223 0-7.924 2.77-10.006 6.457a.75.75 0 0 0 0 .586C4.076 16.98 7.777 19.75 12 19.75s7.924-2.77 10.006-6.457a.75.75 0 0 0 0-.586C19.924 8.02 16.223 5.25 12 5.25Zm0 11.25a4.5 4.5 0 1 1 0-9 4.5 4.5 0 0 1 0 9Zm0-1.5a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z" />
                    </svg>
                  )}
                </button>
              </div>
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
