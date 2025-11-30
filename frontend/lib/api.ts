import type {
  CompanyLookupRequest,
  CompanyLookupResponse,
} from "@/types/company-lookup";

const BASE_URL_API =
  process.env.NEXT_PUBLIC_BASE_URL_API ||
  "https://company-lookup-api-1084464085676.us-central1.run.app";

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

