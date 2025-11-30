"use client";

import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

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
  const router = useRouter();
  const handleConfirmCompany = () => {
    const payload = {
      companyName,
      country,
      categories,
    };
    // Send a user-action to the server to persist this confirmation (requires authenticated user)
    ;(async () => {
      try {
        await fetch("/api/user-actions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ type: "company_confirmation", payload }),
        })
      } catch (e) {
        // Log but continue navigation if saving fails
        console.error("Failed to save user action:", e)
      } finally {
        const encoded = btoa(encodeURIComponent(JSON.stringify(payload)))
        router.push(`/dashboard?data=${encoded}`)
      }
    })()
  }; 

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
