"use client";

import { useServices } from "@/components/providers/services-providers";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { useEffect, useRef } from "react";

interface ConfirmCompanyButtonProps {
  categories?: string[];
  companyName?: string;
  country?: string;
  companyLogo?: string;
}

export function ConfirmCompanyButton({
  categories,
  companyName,
  country,
  companyLogo,
}: ConfirmCompanyButtonProps) {
  const { fetchCompanyPosts, resetAll } = useServices();
  const router = useRouter();
  const hasInitialized = useRef(false);

  const handleConfirmCompany = () => {
    const payload = {
      companyName,
      country,
      categories,
      companyLogo,
    };
    // Send a user-action to the server to persist this confirmation (requires authenticated user)
    (async () => {
      try {
        await fetch("/api/user-actions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ type: "company_confirmation", payload }),
        });
      } catch (e) {
        // Log but continue navigation if saving fails
        console.error("Failed to save user action:", e);
      } finally {
        const encoded = btoa(encodeURIComponent(JSON.stringify(payload)));
        router.push(`/dashboard?data=${encoded}`);
      }
    })();
  };

  useEffect(() => {
    // Only run once on mount - reset all data and start fresh fetch
    if (hasInitialized.current) return;
    hasInitialized.current = true;

    // Reset all previous analytics and posts data
    resetAll();

    // Fetch fresh company posts
    fetchCompanyPosts({
      query: companyName ?? "",
      maxItems: 10,
      platforms: ["tiktok"],
    });
  }, [companyName, fetchCompanyPosts, resetAll]);

  return (
    <Button
      size="lg"
      className="mt-4 w-full max-w-xs text-base"
      onClick={handleConfirmCompany}
    >
      Yes, this is my company
    </Button>
  );
}
