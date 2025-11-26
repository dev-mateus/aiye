import { useState, useEffect } from 'react';

interface Feedback {
  id: number;
  timestamp: string;
  question: string;
  answer: string;
  rating: number;
  comment: string | null;
  created_at: string;
}

interface FilteredResult {
  total: number;
  feedbacks: Feedback[];
  pagination: {
    limit: number;
    offset: number;
    has_more: boolean;
  };
}

interface Stats {
  period: string;
  stats: {
    total: number;
    avg_rating: number;
    rating_5: number;
    rating_4: number;
    rating_3: number;
    rating_2: number;
    rating_1: number;
    with_comments: number;
  };
  recent_feedbacks: Array<{
    id: number;
    timestamp: string;
    question: string;
    rating: number;
    comment: string | null;
  }>;
}

export default function AdminDashboard() {
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Filtros
  const [rating, setRating] = useState<string>('');
  const [search, setSearch] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [period, setPeriod] = useState('7d');
  const [orderBy, setOrderBy] = useState('timestamp');
  const [orderDir, setOrderDir] = useState('DESC');
  
  // Paginação
  const [currentPage, setCurrentPage] = useState(1);
  const [totalResults, setTotalResults] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const resultsPerPage = 20;

  const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

  // Carregar estatísticas
  const loadStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/admin/feedbacks/stats?period=${period}`);
      if (!response.ok) throw new Error('Erro ao carregar estatísticas');
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Erro ao carregar stats:', err);
    }
  };

  // Carregar feedbacks com filtros
  const loadFeedbacks = async (page: number = 1) => {
    setLoading(true);
    setError(null);
    
    try {
      const offset = (page - 1) * resultsPerPage;
      const params = new URLSearchParams({
        limit: resultsPerPage.toString(),
        offset: offset.toString(),
        order_by: orderBy,
        order_dir: orderDir,
      });
      
      if (rating) params.append('rating', rating);
      if (search) params.append('search', search);
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
      const response = await fetch(`${API_BASE}/admin/feedbacks?${params}`);
      if (!response.ok) throw new Error('Erro ao carregar feedbacks');
      
      const data: FilteredResult = await response.json();
      setFeedbacks(data.feedbacks);
      setTotalResults(data.total);
      setHasMore(data.pagination.has_more);
      setCurrentPage(page);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  };

  // Carregar dados iniciais
  useEffect(() => {
    loadStats();
    loadFeedbacks();
  }, [period, orderBy, orderDir]);

  // Aplicar filtros
  const handleFilter = () => {
    setCurrentPage(1);
    loadFeedbacks(1);
  };

  // Limpar filtros
  const handleClearFilters = () => {
    setRating('');
    setSearch('');
    setStartDate('');
    setEndDate('');
    setCurrentPage(1);
    loadFeedbacks(1);
  };

  // Renderizar estrelas
  const renderStars = (rating: number) => {
    return (
      <div className="flex gap-0.5">
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            className={star <= rating ? 'text-yellow-400' : 'text-gray-300'}
          >
            ★
          </span>
        ))}
      </div>
    );
  };

  // Formatar data
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const totalPages = Math.ceil(totalResults / resultsPerPage);

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Dashboard de Feedbacks
          </h1>
          <p className="text-gray-600">
            Análise detalhada das avaliações dos usuários
          </p>
        </div>

        {/* Estatísticas */}
        {stats && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Estatísticas</h2>
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="7d">Últimos 7 dias</option>
                <option value="30d">Últimos 30 dias</option>
                <option value="90d">Últimos 90 dias</option>
                <option value="all">Todo período</option>
              </select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="text-sm text-gray-600 mb-1">Total de Feedbacks</div>
                <div className="text-3xl font-bold text-gray-900">
                  {stats.stats.total}
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="text-sm text-gray-600 mb-1">Média de Rating</div>
                <div className="flex items-center gap-2">
                  <div className="text-3xl font-bold text-gray-900">
                    {stats.stats.avg_rating?.toFixed(1) || '0.0'}
                  </div>
                  <span className="text-yellow-400 text-2xl">★</span>
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="text-sm text-gray-600 mb-1">Com Comentários</div>
                <div className="text-3xl font-bold text-gray-900">
                  {stats.stats.with_comments}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {stats.stats.total > 0
                    ? `${Math.round((stats.stats.with_comments / stats.stats.total) * 100)}%`
                    : '0%'}
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <div className="text-sm text-gray-600 mb-1">Distribuição</div>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span>5★:</span>
                    <span className="font-semibold">{stats.stats.rating_5}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>4★:</span>
                    <span className="font-semibold">{stats.stats.rating_4}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>3★:</span>
                    <span className="font-semibold">{stats.stats.rating_3}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>2★:</span>
                    <span className="font-semibold">{stats.stats.rating_2}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>1★:</span>
                    <span className="font-semibold">{stats.stats.rating_1}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Filtros */}
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Filtros</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Rating
              </label>
              <select
                value={rating}
                onChange={(e) => setRating(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Todos</option>
                <option value="5">5 estrelas</option>
                <option value="4">4 estrelas</option>
                <option value="3">3 estrelas</option>
                <option value="2">2 estrelas</option>
                <option value="1">1 estrela</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Buscar texto
              </label>
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Buscar em perguntas/comentários"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Data inicial
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Data final
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Ordenar por
              </label>
              <select
                value={orderBy}
                onChange={(e) => setOrderBy(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="timestamp">Data</option>
                <option value="rating">Rating</option>
                <option value="id">ID</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Direção
              </label>
              <select
                value={orderDir}
                onChange={(e) => setOrderDir(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="DESC">Decrescente</option>
                <option value="ASC">Crescente</option>
              </select>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleFilter}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Aplicar Filtros
            </button>
            <button
              onClick={handleClearFilters}
              className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
            >
              Limpar
            </button>
          </div>
        </div>

        {/* Lista de Feedbacks */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">
                Feedbacks ({totalResults})
              </h2>
              <div className="text-sm text-gray-600">
                Página {currentPage} de {totalPages || 1}
              </div>
            </div>
          </div>

          {loading && (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-600">Carregando feedbacks...</p>
            </div>
          )}

          {error && (
            <div className="p-6 text-center text-red-600">
              Erro: {error}
            </div>
          )}

          {!loading && !error && feedbacks.length === 0 && (
            <div className="p-12 text-center text-gray-500">
              Nenhum feedback encontrado com os filtros aplicados.
            </div>
          )}

          {!loading && !error && feedbacks.length > 0 && (
            <>
              <div className="divide-y divide-gray-200">
                {feedbacks.map((feedback) => (
                  <div key={feedback.id} className="p-6 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-medium text-gray-500">
                          #{feedback.id}
                        </span>
                        {renderStars(feedback.rating)}
                      </div>
                      <div className="text-sm text-gray-500">
                        {formatDate(feedback.timestamp)}
                      </div>
                    </div>

                    <div className="mb-3">
                      <div className="text-sm font-medium text-gray-700 mb-1">
                        Pergunta:
                      </div>
                      <div className="text-sm text-gray-900">
                        {feedback.question}
                      </div>
                    </div>

                    <div className="mb-3">
                      <div className="text-sm font-medium text-gray-700 mb-1">
                        Resposta:
                      </div>
                      <div className="text-sm text-gray-600 line-clamp-3">
                        {feedback.answer}
                      </div>
                    </div>

                    {feedback.comment && (
                      <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                        <div className="text-sm font-medium text-blue-900 mb-1">
                          Comentário:
                        </div>
                        <div className="text-sm text-blue-800">
                          {feedback.comment}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Paginação */}
              <div className="p-6 border-t border-gray-200 flex items-center justify-between">
                <button
                  onClick={() => loadFeedbacks(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  ← Anterior
                </button>

                <div className="text-sm text-gray-600">
                  Mostrando {((currentPage - 1) * resultsPerPage) + 1} - {Math.min(currentPage * resultsPerPage, totalResults)} de {totalResults}
                </div>

                <button
                  onClick={() => loadFeedbacks(currentPage + 1)}
                  disabled={!hasMore}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Próxima →
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
