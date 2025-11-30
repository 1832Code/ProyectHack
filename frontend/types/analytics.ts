// Analytics API Types

export interface FetchAnalyticsParams {
  keyword: string;
  idCompany?: number;
  limit?: number;
}

export interface AnalyticsResponse {
  keyword: string;
  count_mentions: number;
  approval_score: number;
  sentiment_total_posts: number;
  sentiment_positive_count: number;
  sentiment_negative_count: number;
  sentiment_neutral_count: number;
  error: string | null;
}

