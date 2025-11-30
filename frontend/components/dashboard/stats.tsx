"use client";

import { Card, CardContent } from "@/components/ui/card";
import {
  TrendingUp,
  MessageCircle,
  Activity,
  BarChart3,
  ThumbsUp,
  ThumbsDown,
  Minus,
} from "lucide-react";
import { useServices } from "@/components/providers/services-providers";

export function DashboardStats() {
  const { analytics, isLoadingAnalytics } = useServices();

  return (
    <>
      {/* Stats Cards */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <Card className="border border-slate-200 bg-white/80 rounded-2xl shadow-lg overflow-hidden">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 mb-2">
              <div className="p-2 rounded-lg bg-purple-500 shadow-sm">
                <MessageCircle className="w-4 h-4 text-white" />
              </div>
              <p className="text-sm text-slate-600 font-medium">Menciones</p>
            </div>
            <div className="flex items-baseline gap-2">
              {isLoadingAnalytics ? (
                <div className="h-9 w-16 bg-slate-200 rounded animate-pulse" />
              ) : (
                <span className="text-3xl font-bold text-slate-800">
                  {analytics?.count_mentions ?? 0}
                </span>
              )}
              <span className="text-sm bg-emerald-500 text-white px-2 py-1 rounded-full font-medium flex items-center gap-0.5">
                <TrendingUp className="w-3 h-3" />
                total
              </span>
            </div>
          </CardContent>
        </Card>
        <Card className="border border-slate-200 bg-white/80 rounded-2xl shadow-lg overflow-hidden">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 mb-2">
              <div className="p-2 rounded-lg bg-purple-500 shadow-sm">
                <Activity className="w-4 h-4 text-white" />
              </div>
              <p className="text-sm text-slate-600 font-medium">Aprobación</p>
            </div>
            <div className="flex items-baseline gap-2">
              {isLoadingAnalytics ? (
                <div className="h-9 w-16 bg-slate-200 rounded animate-pulse" />
              ) : (
                <span className="text-3xl font-bold text-slate-800">
                  {analytics?.approval_score?.toFixed(1) ?? "0.0"}%
                </span>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sentiment Breakdown */}
      {/* <div className="">
        <Card className="border border-slate-200 bg-white/80 rounded-2xl shadow-lg p-3">
          <CardContent className="px-0">
            {isLoadingAnalytics ? (
              <div className="space-y-1">
                <div className="h-4 w-full bg-slate-200 rounded animate-pulse" />
                <div className="flex gap-4">
                  <div className="h-16 flex-1 bg-slate-200 rounded animate-pulse" />
                  <div className="h-16 flex-1 bg-slate-200 rounded animate-pulse" />
                  <div className="h-16 flex-1 bg-slate-200 rounded animate-pulse" />
                </div>
              </div>
            ) : (
              <>
                <div className="h-3 w-full rounded-full overflow-hidden flex mb-4">
                  <div
                    className="bg-emerald-500 transition-all duration-500"
                    style={{
                      width: `${
                        analytics?.sentiment_total_posts
                          ? (analytics.sentiment_positive_count /
                              analytics.sentiment_total_posts) *
                            100
                          : 0
                      }%`,
                    }}
                  />
                  <div
                    className="bg-slate-400 transition-all duration-500"
                    style={{
                      width: `${
                        analytics?.sentiment_total_posts
                          ? (analytics.sentiment_neutral_count /
                              analytics.sentiment_total_posts) *
                            100
                          : 0
                      }%`,
                    }}
                  />
                  <div
                    className="bg-red-500 transition-all duration-500"
                    style={{
                      width: `${
                        analytics?.sentiment_total_posts
                          ? (analytics.sentiment_negative_count /
                              analytics.sentiment_total_posts) *
                            100
                          : 0
                      }%`,
                    }}
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="flex items-center justify-center gap-1.5 mb-1">
                      <ThumbsUp className="w-4 h-4 text-emerald-500" />
                      <span className="text-xs text-slate-500">Positivo</span>
                    </div>
                    <span className="text-xl font-bold text-emerald-600">
                      {analytics?.sentiment_positive_count ?? 0}
                    </span>
                  </div>
                  <div className="text-center">
                    <div className="flex items-center justify-center gap-1.5 mb-1">
                      <Minus className="w-4 h-4 text-slate-400" />
                      <span className="text-xs text-slate-500">Neutral</span>
                    </div>
                    <span className="text-xl font-bold text-slate-600">
                      {analytics?.sentiment_neutral_count ?? 0}
                    </span>
                  </div>
                  <div className="text-center">
                    <div className="flex items-center justify-center gap-1.5 mb-1">
                      <ThumbsDown className="w-4 h-4 text-red-500" />
                      <span className="text-xs text-slate-500">Negativo</span>
                    </div>
                    <span className="text-xl font-bold text-red-600">
                      {analytics?.sentiment_negative_count ?? 0}
                    </span>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div> */}
    </>
  );
}
