"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { cn } from "@/lib/utils"

const countries = [
  { id: "peru", label: "Peru" },
  { id: "chile", label: "Chile" },
]

export function SearchScreen() {
  const router = useRouter()

  const [companyName, setCompanyName] = useState("")
  const [country, setCountry] = useState("")
  const [keywords, setKeywords] = useState("")
  const [errors, setErrors] = useState<{ companyName?: string; country?: string }>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const validate = () => {
    const newErrors: { companyName?: string; country?: string } = {}

    if (!companyName || companyName.length < 2) {
      newErrors.companyName = "Name must have at least 2 characters"
    } else if (companyName.length > 100) {
      newErrors.companyName = "Name cannot exceed 100 characters"
    }

    if (!country) {
      newErrors.country = "Select a country"
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const isValid = companyName.length >= 2 && country !== ""

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!validate()) return

    router.push("/panel")
  }

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
        <h1 className="text-[36px] font-bold text-foreground tracking-tight font-serif italic leading-tight">
          New
          <br />
          <span className="text-primary">Search</span>
        </h1>
      </header>

      <form onSubmit={handleSubmit} className="flex flex-col gap-8 flex-1">
        {/* Company Name Field */}
        <div className="flex flex-col gap-2">
          <Label className="text-base text-muted-foreground italic font-normal">company name</Label>
          <Input
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            placeholder=""
            className="h-14 px-4 bg-card border-0 rounded-2xl text-base text-foreground placeholder:text-muted-foreground/60 focus-visible:ring-2 focus-visible:ring-primary/30 transition-all"
          />
          {errors.companyName && <p className="text-xs text-destructive">{errors.companyName}</p>}
        </div>

        {/* Country Field */}
        <div className="flex flex-col gap-3">
          <Label className="text-base text-muted-foreground italic font-normal">country</Label>
          <div className="flex items-center gap-2">
            <ToggleGroup
              type="single"
              value={country}
              onValueChange={(value) => value && setCountry(value)}
              className="flex gap-2"
            >
              {countries.map((c) => (
                <ToggleGroupItem
                  key={c.id}
                  value={c.id}
                  className={cn(
                    "px-5 h-11 rounded-full text-base font-normal transition-all",
                    "border border-border",
                    "data-[state=off]:bg-background data-[state=off]:text-foreground",
                    "data-[state=off]:hover:bg-secondary",
                    "data-[state=on]:bg-primary data-[state=on]:text-primary-foreground data-[state=on]:border-primary",
                  )}
                >
                  {c.label}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
            <Button
              type="button"
              variant="secondary"
              className="px-6 h-11 rounded-full text-base font-normal bg-secondary text-foreground hover:bg-secondary/80"
            >
              Search
            </Button>
          </div>
          {errors.country && <p className="text-xs text-destructive">{errors.country}</p>}
        </div>

        {/* Keywords Field */}
        <div className="flex flex-col gap-2">
          <Label className="text-base text-muted-foreground italic font-normal">keywords</Label>
          <Textarea
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            placeholder=""
            rows={3}
            className="px-4 py-3 bg-card border-0 rounded-2xl text-base text-foreground placeholder:text-muted-foreground/60 resize-none focus-visible:ring-2 focus-visible:ring-primary/30 transition-all"
          />
        </div>

        {/* Spacer to push button to bottom */}
        <div className="flex-1" />

        {/* Submit Button */}
        <Button
          type="submit"
          disabled={!isValid}
          size="lg"
          className={cn(
            "w-full h-14 rounded-2xl text-base font-medium transition-all",
            isValid ? "bg-primary hover:bg-primary/90 text-primary-foreground" : "bg-secondary text-muted-foreground",
            "disabled:opacity-40 disabled:cursor-not-allowed",
          )}
        >
          continue
        </Button>
      </form>
    </div>
  )
}
