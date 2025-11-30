import { DashboardScreen } from "@/components/dashboard-screen";

interface DashboardPageProps {
  searchParams: Promise<{ data?: string }>;
}

interface CompanyAttributes {
  companyName: string;
  country: string;
  categories: string[];
}

export default async function DashboardPage({ searchParams }: DashboardPageProps) {
  const { data } = await searchParams;
  let decodedData: CompanyAttributes | null = null;

  if (data) {
    decodedData = JSON.parse(decodeURIComponent(atob(data)));
    console.log("Decoded data:", decodedData);
  }

  return <DashboardScreen companyName={decodedData?.companyName ?? ""} />;
}
