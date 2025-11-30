import { NextRequest, NextResponse } from "next/server";

const COMPANY_POSTS_API =
  process.env.NEXT_PUBLIC_COMPANY_POSTS_API ||
  "https://global-search-api-a2kpxwo5oq-uc.a.run.app";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const { query, id_company, limit } = body;

    if (!query) {
      return NextResponse.json({ error: "query is required" }, { status: 400 });
    }

    console.log("body opportunity route", body);

    const payload = {
      query,
      id_company: id_company ?? 1,
      limit: limit ?? 100,
    };

    const response = await fetch(`${COMPANY_POSTS_API}/oportunity`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      next: { revalidate: 60 * 60 * 2 },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        {
          error:
            errorData.message ||
            errorData.error ||
            "Failed to fetch opportunity",
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Opportunity API proxy error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
