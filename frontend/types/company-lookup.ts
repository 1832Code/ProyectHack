// Company Lookup API Types

export interface CompanyLookupRequest {
  company: string;
  keywords: string[];
  max_items_per_query: number;
  country_code: string;
  language_code: string;
  force_refresh: boolean;
}

export interface CompanyAgent {
  company_name: string;
  short_description: string;
  keywords: string[];
  logo_url: string;
  domain: string;
  additional_data: {
    sector: string;
    ubicacion: string;
    mercado_objetivo: string;
    productos_principales: string[];
    servicios: string[];
  };
}

export interface SearchQuery {
  term: string;
  url: string;
  device: string;
  page: number;
  type: string;
  domain: string;
  countryCode: string;
  languageCode: string;
  locationUule: string | null;
  resultsPerPage: number;
}

export interface SiteLink {
  title: string;
  url: string;
  description: string;
}

export interface OrganicResult {
  title: string;
  url: string;
  displayedUrl: string;
  description: string;
  emphasizedKeywords: string[];
  siteLinks: SiteLink[];
  productInfo: Record<string, unknown>;
  type: string;
  position: number;
  followersAmount?: string;
  likes?: string;
  lastUpdated?: string;
  channelName?: string;
}

export interface RelatedQuery {
  title: string;
  url: string;
}

export interface CompanySearchResult {
  "#debug": {
    requestId: string;
    url: string;
    loadedUrl: string;
    method: string;
    retryCount: number;
    errorMessages: string[];
    statusCode: number;
  };
  "#error": boolean;
  searchQuery: SearchQuery;
  url: string;
  hasNextPage: boolean;
  serpProviderCode: string;
  resultsTotal: number | null;
  relatedQueries: RelatedQuery[];
  paidResults: unknown[];
  paidProducts: unknown[];
  organicResults: OrganicResult[];
  suggestedResults: unknown[];
  peopleAlsoAsk: unknown[];
  customData: unknown | null;
  htmlSnapshotUrl: string;
}

export interface CompanyResults {
  company: string;
  keywords: string[];
  company_results: CompanySearchResult[];
  keyword_results: Record<string, CompanySearchResult[]>;
}

export interface CompanyLookupSummary {
  total_company_results: number;
  total_keyword_results: number;
  total_results: number;
  keywords_searched: number;
  keywords_with_results: number;
}

export interface CompanyLookupResponse {
  status: "success" | "error";
  company: string;
  keywords: string[];
  agent: CompanyAgent;
  results: CompanyResults;
  summary: CompanyLookupSummary;
  message: string | null;
}

