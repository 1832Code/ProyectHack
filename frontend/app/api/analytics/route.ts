import { NextRequest, NextResponse } from "next/server";

const COMPANY_POSTS_API =
  process.env.NEXT_PUBLIC_COMPANY_POSTS_API ||
  "https://global-search-api-a2kpxwo5oq-uc.a.run.app";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    
    const keyword = searchParams.get("keyword");
    const idCompany = searchParams.get("id_company");
    const limit = searchParams.get("limit");

    if (!keyword) {
      return NextResponse.json(
        { error: "keyword is required" },
        { status: 400 }
      );
    }

    const params = new URLSearchParams({
      keyword,
      id_company: idCompany ?? "1",
      limit: limit ?? "1000",
    });

    const response = await fetch(
      `${COMPANY_POSTS_API}/analytics?${params.toString()}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        next: { revalidate: 60 * 60 * 2 },
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.message || errorData.error || "Failed to fetch analytics" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Analytics API proxy error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

