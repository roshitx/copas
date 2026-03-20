import type { Metadata } from "next";
import { LandingPage } from "@/components/landing-page";

export const metadata: Metadata = {
    title: "Copas.io | Download Media dari Semua Platform",
    description:
        "Download video, audio, dan gambar dari TikTok, Instagram, YouTube, X, Facebook, dan Threads. Gratis, tanpa login, tanpa watermark.",
    keywords: [
        "download video tiktok",
        "download instagram",
        "youtube downloader",
        "social media downloader",
        "copas.io",
    ],
    openGraph: {
        title: "Copas.io | Social Media Downloader",
        description:
            "Download dari TikTok, Instagram, YouTube, X, Facebook, Threads. Gratis.",
        type: "website",
    },
};

export default function Page() {
    return <LandingPage />;
}
