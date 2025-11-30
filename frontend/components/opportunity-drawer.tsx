"use client";

import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerDescription,
} from "@/components/ui/drawer";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { AlertCircle, Lightbulb } from "lucide-react";
import { OpportunityCard } from "./opportunity-card";
import { useServices } from "./providers/services-providers";

interface OpportunityDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

function SkeletonLine({ className }: { className?: string }) {
  return (
    <div
      className={`h-4 bg-muted-foreground/20 rounded animate-pulse ${className || ""}`}
    />
  );
}

function OpportunityCardSkeleton() {
  return (
    <div className="rounded-lg border bg-card p-4 space-y-4">
      {/* Insight skeleton */}
      <div className="space-y-2">
        <SkeletonLine className="w-3/4" />
        <SkeletonLine className="w-1/2" />
      </div>
      
      {/* Tags skeleton */}
      <div className="flex gap-2">
        <div className="h-6 w-16 bg-muted-foreground/20 rounded-full animate-pulse" />
        <div className="h-6 w-20 bg-muted-foreground/20 rounded-full animate-pulse" />
        <div className="h-6 w-14 bg-muted-foreground/20 rounded-full animate-pulse" />
      </div>
      
      {/* Description skeleton */}
      <div className="space-y-2">
        <SkeletonLine className="w-full" />
        <SkeletonLine className="w-5/6" />
        <SkeletonLine className="w-4/6" />
      </div>
    </div>
  );
}

function OpportunitySkeleton() {
  return (
    <div className="space-y-3">
      {[...Array(4)].map((_, index) => (
        <div key={index} className="border-b border-border/50 pb-3">
          {/* Accordion trigger skeleton */}
          <div className="flex items-center justify-between py-3">
            <SkeletonLine className="flex-1 mr-4" />
            <div className="h-4 w-4 bg-muted-foreground/20 rounded animate-pulse" />
          </div>
          
          {/* Show expanded card skeleton only for first item */}
          {index === 0 && <OpportunityCardSkeleton />}
        </div>
      ))}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="rounded-full bg-muted p-4 mb-4">
        <Lightbulb className="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 className="text-lg font-medium mb-2">No hay oportunidades aún</h3>
      <p className="text-sm text-muted-foreground max-w-xs">
        Realiza una búsqueda para descubrir oportunidades basadas en el análisis de redes sociales.
      </p>
    </div>
  );
}

function ErrorState({ error }: { error: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="rounded-full bg-destructive/10 p-4 mb-4">
        <AlertCircle className="h-8 w-8 text-destructive" />
      </div>
      <h3 className="text-lg font-medium mb-2">Error al cargar oportunidades</h3>
      <p className="text-sm text-muted-foreground max-w-xs">
        {error}
      </p>
    </div>
  );
}

export function OpportunityDrawer({
  open,
  onOpenChange,
}: OpportunityDrawerProps) {
  const { opportunity, isLoadingOpportunity, opportunityError } = useServices();
  

  console.log("opportunity", opportunity);
  const hasResults = opportunity?.results && opportunity.results.length > 0;
  
  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent>
        <DrawerHeader className="text-left">
          <DrawerTitle className="text-xl">
            {isLoadingOpportunity ? (
              <span className="block h-7 w-64 bg-muted-foreground/20 rounded animate-pulse" />
            ) : (
              <>Oportunidades {opportunity?.query ? `para "${opportunity.query}"` : ""}</>
            )}
          </DrawerTitle>
          <DrawerDescription>
            {isLoadingOpportunity ? (
              <span className="block h-5 w-80 bg-muted-foreground/20 rounded animate-pulse" />
            ) : hasResults ? (
              `${opportunity.results.length} oportunidades encontradas basados en el análisis de redes sociales`
            ) : (
              "Descubre insights y oportunidades de mejora"
            )}
          </DrawerDescription>
        </DrawerHeader>
        <div className="overflow-y-auto max-h-[70vh] px-4 pb-6">
          {isLoadingOpportunity ? (
            <OpportunitySkeleton />
          ) : opportunityError ? (
            <ErrorState error={opportunityError} />
          ) : !hasResults ? (
            <EmptyState />
          ) : (
            <Accordion
              type="single"
              collapsible
              defaultValue="item-0"
              className="w-full"
            >
              {opportunity.results.map((result, index) => (
                <AccordionItem
                  key={index}
                  value={`item-${index}`}
                  className="border-none"
                >
                  <AccordionTrigger className="hover:no-underline py-3 group">
                    <span className="text-sm font-medium text-left line-clamp-1 pr-2 group-hover:text-primary transition-colors">
                      {result.insight}
                    </span>
                  </AccordionTrigger>
                  <AccordionContent>
                    <OpportunityCard result={result} />
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          )}
        </div>
      </DrawerContent>
    </Drawer>
  );
}
