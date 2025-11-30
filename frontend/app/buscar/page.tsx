import { SearchScreen } from "@/components/search-screen";
import { getServerSession } from "next-auth";
import authOptions from "@/lib/auth";
import { redirect } from "next/navigation";

export default async function BuscarPage() {
  // Require authentication on the /buscar page.
  const session = await getServerSession(authOptions as any);

  if (!session) {
    // If user is not authenticated, redirect to the sign-in page.
    redirect("/signin");
  }

  return <SearchScreen />;
}
