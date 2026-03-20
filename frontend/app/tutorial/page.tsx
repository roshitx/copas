import type { Metadata } from "next";
import Link from "next/link";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
    title: "Tutorial Download | Copas.io",
    description:
        "Panduan lengkap cara download video dan konten dari berbagai platform media sosial menggunakan Copas.io.",
};

const TUTORIALS = [
    {
        platform: "TikTok",
        href: "/tutorial/tiktok",
        description: "Download video TikTok tanpa watermark",
    },
    {
        platform: "Instagram",
        href: "/tutorial/instagram",
        description: "Download foto, video, Reels, dan Story Instagram",
    },
    {
        platform: "YouTube",
        href: "/tutorial/youtube",
        description: "Download video YouTube dalam berbagai kualitas",
    },
    {
        platform: "X (Twitter)",
        href: "/tutorial/twitter",
        description: "Download video dan gambar dari X / Twitter",
    },
    {
        platform: "Facebook",
        href: "/tutorial/facebook",
        description: "Download video Facebook publik",
    },
    {
        platform: "Threads",
        href: "/tutorial/threads",
        description: "Download foto dan video dari Threads",
    },
] as const;

export default function TutorialHub() {
    return (
        <div className="min-h-screen bg-background flex flex-col">
            <SiteHeader />
            <main className="flex-1 px-4 py-10 md:py-14">
                <div className="mx-auto w-full max-w-3xl space-y-10">
                    <div className="space-y-3">
                        <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-foreground">
                            Tutorial Download
                        </h1>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Pilih platform di bawah untuk melihat panduan
                            langkah demi langkah cara download konten
                            menggunakan Copas.io.
                        </p>
                    </div>

                    <div className="grid gap-4 sm:grid-cols-2">
                        {TUTORIALS.map(({ platform, href, description }) => (
                            <Link
                                key={href}
                                href={href}
                                className="group rounded-xl border border-border bg-card p-5 transition-colors hover:border-amber-500/40 hover:bg-card/80"
                            >
                                <h2 className="text-lg font-semibold text-foreground group-hover:text-amber-500 transition-colors">
                                    {platform}
                                </h2>
                                <p className="mt-1 text-sm text-muted-foreground">
                                    {description}
                                </p>
                            </Link>
                        ))}
                    </div>
                </div>
            </main>
            <SiteFooter />
        </div>
    );
}
