import { DashboardScreen } from "@/components/dashboard-screen";

interface DashboardPageProps {
  searchParams: Promise<{ data?: string }>;
}

export default async function DashboardPage({ searchParams }: DashboardPageProps) {
  const { data } = await searchParams;

  if (data) {
    const decoded = JSON.parse(decodeURIComponent(atob(data)));
    console.log("Decoded data:", decoded);
  }

  return <DashboardScreen />;
}
