import {
  HealthResponse,
  StudentProfile,
  RecommendationResponse,
  ApiResponse,
} from '@/types/api';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers || {}),
    },
    ...options,
  });

  if (!res.ok) {
    const errorText = await res.text().catch(() => '');
    throw new Error(`API error ${res.status}: ${errorText || res.statusText}`);
  }

  return res.json();
}

/** Check health status of backend */
export async function checkHealth(): Promise<HealthResponse> {
  return fetchJson<HealthResponse>(`${API_URL}/api/health`);
}

/** Create or update student profile */
export async function createStudent(profile: StudentProfile): Promise<ApiResponse> {
  return fetchJson<ApiResponse>(`${API_URL}/api/students`, {
    method: 'POST',
    body: JSON.stringify(profile),
  });
}

/** Request recommendations */
export async function getRecommendations(payload?: any): Promise<RecommendationResponse> {
  return fetchJson<RecommendationResponse>(`${API_URL}/api/recommendations`, {
    method: 'POST',
    body: JSON.stringify(payload || {}),
  });
}

/** Get recommendations for a specific student */
export async function getStudentRecommendations(studentId: string): Promise<RecommendationResponse> {
  return fetchJson<RecommendationResponse>(`${API_URL}/api/recommendations/student/${studentId}`);
}

/** List all careers */
export async function listCareers(): Promise<ApiResponse> {
  return fetchJson<ApiResponse>(`${API_URL}/api/careers`);
}

/** Get single career details */
export async function getCareer(careerId: string): Promise<ApiResponse> {
  return fetchJson<ApiResponse>(`${API_URL}/api/careers/${careerId}`);
}

/** Solve financial / EMI constraints */
export async function solveFinancial(payload: any): Promise<ApiResponse> {
  return fetchJson<ApiResponse>(`${API_URL}/api/financial/solver`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/** Resolve parent-student preference conflict */
export async function resolveConflict(payload: any): Promise<ApiResponse> {
  return fetchJson<ApiResponse>(`${API_URL}/api/conflict`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/** Analyze skills gap */
export async function analyzeSkillsGap(payload: any): Promise<ApiResponse> {
  return fetchJson<ApiResponse>(`${API_URL}/api/skills/gap`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/** Get educational / skill pathways for career */
export async function getPathways(careerId: string): Promise<ApiResponse> {
  return fetchJson<ApiResponse>(`${API_URL}/api/pathways/${careerId}`);
}

/** Create action plan */
export async function createActionPlan(payload: any): Promise<ApiResponse> {
  return fetchJson<ApiResponse>(`${API_URL}/api/action-plan`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/** Chat with LLM guidance agent */
export async function chatWithLLM(message: string, context?: any): Promise<ApiResponse> {
  return fetchJson<ApiResponse>(`${API_URL}/api/llm/chat`, {
    method: 'POST',
    body: JSON.stringify({ message, context }),
  });
}
