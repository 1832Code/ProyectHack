"use client";

import { useState, useCallback, useEffect, useRef, useMemo } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  MessageSquare,
  Sparkles,
  ThumbsDown,
  Minus,
  ThumbsUp,
  AlertCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useServices } from "@/components/providers/services-providers";
import type { CompanyPost } from "@/types/company-posts";

const sentimentColors = {
  positive: "bg-emerald-50 text-emerald-700 border-emerald-200 shadow-sm",
  negative: "bg-blue-50 text-blue-700 border-blue-200 shadow-sm",
  neutral: "bg-purple-50 text-purple-700 border-purple-200 shadow-sm",
};

const sentimentIcons = {
  positive: ThumbsUp,
  negative: ThumbsDown,
  neutral: Minus,
};

function getSentimentType(
  sentiment: number
): "positive" | "negative" | "neutral" {
  if (sentiment > 0.3) return "positive";
  if (sentiment < -0.3) return "negative";
  return "neutral";
}

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return "Ahora";
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h`;
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d`;
  return date.toLocaleDateString("es-PE", { day: "numeric", month: "short" });
}

function PostSkeleton() {
  return (
    <Card className="border border-slate-200 bg-white/80 rounded-2xl shadow-lg overflow-hidden animate-pulse">
      <CardContent className="p-5">
        <div className="flex items-start gap-4">
          <div className="p-3 rounded-xl bg-slate-200 w-11 h-11" />
          <div className="flex-1 min-w-0 space-y-3">
            <div className="flex items-center justify-between gap-2">
              <div className="h-4 bg-slate-200 rounded w-32" />
              <div className="h-3 bg-slate-200 rounded w-12" />
            </div>
            <div className="space-y-2">
              <div className="h-3 bg-slate-200 rounded w-full" />
              <div className="h-3 bg-slate-200 rounded w-3/4" />
            </div>
            <div className="flex items-center justify-between">
              <div className="h-3 bg-slate-200 rounded w-20" />
              <div className="h-6 bg-slate-200 rounded-full w-20" />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function Mentions() {
  const { companyPosts, isLoading: isProviderLoading, error } = useServices();
  const allPosts = useMemo(() => companyPosts?.posts ?? [], [companyPosts]);

  const [displayedPosts, setDisplayedPosts] = useState<CompanyPost[]>([]);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const loaderRef = useRef<HTMLDivElement>(null);

  // Initialize displayed posts when provider data loads
  useEffect(() => {
    if (allPosts.length > 0) {
      setDisplayedPosts(allPosts.slice(0, 5));
      setHasMore(allPosts.length > 5);
    }
  }, [allPosts]);

  const loadMore = useCallback(() => {
    if (isLoadingMore || !hasMore || allPosts.length === 0) return;

    setIsLoadingMore(true);
    setTimeout(() => {
      const currentLength = displayedPosts.length;
      const nextItems = allPosts.slice(currentLength, currentLength + 5);
      if (nextItems.length === 0) {
        setHasMore(false);
      } else {
        setDisplayedPosts((prev) => [...prev, ...nextItems]);
        setHasMore(currentLength + nextItems.length < allPosts.length);
      }
      setIsLoadingMore(false);
    }, 500);
  }, [displayedPosts.length, isLoadingMore, hasMore, allPosts]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (
          entries[0].isIntersecting &&
          hasMore &&
          !isLoadingMore &&
          !isProviderLoading
        ) {
          loadMore();
        }
      },
      { threshold: 0.1 }
    );

    if (loaderRef.current) {
      observer.observe(loaderRef.current);
    }

    return () => observer.disconnect();
  }, [loadMore, hasMore, isLoadingMore, isProviderLoading]);

  // Loading state
  // if (isProviderLoading && companyPosts?.posts.length === 0) {
  if (isProviderLoading) {
    return (
      <section className="pb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2" />
          <div className="h-4 bg-slate-200 rounded w-20 animate-pulse" />
        </div>
        <div className="flex flex-col gap-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <PostSkeleton key={i} />
          ))}
        </div>
      </section>
    );
  }

  // Error state
  if (error) {
    return (
      <section className="pb-8">
        <Card className="border border-red-200 bg-red-50 rounded-2xl">
          <CardContent className="p-6 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <p className="text-sm text-red-700">
              Error al cargar las menciones: {error}
            </p>
          </CardContent>
        </Card>
      </section>
    );
  }

  // Empty state
  if (allPosts.length === 0) {
    return (
      <section className="pb-8">
        <Card className="border border-slate-200 bg-white/80 rounded-2xl">
          <CardContent className="p-8 text-center">
            <MessageSquare className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <p className="text-slate-500">No hay menciones disponibles</p>
          </CardContent>
        </Card>
      </section>
    );
  }

  return (
    <section className="pb-8">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2" />
        <span className="text-sm text-slate-500">
          {allPosts.length} en total
        </span>
      </div>

      <div className="flex flex-col gap-4">
        {displayedPosts.map((post) => {
          const sentimentType = getSentimentType(post.sentiment);
          const SentimentIcon = sentimentIcons[sentimentType];

          return (
            <Card
              key={post.id}
              className="border border-slate-200 bg-white/80 rounded-2xl shadow-lg overflow-hidden"
            >
              <CardContent className="p-5">
                <div className="flex items-start gap-4">
                  {post.image ? (
                    <img
                      src={post.image}
                      alt=""
                      className="w-11 h-11 rounded-xl object-cover border border-slate-200"
                    />
                  ) : (
                    <div className="p-3 rounded-xl border shadow-sm text-white bg-purple-500 border-purple-400">
                      <MessageSquare className="w-5 h-5" />
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2 mb-2">
                      {post.title && (
                        <span className="text-sm font-semibold text-slate-800 truncate">
                          {post.title}
                        </span>
                      )}
                      <span className="text-xs text-slate-500 shrink-0">
                        {formatTimeAgo(post.created_at)}
                      </span>
                    </div>
                    <p className="text-sm text-slate-600 leading-relaxed line-clamp-2 mb-3">
                      {post.description}
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-500">
                        {post.query || "Mención"}
                      </span>
                      <Badge
                        variant="secondary"
                        className={cn(
                          "text-xs font-medium px-3 py-1.5 rounded-full border flex items-center gap-1.5",
                          sentimentColors[sentimentType]
                        )}
                      >
                        <SentimentIcon className="w-3 h-3" />
                        {sentimentType === "positive"
                          ? "Positivo"
                          : sentimentType === "negative"
                          ? "Negativo"
                          : "Neutro"}
                      </Badge>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div ref={loaderRef} className="flex justify-center py-6">
        {isLoadingMore && (
          <div className="flex items-center gap-2 text-slate-500">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600" />
            <span className="text-sm">Cargando más menciones...</span>
          </div>
        )}
        {!hasMore && displayedPosts.length > 0 && (
          <p className="text-sm text-slate-500">
            No hay más menciones para cargar
          </p>
        )}
      </div>

      {/* Generate Report Button */}
      <div className="mt-2">
        <Button className="w-full h-14 rounded-2xl bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white text-base font-semibold shadow-lg hover:shadow-xl transition-all duration-300">
          <Sparkles className="w-5 h-5 mr-2" />
          Generar reporte
        </Button>
      </div>
    </section>
  );
}
