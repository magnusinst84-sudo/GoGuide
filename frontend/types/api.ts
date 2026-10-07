export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface InterestRatings {
  [questionId: string]: number | null;
}

export interface SkillLevels {
  mathematics: number;
  statistics: number;
  programming: number;
  logic: number;
  communication: number;
  design: number;
  biology: number;
  electronics: number;
  [key: string]: number;
}

export interface StudentProfile {
  academic_stream: string;
  marks_percentage: number;
  current_city: string;
  interests: InterestRatings;
  skills: SkillLevels;
  risk_tolerance: number | null;
  target_career?: string | null;
}

export interface Career {
  id: string;
  title: string;
  category: string;
  description?: string;
  match_score?: number;
  growth_rate?: string;
  median_salary?: string;
  required_skills?: string[];
}

export interface RecommendationResponse {
  status: string;
  student_id?: string;
  careers?: Career[];
  pathways?: any[];
  message?: string;
}

export interface ApiResponse<T = any> {
  status: string;
  message?: string;
  data?: T;
}
