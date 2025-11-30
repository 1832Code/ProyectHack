import { NextRequest, NextResponse } from "next/server";

const COMPANY_POSTS_API =
  process.env.NEXT_PUBLIC_COMPANY_POSTS_API ||
  "https://global-search-api-a2kpxwo5oq-uc.a.run.app";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();


    console.log("body posts route", body);

    const response = await fetch(`${COMPANY_POSTS_API}/posts`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      next: { revalidate: 60 * 10 },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.message || errorData.error || "Failed to fetch company posts" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("API proxy error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

