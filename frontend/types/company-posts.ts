// Company Posts API Types

export type Platform = "tiktok" | "instagram" | "twitter" | "youtube" | "google" | "x";

export interface CompanyPostsRequest {
  query: string;
  max_items: number;
  platforms: Platform[];
  country_code: string;
  language_code: string;
  force_refresh: boolean;
  process_posts: boolean;
}

export interface CompanyPost {
  id: number;
  id_company: number;
  title: string;
  description: string;
  insight1: number;
  insight2: number;
  insight3: number;
  sentiment: number;
  created_at: string;
  updated_at: string;
  image: string;
  video: string;
  query: string | null;
}

export interface CapturedPlatforms {
  tiktok?: number;
  instagram?: number;
  twitter?: number;
  youtube?: number;
}

export interface CompanyPostsResponse {
  status: "success" | "error";
  message: string;
  captured: CapturedPlatforms;
  posts_created: number;
  skipped_platforms: string[];
  posts: CompanyPost[];
}

