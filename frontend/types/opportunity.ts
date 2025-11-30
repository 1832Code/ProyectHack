// Opportunity API Types

export interface FetchOpportunityParams {
  query: string;
  idCompany?: number;
  limit?: number;
}

export interface OpportunityRequest {
  query: string;
  id_company: number;
  limit: number;
}

export interface OpportunityPost {
  id: number;
  id_company: number;
  title: string;
  description: string;
  insight1: number | null;
  insight2: number | null;
  insight3: number | null;
  sentiment: number | null;
  created_at: string;
  updated_at: string;
  image: string | null;
  video: string;
  query: string;
  source: string | null;
}

export interface OpportunityResult {
  insight: string;
  ideas: string[];
  posts: OpportunityPost[];
}

export interface OpportunityResponse {
  query: string;
  results: OpportunityResult[];
}

