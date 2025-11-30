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
    const encoded = btoa(encodeURIComponent(JSON.stringify(payload)));

    router.push(`/dashboard?data=${encoded}`);
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
