const withBundleAnalyzer = require("@next/bundle-analyzer")({
    enabled: process.env.ANALYZE === "true",
});

/** @type {import('next').NextConfig} */
const nextConfig = {
    experimental: {
        typedRoutes: true,
    },
    images: {
        remotePatterns: [
            // Twitter / X
            { protocol: "https", hostname: "pbs.twimg.com" },
            { protocol: "https", hostname: "video.twimg.com" },
            // Instagram
            { protocol: "https", hostname: "*.cdninstagram.com" },
            { protocol: "https", hostname: "*.instagram.com" },
            // TikTok
            { protocol: "https", hostname: "*.tiktokcdn.com" },
            { protocol: "https", hostname: "*.tiktokcdn-us.com" },
            { protocol: "https", hostname: "*.tiktok.com" },
            // Facebook
            { protocol: "https", hostname: "*.fbcdn.net" },
            { protocol: "https", hostname: "*.facebook.com" },
            // YouTube
            { protocol: "https", hostname: "i.ytimg.com" },
            { protocol: "https", hostname: "*.ytimg.com" },
            { protocol: "https", hostname: "img.youtube.com" },
        ],
    },
};

module.exports = withBundleAnalyzer(nextConfig);
