import type {
  CompanyLookupRequest,
  CompanyLookupResponse,
} from "@/types/company-lookup";
import type {
  CompanyPostsRequest,
  CompanyPostsResponse,
  Platform,
} from "@/types/company-posts";
import type {
  FetchAnalyticsParams,
  AnalyticsResponse,
} from "@/types/analytics";
import type {
  FetchOpportunityParams,
  OpportunityRequest,
  OpportunityResponse,
} from "@/types/opportunity";

export type { FetchAnalyticsParams, AnalyticsResponse };
export type { FetchOpportunityParams, OpportunityResponse };

const BASE_URL_API =
  process.env.NEXT_PUBLIC_SEARCH_URL_API ||
  "https://company-lookup-api-1084464085676.us-central1.run.app";

const COMPANY_POSTS_API =
  process.env.NEXT_PUBLIC_COMPANY_POSTS_API ||
  "https://global-search-api-a2kpxwo5oq-uc.a.run.app";

export interface SearchParams {
  name: string;
  country: string;
  sector: string;
  keyword: string;
}

export interface SearchResponse {
  company_name: string;
  country: string;
  sector: string;
  keyword_analysis: any[];
  final_analysis: {
    summary: string;
    key_findings: string[];
    recommendations: string[];
    overall_score: number;
  };
  timestamp: string | null;
}

export async function searchCompany(
  params: SearchParams
): Promise<SearchResponse> {
  const response = await fetch("http://127.0.0.1:5000/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || "Failed to search company");
  }

  return response.json();
}

export interface CompanyLookupParams {
  company: string;
  keywords?: string[];
  maxItemsPerQuery?: number;
  countryCode?: string;
  languageCode?: string;
  forceRefresh?: boolean;
}

export async function lookupCompany(
  params: CompanyLookupParams
): Promise<CompanyLookupResponse> {
  const payload: CompanyLookupRequest = {
    company: params.company,
    keywords: params.keywords ?? [],
    max_items_per_query: params.maxItemsPerQuery ?? 5,
    country_code: params.countryCode ?? "PE",
    language_code: params.languageCode ?? "es",
    force_refresh: params.forceRefresh ?? false,
  };

  console.log("payload", payload);

  const response = await fetch(`${BASE_URL_API}/lookup/company`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.message || errorData.error || "Failed to lookup company"
    );
  }

  return response.json();
}

export interface FetchCompanyPostsParams {
  query: string;
  maxItems?: number;
  platforms?: Platform[];
  countryCode?: string;
  languageCode?: string;
  useCache?: boolean;
  forceRefresh?: boolean;
  processPosts?: boolean;
  showLoading?: boolean;
}

export async function fetchCompanyPosts(
  params: FetchCompanyPostsParams
): Promise<CompanyPostsResponse> {
  const payload: CompanyPostsRequest = {
    query: params.query,
    max_items: params.maxItems ?? 30,
    platforms: params.platforms ?? ["tiktok"],
    country_code: params.countryCode ?? "PE",
    language_code: params.languageCode ?? "es",
    force_refresh: true,
    process_posts: params.processPosts ?? true,
  };

  // Use local API route as proxy to avoid CORS
  const response = await fetch("/api/posts", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.message || errorData.error || "Failed to fetch company posts"
    );
  }

  return response.json();
}

export async function fetchAnalytics(
  params: FetchAnalyticsParams
): Promise<AnalyticsResponse> {
  const searchParams = new URLSearchParams({
    keyword: params.keyword,
    id_company: String(params.idCompany ?? 1),
    limit: String(params.limit ?? 1000),
  });

  // Use local API route as proxy to avoid CORS
  const response = await fetch(`/api/analytics?${searchParams.toString()}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.message || errorData.error || "Failed to fetch analytics"
    );
  }

  return response.json();
}

export async function fetchOpportunity(
  params: FetchOpportunityParams
): Promise<OpportunityResponse> {
  const payload: OpportunityRequest = {
    query: params.query,
    id_company: params.idCompany ?? 1,
    limit: params.limit ?? 100,
  };

  console.log("payload opportunity", payload);

  // Use local API route as proxy to avoid CORS
  const response = await fetch("/api/opportunity", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.message || errorData.error || "Failed to fetch opportunity"
    );
  }

  return response.json();
}
