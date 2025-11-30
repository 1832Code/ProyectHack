"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

export default function BackButton({
  className = "",
  children,
  ariaLabel = "Volver",
}: {
  className?: string;
  children?: React.ReactNode;
  ariaLabel?: string;
}) {
  const router = useRouter();

  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label={ariaLabel}
      onClick={() => router.back()}
      className={`p-2 rounded-full ${className}`}
    >
      {children ?? <ArrowLeft className="w-4 h-4" />}
    </Button>
  );
}
