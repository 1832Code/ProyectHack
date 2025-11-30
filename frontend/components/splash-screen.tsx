"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"

const ArrowRightIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className="ml-2"
  >
    <path d="M5 12h14" />
    <path d="m12 5 7 7-7 7" />
  </svg>
)

export function SplashScreen() {
  return (
    <div className="min-h-screen bg-background flex flex-col px-5 py-10">
      <header className="flex items-center gap-3">
        <div className="h-9 w-9 rounded-xl bg-primary flex items-center justify-center">
          <span className="text-primary-foreground font-semibold text-sm">S</span>
        </div>
        <span className="text-base font-semibold tracking-tight text-foreground">Signal</span>
      </header>

      <main className="flex-1 flex flex-col justify-center gap-6">
        <h1 className="text-[38px] font-bold text-foreground leading-[1.1] tracking-tight font-serif">
          Detect what
          <br />
          <span className="text-primary">matters</span> before
          <br />
          anyone else.
        </h1>

        <p className="text-base text-muted-foreground leading-relaxed max-w-[280px]">
          Monitor mentions, analyze sentiment and discover opportunities in real time.
        </p>
      </main>

      <footer className="flex flex-col gap-4">
        <Button
          asChild
          size="lg"
          className="w-full h-14 rounded-2xl text-base font-medium bg-primary hover:bg-primary/90 text-primary-foreground transition-all active:scale-[0.98]"
        >
          <Link href="/buscar">
            Get Started
            <ArrowRightIcon />
          </Link>
        </Button>

        <p className="text-center text-sm text-muted-foreground">No credit card required</p>
      </footer>
    </div>
  )
}
