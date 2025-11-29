import type React from "react"
import type { Metadata, Viewport } from "next"
import { Plus_Jakarta_Sans, Source_Serif_4 } from "next/font/google"
import "./globals.css"

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-jakarta",
})

const sourceSerif = Source_Serif_4({
  subsets: ["latin"],
  variable: "--font-source-serif",
})

export const metadata: Metadata = {
  title: "Señal | Inteligencia de mercado",
  description: "Detecta señales del mercado antes que tu competencia.",
    generator: 'v0.app'
}

export const viewport: Viewport = {
  themeColor: "#faf8f5",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="es">
      <body className={`${jakarta.className} ${sourceSerif.variable} font-sans`}>{children}</body>
    </html>
  )
}
