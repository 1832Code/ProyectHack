import { NextResponse } from "next/server"
import { getServerSession } from "next-auth"
import { authOptions } from "@/lib/auth"
import { supabaseAdmin } from "@/lib/supabase-server"

export async function POST(req: Request) {
  try {
    const session = (await getServerSession(authOptions as any)) as any

    if (!session || !session.user) {
      return NextResponse.json({ error: "Unauthenticated" }, { status: 401 })
    }

    const body = await req.json()
    const { type, payload } = body || {}

    if (!type) {
      return NextResponse.json({ error: "Missing type" }, { status: 400 })
    }

    // Insert action into user_actions table. Ensure this table exists on your Supabase project.
    const userId = session.user?.id ?? session.user?.email ?? null

    const insertPayload: any = {
      user_id: userId,
      type,
      payload: JSON.stringify(payload ?? {}),
      created_at: new Date().toISOString(),
    }

    const { error } = await supabaseAdmin.from("user_actions").insert([insertPayload])
    if (error) {
      console.error("Supabase insert error (user_actions):", error)
      return NextResponse.json({ error: "DB error" }, { status: 500 })
    }

    return NextResponse.json({ ok: true })
  } catch (e) {
    console.error(e)
    return NextResponse.json({ error: "Server error" }, { status: 500 })
  }
}
