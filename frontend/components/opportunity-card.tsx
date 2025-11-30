"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Lightbulb, ChevronDown, ChevronUp } from "lucide-react";
import type { OpportunityResult } from "@/types/opportunity";

interface OpportunityCardProps {
  result: OpportunityResult;
}

export function OpportunityCard({ result }: OpportunityCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <Card className="border-l-4 border-l-primary">
      <CardHeader className="pb-3">
        <CardTitle className="text-base font-medium leading-relaxed line-clamp-2">
          {result.insight}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Ideas Section */}
        <div className="space-y-2">
          <h4 className="text-sm font-semibold flex items-center gap-2 text-foreground">
            <Lightbulb className="h-4 w-4 text-primary" />
            Ideas de mejora
          </h4>
          <ul className="space-y-1.5">
            {result.ideas.map((idea, idx) => (
              <li key={idx} className="text-sm flex items-start gap-2">
                <Badge
                  variant="secondary"
                  className="mt-0.5 h-5 w-5 shrink-0 rounded-full p-0 flex items-center justify-center text-xs"
                >
                  {idx + 1}
                </Badge>
                <span>{idea}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Posts Section */}
        <div className="space-y-2">
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-between"
            onClick={() => setExpanded(!expanded)}
          >
            <span className="text-sm font-semibold text-muted-foreground">
              {result.posts.length} posts relacionados
            </span>
            {expanded ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </Button>
          {expanded && (
            <div className="space-y-3 pt-2">
              {result.posts.map((post) => (
                <PostCard key={post.id} title={post.title ||post.description} />
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function PostCard({ title }: { title: string }) {
  return (
    <div className="rounded-lg border border-border bg-secondary/20 p-3 space-y-2">
      <div className="flex items-start gap-3">
        <div className="flex-1 min-w-0">
          {title && <p className="text-sm font-medium truncate text-foreground">{title}</p>}
        </div>
      </div>
    </div>
  );
}
