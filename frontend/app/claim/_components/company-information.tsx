import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { ConfirmCompanyButton } from "./confirm-company-button";
import { Building2 } from "lucide-react";
import { lookupCompany } from "@/lib/api";
import { CompanyLookupResponse } from "@/types/company-lookup";

interface CompanyConfirmationProps {
  companyName: string;
  country: string;
}

export async function CompanyConfirmation({
  companyName,
  country,
}: CompanyConfirmationProps) {
  let company: CompanyLookupResponse | null = null;
  try {
    company = await lookupCompany({
      company: companyName,
      countryCode: country,
    });
  } catch (error) {
    console.error(error);
    throw new Error("Error loading company information", { cause: error });
  }

  return (
    <div className="flex flex-col items-center text-center max-w-md w-full space-y-8">
      {/* Big Avatar */}
      <Avatar className="h-32 w-32 border-4 border-muted">
        <AvatarImage
          src={company?.agent.logo_url || "/placeholder.svg"}
          alt={company?.agent.company_name || "Company Logo"}
        />
        <AvatarFallback className="text-3xl bg-muted">
          <Building2 className="h-12 w-12 text-muted-foreground" />
        </AvatarFallback>
      </Avatar>

      {/* Company Name */}
      <h1 className="text-3xl md:text-4xl font-bold text-foreground text-balance">
        {company?.agent.company_name}
      </h1>

      {/* Sector */}
      <div className="space-y-2">
        <p className="text-sm text-muted-foreground uppercase tracking-wide">
          Sector
        </p>
        <p className="text-lg font-medium text-foreground">
          {company?.agent.additional_data.sector}
        </p>
      </div>

      {/* Categories */}
      <div className="space-y-3">
        <p className="text-sm text-muted-foreground uppercase tracking-wide">
          Categories
        </p>
        <div className="flex flex-wrap justify-center gap-2">
          {company?.agent.keywords.map((category) => (
            <Badge key={category} variant="secondary" className="px-3 py-1">
              {category}
            </Badge>
          ))}
        </div>
      </div>

      {/* CTA Button */}
      <ConfirmCompanyButton
        categories={company?.agent.keywords}
        companyName={companyName}
        country={country}
      />
    </div>
  );
}
