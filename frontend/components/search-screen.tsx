"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { searchCompany } from "@/lib/api";
import { SearchCommand } from "./search-command";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from "@/components/ui/form";

const countries = [
  { id: "peru", label: "Peru", flag: "🇵🇪" },
  { id: "chile", label: "Chile", flag: "🇨🇱" },
];

const searchFormSchema = z.object({
  companyName: z
    .string()
    .min(2, "Name must have at least 2 characters")
    .max(100, "Name cannot exceed 100 characters"),
  country: z.string().min(1, "Select a country"),
  sector: z.string().min(2, "Sector is required"),
  keywords: z.string().optional(),
});

type SearchFormValues = z.infer<typeof searchFormSchema>;

export function SearchScreen() {
  const router = useRouter();

  const form = useForm<SearchFormValues>({
    resolver: zodResolver(searchFormSchema),
    defaultValues: {
      companyName: "",
      country: "",
      sector: "",
      keywords: "",
    },
    mode: "onChange",
  });

  const {
    formState: { isSubmitting },
    setValue,
    watch,
  } = form;

  const companyName = watch("companyName");
  const country = watch("country");
  const sector = watch("sector");

  // Button is enabled when a company is selected (which auto-fills sector) and country is chosen
  const isFormReady =
    companyName.length >= 2 && country.length > 0 && sector.length >= 2;

  const onSubmit = (data: SearchFormValues) => {
    const queryParams = new URLSearchParams();
    queryParams.set("companyName", data.companyName);
    queryParams.set("country", data.country);

    router.push(`/claim?${queryParams.toString()}`);
  };

  const handleCompanySelect = (company: { name: string; sector: string }) => {
    setValue("companyName", company.name, { shouldValidate: true });
    setValue("sector", company.sector, { shouldValidate: true });
  };

  return (
    <div className="min-h-screen bg-background px-5 py-6 flex flex-col">
      <header className="mb-8">
        <Button
          variant="secondary"
          size="sm"
          asChild
          className="mb-5 -ml-2 bg-card hover:bg-secondary text-muted-foreground hover:text-foreground rounded-full px-3"
        >
          <Link href="/">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="mr-1"
            >
              <path d="m12 19-7-7 7-7" />
              <path d="M19 12H5" />
            </svg>
            Back
          </Link>
        </Button>
        <h1 className="text-[36px] font-bold text-foreground tracking-tight font-serif leading-tight text-center">
          New <span className="text-primary">Search</span>
        </h1>
      </header>

      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex flex-col gap-8 flex-1"
        >
          {/* Company Name Field */}
          <FormField
            control={form.control}
            name="companyName"
            render={({ field }) => (
              <FormItem className="flex justify-center w-full items-center">
                <FormControl>
                  <SearchCommand
                    value={field.value}
                    onChange={field.onChange}
                    onCompanySelect={handleCompanySelect}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Country Field */}
          <FormField
            control={form.control}
            name="country"
            render={({ field }) => (
              <FormItem className="flex flex-col gap-3">
                <div className="flex items-center gap-3">
                  {countries.map((c) => (
                    <Badge
                      key={c.id}
                      variant={field.value === c.id ? "default" : "outline"}
                      onClick={() => field.onChange(c.id)}
                      className="cursor-pointer"
                    >
                      <span className="text-base">{c.flag}</span>
                      {c.label}
                    </Badge>
                  ))}
                </div>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Hidden Sector Field - auto-filled from company selection */}
          <FormField
            control={form.control}
            name="sector"
            render={() => <input type="hidden" />}
          />

          {/* Spacer to push button to bottom */}
          <div className="flex-1" />

          {/* Submit Button */}
          <div className="flex flex-col gap-2">
            {form.formState.errors.root && (
              <p className="text-sm text-destructive text-center">
                {form.formState.errors.root.message}
              </p>
            )}
            <Button
              type="submit"
              disabled={!isFormReady || isSubmitting}
              size="lg"
              className={cn(
                "w-full h-14 rounded-2xl text-base font-medium transition-all",
                isFormReady
                  ? "bg-primary hover:bg-primary/90 text-primary-foreground"
                  : "bg-secondary text-muted-foreground",
                "disabled:opacity-40 disabled:cursor-not-allowed"
              )}
            >
              {isSubmitting ? "Searching..." : "continue"}
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
