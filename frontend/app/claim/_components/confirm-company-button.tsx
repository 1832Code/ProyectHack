"use client";

import { useServices } from "@/components/providers/services-providers";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { useEffect, useRef } from "react";

interface ConfirmCompanyButtonProps {
  categories?: string[];
  companyName?: string;
  country?: string;
}

export function ConfirmCompanyButton({
  categories,
  companyName,
  country,
}: ConfirmCompanyButtonProps) {
  const { fetchCompanyPosts, resetAll } = useServices();
  const router = useRouter();
  const hasInitialized = useRef(false);

  const handleConfirmCompany = () => {
    const payload = {
      companyName,
      country,
      categories,
    };
    const encoded = btoa(encodeURIComponent(JSON.stringify(payload)));

    router.push(`/dashboard?data=${encoded}`);
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
      platforms: ["google"],
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
