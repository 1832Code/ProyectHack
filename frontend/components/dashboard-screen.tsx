"use client"

import Link from "next/link"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { useEffect, useState, useCallback, useRef } from "react"

const ArrowLeftIcon = ({ className }: { className?: string }) => (
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
    className={className}
  >
    <path d="m12 19-7-7 7-7" />
    <path d="M19 12H5" />
  </svg>
)

const Loader2Icon = ({ className }: { className?: string }) => (
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
    className={cn("animate-spin", className)}
  >
    <path d="M21 12a9 9 0 1 1-6.219-8.56" />
  </svg>
)

const PlatformIcons = {
  youtube: (
    <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current">
      <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93-.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
    </svg>
  ),
  tiktok: (
    <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current">
      <path d="M12.525.02c1.31-.02 2.61-.012 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z" />
    </svg>
  ),
  instagram: (
    <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current">
      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.057-1.644.07-4.849.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.073-1.689-.073-4.948 0-3.205.012-3.583.072-4.948.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
    </svg>
  ),
  x: (
    <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  ),
  facebook: (
    <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current">
      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
    </svg>
  ),
  article: (
    <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current">
      <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" />
    </svg>
  ),
}

const allMentions = [
  {
    id: 1,
    platform: "tiktok" as const,
    username: "@delivery_fails",
    avatar: "/tiktok-user-avatar.jpg",
    content: "POV: When Rappi says 10 minutes but you've been waiting 45 #rappi #delivery #peru",
    engagement: "245k views",
    time: "2h",
    sentiment: "negative" as const,
  },
  {
    id: 2,
    platform: "instagram" as const,
    username: "@foodie_lima",
    avatar: "/instagram-food-blogger.jpg",
    content: "Tried the new RappiPrime and it's worth every penny. Unlimited free shipping and great deals",
    engagement: "1.2k likes",
    time: "3h",
    sentiment: "positive" as const,
  },
  {
    id: 3,
    platform: "youtube" as const,
    username: "Tech Review Peru",
    avatar: "/youtube-tech-channel-logo.jpg",
    content: "Full comparison: Rappi vs PedidosYa vs DiDi Food - Which is better in 2024? | Complete Review",
    engagement: "89k views",
    time: "5h",
    sentiment: "neutral" as const,
  },
  {
    id: 4,
    platform: "x" as const,
    username: "@carlosm_pe",
    avatar: "/male-twitter-user.jpg",
    content: "The Rappi app is getting slower every day. Anyone else having issues? Can't even order properly.",
    engagement: "342 retweets",
    time: "6h",
    sentiment: "negative" as const,
  },
  {
    id: 5,
    platform: "article" as const,
    username: "El Comercio",
    avatar: "/peruvian-newspaper-logo.jpg",
    content: "Rappi announces expansion to 5 new cities in Peru and promises 2,000 new jobs for delivery drivers",
    engagement: "Economy",
    time: "8h",
    sentiment: "positive" as const,
  },
  {
    id: 6,
    platform: "facebook" as const,
    username: "Lima Deals",
    avatar: "/deals-group-logo.jpg",
    content: "RAPPI DISCOUNT CODE: Use 'SAVE30' for 30% off your next order. Valid until tomorrow!",
    engagement: "2.3k shares",
    time: "10h",
    sentiment: "positive" as const,
  },
  {
    id: 7,
    platform: "tiktok" as const,
    username: "@delivery_official",
    avatar: "/delivery-person.png",
    content: "A normal day as a Rappi delivery driver in Lima. Life of a rappitendero #rappi #work",
    engagement: "567k views",
    time: "12h",
    sentiment: "neutral" as const,
  },
  {
    id: 8,
    platform: "instagram" as const,
    username: "@peruvian_restaurant",
    avatar: "/peruvian-restaurant-logo.jpg",
    content: "We're now on Rappi! Order your favorite ceviche with free delivery this week. Link in bio",
    engagement: "856 likes",
    time: "14h",
    sentiment: "positive" as const,
  },
  {
    id: 9,
    platform: "x" as const,
    username: "@startup_latam",
    avatar: "/startup-news-logo.jpg",
    content: "Rappi reports 40% growth in Peru during Q3. The delivery market continues to expand in the region.",
    engagement: "189 likes",
    time: "16h",
    sentiment: "positive" as const,
  },
  {
    id: 10,
    platform: "youtube" as const,
    username: "3 Pepitos Podcast",
    avatar: "/podcast-microphone-logo.jpg",
    content: "Ep. 234: We discuss the delivery app war in Peru. Rappi, PedidosYa and the new players",
    engagement: "12k views",
    time: "1d",
    sentiment: "neutral" as const,
  },
  {
    id: 11,
    platform: "article" as const,
    username: "Gestion",
    avatar: "/business-newspaper-logo.jpg",
    content: "Rappi launches RappiBank in Peru: Credit card with cashback on all orders",
    engagement: "Finance",
    time: "1d",
    sentiment: "positive" as const,
  },
  {
    id: 12,
    platform: "facebook" as const,
    username: "Delivery Complaints Peru",
    avatar: "/complaint-group.jpg",
    content:
      "Watch out for Rappi, they charged me twice and support hasn't responded in 3 days. Anyone know how to file a claim?",
    engagement: "456 comments",
    time: "1d",
    sentiment: "negative" as const,
  },
  {
    id: 13,
    platform: "instagram" as const,
    username: "@influencer_peru",
    avatar: "/female-influencer.png",
    content: "My experience with RappiTravel was amazing. Booked hotel and flight all from the app! Highly recommended",
    engagement: "3.4k likes",
    time: "1d",
    sentiment: "positive" as const,
  },
  {
    id: 14,
    platform: "tiktok" as const,
    username: "@viral_food",
    avatar: "/food-viral-tiktok.jpg",
    content: "This restaurant is only on Rappi and has the best burger in Lima #foodtiktok #rappi #lima",
    engagement: "892k views",
    time: "2d",
    sentiment: "positive" as const,
  },
  {
    id: 15,
    platform: "x" as const,
    username: "@techbro_lima",
    avatar: "/tech-guy-avatar.jpg",
    content: "Rappi's real-time tracking is better than any other app. Facts.",
    engagement: "78 likes",
    time: "2d",
    sentiment: "positive" as const,
  },
  {
    id: 16,
    platform: "youtube" as const,
    username: "Finance For Everyone",
    avatar: "/finance-youtube-channel.jpg",
    content: "Is RappiPay worth it? Complete analysis of Rappi's digital wallet in Peru",
    engagement: "45k views",
    time: "2d",
    sentiment: "neutral" as const,
  },
  {
    id: 17,
    platform: "facebook" as const,
    username: "Miraflores Neighbors",
    avatar: "/neighborhood-group.jpg",
    content: "Rappi delivery drivers are driving too fast in the area. Watch out for the kids!",
    engagement: "234 comments",
    time: "2d",
    sentiment: "negative" as const,
  },
  {
    id: 18,
    platform: "article" as const,
    username: "Peru21",
    avatar: "/peru-news-logo.jpg",
    content: "Rappi and the Ministry of Labor sign agreement to improve conditions for delivery drivers",
    engagement: "Politics",
    time: "3d",
    sentiment: "positive" as const,
  },
  {
    id: 19,
    platform: "instagram" as const,
    username: "@newmom",
    avatar: "/mom-blogger.jpg",
    content: "With Rappi I can order diapers and food without leaving home. Lifesaver for new moms",
    engagement: "2.1k likes",
    time: "3d",
    sentiment: "positive" as const,
  },
  {
    id: 20,
    platform: "tiktok" as const,
    username: "@peruvian_humor",
    avatar: "/comedy-tiktok.jpg",
    content: "When the Rappi driver calls but you don't know where your own house is #humor #rappi",
    engagement: "1.2M views",
    time: "3d",
    sentiment: "neutral" as const,
  },
  {
    id: 21,
    platform: "x" as const,
    username: "@digital_journalist",
    avatar: "/placeholder.svg?height=40&width=40",
    content: "Rappi introduces artificial intelligence to predict delivery times with greater accuracy.",
    engagement: "445 retweets",
    time: "3d",
    sentiment: "positive" as const,
  },
  {
    id: 22,
    platform: "facebook" as const,
    username: "Peru Entrepreneurs",
    avatar: "/placeholder.svg?height=40&width=40",
    content: "Has anyone had success selling through Rappi? I want to add my dessert business",
    engagement: "89 comments",
    time: "4d",
    sentiment: "neutral" as const,
  },
  {
    id: 23,
    platform: "youtube" as const,
    username: "Vlog Lima",
    avatar: "/placeholder.svg?height=40&width=40",
    content: "24 HOURS eating ONLY from RAPPI - How much did I spend? The result will surprise you",
    engagement: "156k views",
    time: "4d",
    sentiment: "neutral" as const,
  },
  {
    id: 24,
    platform: "instagram" as const,
    username: "@peruvian_chef",
    avatar: "/placeholder.svg?height=40&width=40",
    content: "Partnership with Rappi to bring authentic Peruvian food to all of Lima. Coming soon!",
    engagement: "5.6k likes",
    time: "4d",
    sentiment: "positive" as const,
  },
  {
    id: 25,
    platform: "article" as const,
    username: "La Republica",
    avatar: "/placeholder.svg?height=40&width=40",
    content: "Rappi surpasses 2 million active users in Peru according to latest quarterly report",
    engagement: "Technology",
    time: "5d",
    sentiment: "positive" as const,
  },
  {
    id: 26,
    platform: "tiktok" as const,
    username: "@uni_student",
    avatar: "/placeholder.svg?height=40&width=40",
    content: "Rappi has a student discount and nobody talks about it! Code: UNI2024 #rappi #students",
    engagement: "234k views",
    time: "5d",
    sentiment: "positive" as const,
  },
  {
    id: 27,
    platform: "x" as const,
    username: "@consumer_rights",
    avatar: "/placeholder.svg?height=40&width=40",
    content: "Indecopi opens investigation into Rappi for alleged improper charges. Pending results.",
    engagement: "1.2k retweets",
    time: "5d",
    sentiment: "negative" as const,
  },
  {
    id: 28,
    platform: "facebook" as const,
    username: "San Isidro Foodies",
    avatar: "/placeholder.svg?height=40&width=40",
    content: "The best restaurants in San Isidro that are ONLY on Rappi. Thread",
    engagement: "567 reactions",
    time: "6d",
    sentiment: "positive" as const,
  },
  {
    id: 29,
    platform: "instagram" as const,
    username: "@fitness_lima",
    avatar: "/placeholder.svg?height=40&width=40",
    content: "Rappi now has a healthy food category! Finally I can order my bowls guilt-free",
    engagement: "1.8k likes",
    time: "6d",
    sentiment: "positive" as const,
  },
  {
    id: 30,
    platform: "youtube" as const,
    username: "Easy Economics",
    avatar: "/placeholder.svg?height=40&width=40",
    content: "Rappi's business model explained: How does this Colombian startup make money?",
    engagement: "78k views",
    time: "1w",
    sentiment: "neutral" as const,
  },
]

const platformColors = {
  youtube: "text-[#ff4444] bg-[#fff0f0]",
  tiktok: "text-foreground bg-secondary",
  instagram: "text-[#e1306c] bg-[#fff0f5]",
  x: "text-foreground bg-secondary",
  facebook: "text-[#1877f2] bg-[#f0f5ff]",
  article: "text-primary bg-primary/10",
}

const sentimentColors = {
  positive: "bg-primary/15 text-primary",
  negative: "bg-destructive/15 text-destructive",
  neutral: "bg-muted text-muted-foreground",
}

export function DashboardScreen() {
  const [isSticky, setIsSticky] = useState(false)
  const [displayedMentions, setDisplayedMentions] = useState(allMentions.slice(0, 5))
  const [isLoading, setIsLoading] = useState(false)
  const [hasMore, setHasMore] = useState(true)
  const loaderRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleScroll = () => {
      setIsSticky(window.scrollY > 120)
    }
    window.addEventListener("scroll", handleScroll, { passive: true })
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const loadMore = useCallback(() => {
    if (isLoading || !hasMore) return

    setIsLoading(true)

    setTimeout(() => {
      const currentLength = displayedMentions.length
      const nextItems = allMentions.slice(currentLength, currentLength + 5)

      if (nextItems.length === 0) {
        setHasMore(false)
      } else {
        setDisplayedMentions((prev) => [...prev, ...nextItems])
      }
      setIsLoading(false)
    }, 800)
  }, [displayedMentions.length, isLoading, hasMore])

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !isLoading) {
          loadMore()
        }
      },
      { threshold: 0.1 },
    )

    if (loaderRef.current) {
      observer.observe(loaderRef.current)
    }

    return () => observer.disconnect()
  }, [loadMore, hasMore, isLoading])

  return (
    <div className="min-h-screen bg-background">
      <div
        className={cn(
          "sticky top-0 z-50 transition-all duration-300 flex justify-center",
          isSticky ? "pt-4 px-4" : "px-5 pt-6 pb-0",
        )}
      >
        <div
          className={cn(
            "transition-all duration-300",
            isSticky
              ? "py-2 px-4 bg-background/80 backdrop-blur-xl rounded-full border border-border/50 shadow-lg w-fit"
              : "w-full bg-background",
          )}
        >
          <div
            className={cn(
              "transition-all duration-300 overflow-hidden",
              isSticky ? "h-0 opacity-0 mb-0" : "h-auto opacity-100 mb-5",
            )}
          >
            <Button
              variant="secondary"
              size="sm"
              asChild
              className="bg-card hover:bg-secondary text-muted-foreground hover:text-foreground rounded-full px-3"
            >
              <Link href="/buscar">
                <ArrowLeftIcon className="w-4 h-4 mr-1" />
                New search
              </Link>
            </Button>
          </div>

          <header
            className={cn(
              "flex items-center transition-all duration-300",
              isSticky ? "justify-center gap-2" : "gap-3 mb-5",
            )}
          >
            <div className="flex items-center gap-2">
              <Button
                variant="secondary"
                size="icon"
                asChild
                className={cn(
                  "bg-card hover:bg-secondary text-muted-foreground hover:text-foreground transition-all duration-300 rounded-full",
                  isSticky ? "w-7 h-7 opacity-100" : "w-0 h-0 opacity-0 overflow-hidden",
                )}
              >
                <Link href="/buscar">
                  <ArrowLeftIcon className="w-4 h-4" />
                </Link>
              </Button>
              <Avatar
                className={cn(
                  "ring-2 ring-primary/30 transition-all duration-300",
                  isSticky ? "h-7 w-7 rounded-full" : "h-12 w-12 rounded-2xl",
                )}
              >
                <AvatarImage src="/rappi-logo.png" alt="Rappi" />
                <AvatarFallback
                  className={cn(
                    "bg-primary/10 text-primary font-semibold transition-all duration-300",
                    isSticky ? "rounded-full text-xs" : "rounded-2xl text-base",
                  )}
                >
                  RA
                </AvatarFallback>
              </Avatar>
              <div
                className={cn(
                  "flex items-center gap-3 transition-all duration-300",
                  isSticky ? "opacity-100 ml-2" : "opacity-0 w-0 overflow-hidden",
                )}
              >
                <div className="h-4 w-px bg-border" />
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1.5">
                    <span className="text-sm font-bold text-foreground">32k</span>
                    <span className="text-xs text-primary">↑2%</span>
                  </div>
                  <div className="h-3 w-px bg-border" />
                  <div className="flex items-center gap-1.5">
                    <span className="text-sm font-bold text-foreground">89%</span>
                    <span className="text-xs text-primary">↑12%</span>
                  </div>
                </div>
              </div>
              <div className={cn("transition-all duration-300", isSticky ? "hidden" : "block")}>
                <h1 className="text-xl font-bold text-foreground font-serif italic">Rappi</h1>
                <p className="text-sm text-muted-foreground">Peru · Sep 20th</p>
              </div>
            </div>
          </header>
        </div>
      </div>

      <div className="px-5 pt-5">
        <div className="grid grid-cols-2 gap-3 mb-8">
          <Card className="border-0 bg-card rounded-2xl">
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground mb-1 italic">mentions</p>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-foreground font-serif">32k</span>
                <span className="text-sm text-primary font-medium">↑2%</span>
              </div>
            </CardContent>
          </Card>
          <Card className="border-0 bg-card rounded-2xl">
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground mb-1 italic">approval</p>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-foreground font-serif">89%</span>
                <span className="text-sm text-primary font-medium">↑12%</span>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="mb-8">
          <p className="text-sm text-muted-foreground mb-3 italic">sentiment</p>
          <Card className="border-0 bg-card rounded-2xl">
            <CardContent className="p-4">
              <svg viewBox="0 0 300 48" className="w-full h-12">
                <path
                  d="M0,40 Q30,38 60,32 T120,28 T180,20 T240,16 T300,8"
                  fill="none"
                  stroke="oklch(0.55 0.22 280)"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>
            </CardContent>
          </Card>
        </div>

        <div className="mb-8">
          <div className="flex flex-wrap gap-2">
            {["chicken", "stale", "bad service", "scam"].map((tag) => (
              <Badge
                key={tag}
                variant="outline"
                className="px-4 py-2 text-sm font-normal rounded-full border-border bg-background text-foreground hover:bg-secondary cursor-pointer transition-colors"
              >
                {tag}
              </Badge>
            ))}
          </div>
        </div>

        <div className="mb-8">
          <p className="text-base text-foreground mb-4 italic font-serif">talking now</p>
          <div className="flex flex-col gap-2">
            <Card className="border-0 bg-card rounded-xl">
              <CardContent className="p-3 flex items-center justify-between">
                <span className="text-sm font-medium text-foreground">Complaints about Pios Chicken</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">+200 i</span>
                  <div className="p-1.5 rounded-lg bg-[#fff0f5]">{PlatformIcons.instagram}</div>
                </div>
              </CardContent>
            </Card>
            <Card className="border-0 bg-card rounded-xl">
              <CardContent className="p-3 flex items-center justify-between">
                <span className="text-sm font-medium text-foreground">Talk about stale chicken in Lima</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">+20 i</span>
                  <div className="p-1.5 rounded-lg bg-secondary border border-border">{PlatformIcons.tiktok}</div>
                </div>
              </CardContent>
            </Card>
          </div>
          <button className="w-full text-center text-sm text-muted-foreground mt-3 hover:text-primary transition-colors">
            see all
          </button>
        </div>

        <section className="pb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base text-foreground font-serif italic">Social mentions</h2>
            <span className="text-sm text-muted-foreground">{allMentions.length} total</span>
          </div>

          <div className="flex flex-col gap-3">
            {displayedMentions.map((mention) => (
              <Card key={mention.id} className="border-0 bg-card rounded-2xl overflow-hidden">
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div className={cn("p-2 rounded-xl shrink-0", platformColors[mention.platform])}>
                      {PlatformIcons[mention.platform]}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <span className="text-sm font-medium text-foreground truncate">{mention.username}</span>
                        <span className="text-xs text-muted-foreground shrink-0">{mention.time}</span>
                      </div>
                      <p className="text-sm text-muted-foreground leading-relaxed line-clamp-2 mb-2">
                        {mention.content}
                      </p>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">{mention.engagement}</span>
                        <Badge
                          variant="secondary"
                          className={cn(
                            "text-xs font-normal px-2 py-0.5 rounded-full",
                            sentimentColors[mention.sentiment],
                          )}
                        >
                          {mention.sentiment === "positive"
                            ? "Positive"
                            : mention.sentiment === "negative"
                              ? "Negative"
                              : "Neutral"}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div ref={loaderRef} className="flex justify-center py-6">
            {isLoading && (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2Icon className="w-5 h-5" />
                <span className="text-sm">Loading more mentions...</span>
              </div>
            )}
            {!hasMore && displayedMentions.length > 0 && (
              <p className="text-sm text-muted-foreground">No more mentions</p>
            )}
          </div>

          <div className="mt-2">
            <Button className="w-full h-14 rounded-2xl bg-primary hover:bg-primary/90 text-primary-foreground text-base font-medium">
              Generate report
            </Button>
          </div>
        </section>
      </div>
    </div>
  )
}
