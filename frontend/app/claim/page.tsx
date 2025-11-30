import { Suspense } from "react";
import { CompanyConfirmation } from "./_components/company-information";
import ClaimLoading from "./_components/claim-loading";

interface ClaimPageProps {
  searchParams: Promise<{
    companyName?: string;
    country?: string;
  }>;
}

export default async function Claim({ searchParams }: ClaimPageProps) {
  const { companyName, country } = await searchParams;

  return (
    <main className="min-h-screen flex items-center justify-center bg-background ">
      <Suspense fallback={<ClaimLoading />}>
        <CompanyConfirmation
          companyName={companyName ?? ""}
          country={country ?? ""}
        />
      </Suspense>
    </main>
  );
}
