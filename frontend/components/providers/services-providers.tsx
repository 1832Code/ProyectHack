"use client";

import { createContext, useContext, useState, type ReactNode } from "react";
import {
  fetchCompanyPosts as fetchCompanyPostsApi,
  fetchAnalytics as fetchAnalyticsApi,
  fetchOpportunity as fetchOpportunityApi,
  type FetchCompanyPostsParams,
  type FetchAnalyticsParams,
  type FetchOpportunityParams,
} from "@/lib/api";
import type { CompanyPostsResponse, CompanyPost } from "@/types/company-posts";
import type { AnalyticsResponse } from "@/types/analytics";
import type { OpportunityResponse } from "@/types/opportunity";

interface ServicesContextType {
  isLoading: boolean;
  isLoadingAnalytics: boolean;
  isLoadingOpportunity: boolean;
  companyPosts: CompanyPostsResponse | null;
  analytics: AnalyticsResponse | null;
  opportunity: OpportunityResponse | null;
  error: string | null;
  analyticsError: string | null;
  opportunityError: string | null;
  fetchCompanyPosts: (params: FetchCompanyPostsParams) => Promise<void>;
  fetchAnalytics: (params: FetchAnalyticsParams) => Promise<void>;
  fetchOpportunity: (params: FetchOpportunityParams) => Promise<void>;
  clearCompanyPosts: () => void;
  resetAll: () => void;
}

// Helper function to remove duplicate posts by id
function removeDuplicatePosts(posts: CompanyPost[]): CompanyPost[] {
  const seen = new Set<number>();
  return posts.filter((post) => {
    if (seen.has(post.id)) {
      return false;
    }
    seen.add(post.id);
    return true;
  });
}

// Helper function to reorder posts with images at the top
function reorderPostsWithImagesFirst(posts: CompanyPost[]): CompanyPost[] {
  const postsWithImages = posts.filter(
    (post) => post.image && post.image.trim() !== ""
  );
  const postsWithoutImages = posts.filter(
    (post) => !post.image || post.image.trim() === ""
  );
  return [...postsWithImages, ...postsWithoutImages];
}

const ServicesContext = createContext<ServicesContextType | undefined>(
  undefined
);

export function useServices() {
  const context = useContext(ServicesContext);
  if (context === undefined) {
    throw new Error("useServices must be used within a ServicesProvider");
  }
  return context;
}

interface ServicesProviderProps {
  children: ReactNode;
}

export function ServicesProvider({ children }: ServicesProviderProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingAnalytics, setIsLoadingAnalytics] = useState(false);
  const [isLoadingOpportunity, setIsLoadingOpportunity] = useState(false);
  const [companyPosts, setCompanyPosts] = useState<CompanyPostsResponse | null>(
    null
  );

  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [opportunity, setOpportunity] = useState<OpportunityResponse | null>(
    null
  );

  const [error, setError] = useState<string | null>(null);
  const [analyticsError, setAnalyticsError] = useState<string | null>(null);
  const [opportunityError, setOpportunityError] = useState<string | null>(null);

  const fetchAnalytics = async ({
    keyword,
    idCompany,
    limit,
  }: FetchAnalyticsParams) => {
    setIsLoadingAnalytics(true);
    console.log("🚀 Starting analytics request...", keyword);

    try {
      const response = await fetchAnalyticsApi({
        keyword,
        idCompany,
        limit,
      });

      console.log("✅ Analytics request successful!");
      console.log("📦 Analytics data:", response);

      setAnalytics(response);
      setAnalyticsError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      console.log("❌ Analytics request failed:", errorMessage);
      setAnalyticsError(errorMessage);
    } finally {
      setIsLoadingAnalytics(false);
      console.log("🏁 Analytics request completed. Loading state:", false);
    }
  };

  const fetchOpportunity = async ({
    query,
    idCompany,
    limit,
  }: FetchOpportunityParams) => {
    setIsLoadingOpportunity(true);
    console.log("🚀 Starting opportunity request...", query);

    try {
      const response = await fetchOpportunityApi({
        query,
        idCompany,
        limit,
      });

      console.log("response opportunity", response);

      console.log("✅ Opportunity request successful!");
      console.log("📦 Opportunity data:", response);

      setOpportunity(response);
      setOpportunityError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      console.log("❌ Opportunity request failed:", errorMessage);
      setOpportunityError(errorMessage);
    } finally {
      setIsLoadingOpportunity(false);
      console.log("🏁 Opportunity request completed. Loading state:", false);
    }
  };

  const fetchCompanyPosts = async ({
    query,
    maxItems,
    platforms,
  }: FetchCompanyPostsParams) => {
    setIsLoading(true);
    console.log("🚀 Starting test request to fetchCompanyPosts...", query);

    try {
      const response = await fetchCompanyPostsApi({
        query,
        maxItems,
        platforms,
      });

      fetchAnalytics({
        keyword: query,
        idCompany: 1,
        limit: 1000,
      });

      fetchOpportunity({
        query,
        idCompany: 1,
        limit: 100,
      });

      console.log("✅ Test request successful!");
      console.log("📦 Response data:", response);

      // Accumulate posts, remove duplicates, and reorder with images first
      setCompanyPosts((prev) => {
        if (!prev) {
          const reorderedPosts = reorderPostsWithImagesFirst(response.posts);
          return {
            ...response,
            posts: reorderedPosts,
          };
        }

        const allPosts = [...prev.posts, ...response.posts];
        const uniquePosts = removeDuplicatePosts(allPosts);
        const reorderedPosts = reorderPostsWithImagesFirst(uniquePosts);

        return {
          ...response,
          posts: reorderedPosts,
          posts_created: reorderedPosts.length,
        };
      });
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      console.log("❌ Test request failed:", errorMessage);
      setError(errorMessage);
    } finally {
      setIsLoading(false);
      console.log("🏁 Test request completed. Loading state:", false);
    }
  };

  const clearCompanyPosts = () => {
    setCompanyPosts(null);
  };

  const resetAll = () => {
    setCompanyPosts(null);
    setAnalytics(null);
    setOpportunity(null);
    setError(null);
    setAnalyticsError(null);
    setOpportunityError(null);
    setIsLoading(true);
    setIsLoadingAnalytics(false);
    setIsLoadingOpportunity(false);
  };

  const value: ServicesContextType = {
    isLoading,
    isLoadingAnalytics,
    isLoadingOpportunity,
    companyPosts,
    analytics,
    opportunity,
    error,
    analyticsError,
    opportunityError,
    fetchCompanyPosts,
    fetchAnalytics,
    fetchOpportunity,
    clearCompanyPosts,
    resetAll,
  };

  return (
    <ServicesContext.Provider value={value}>
      {children}
    </ServicesContext.Provider>
  );
}
