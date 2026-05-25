/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'api.skoutmarketplace.com' },
      { protocol: 'http', hostname: 'localhost' },
    ],
  },
}

module.exports = nextConfig
