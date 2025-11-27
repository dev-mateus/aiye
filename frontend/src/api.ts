/**
 * Cliente HTTP para comunicação com o backend
 */

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export interface Source {
  title: string;
  page_start: number;
  page_end: number;
  uri: string;
  score?: number;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
  meta: {
    latency_ms: number;
    top_k: number;
    min_sim: number;
    num_contexts: number;
  };
}

export interface ConversationMessage {
  question: string;
  answer: string;
}

/**
 * Faz uma pergunta ao backend e retorna a resposta com fontes
 */
export async function ask(question: string, history?: ConversationMessage[]): Promise<AskResponse> {
  try {
    const response = await fetch(`${API_BASE}/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question, history }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Erro ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Erro ao comunicar com o backend:", error);
    throw error;
  }
}

/**
 * Verifica se o backend está disponível
 */
export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/healthz`);
    return response.ok;
  } catch {
    return false;
  }
}
