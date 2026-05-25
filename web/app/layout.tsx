import type { Metadata } from 'next'
import './globals.css'
import { AuthProvider } from '@/contexts/AuthContext'

export const metadata: Metadata = {
  title: 'Skout Marketplace — AI-Powered Influencer Discovery',
  description: 'Find the right creators for your brand using AI. Discover, filter, and connect with influencers that match your campaign goals.',
  metadataBase: new URL('https://skoutmarketplace.com'),
  openGraph: {
    title: 'Skout Marketplace',
    description: 'AI-powered influencer discovery platform',
    siteName: 'Skout Marketplace',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  )
}
