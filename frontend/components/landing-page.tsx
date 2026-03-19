"use client";

import Link from "next/link";
import { useDownload } from "@/hooks/use-download";
import { UrlInput } from "@/components/url-input";
import { ResultCard } from "@/components/result-card";
import { SkeletonResult } from "@/components/skeleton-result";
import { PlatformIcon } from "@/components/platform-icon";
import { ThemeToggle } from "@/components/theme-toggle";
import { useKeyboardShortcuts } from "@/hooks/use-keyboard-shortcuts";
import { ErrorCard } from "@/components/error-card";
import type { Platform } from "@/types";

const PLATFORMS: Platform[] = [
    "tiktok",
    "instagram",
    "youtube",
    "twitter",
    "facebook",
    "threads",
];

export function LandingPage() {
    const { status, result, error, platform, errorCode, processUrl, reset } = useDownload();

    useKeyboardShortcuts({
        onPaste: processUrl,
        onCancel: reset,
        isLoading: status === "loading",
        canCancel: status !== "idle",
    });

    return (
        <div className="min-h-screen bg-background flex flex-col">
            <header className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md">
                <div className="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">
                    <span className="text-base font-bold tracking-tight text-foreground">
                        Copas<span className="text-amber-500">.io</span>
                    </span>
                    <div className="flex items-center gap-3">
                        <Link
                            href="/faq"
                            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                        >
                            FAQ
                        </Link>
                        <ThemeToggle />
                    </div>
                </div>
            </header>

            <main className="flex-1 flex flex-col items-center px-4 pt-24 pb-16">
                <div className="text-center mb-10">
                    <div className="text-xs font-semibold uppercase tracking-widest text-amber-500 mb-4">
                        Downloader Serba Bisa
                    </div>
                    <h1 className="text-5xl md:text-6xl font-black tracking-tighter text-foreground leading-none mb-4">
                        Copas<span className="text-amber-500">.</span>io
                    </h1>
                    <p className="text-base text-muted-foreground max-w-md mx-auto leading-relaxed">
                        Copas link dari TikTok, Instagram, YouTube, X, Facebook,
                        atau Threads — kami urus sisanya.
                    </p>
                </div>

                <div className="w-full max-w-2xl mx-auto">
                    <UrlInput
                        onSubmit={processUrl}
                        isLoading={status === "loading"}
                        onReset={reset}
                    />

                    <p className="mt-2 text-center text-xs text-muted-foreground">
                        Tip: Tekan Ctrl+V/Cmd+V untuk tempel, Esc untuk batal
                    </p>

                    <div className="mt-5 flex items-center gap-3 justify-center">
                        <span className="text-xs text-muted-foreground">Mendukung</span>
                        {PLATFORMS.map((platform) => (
                            <PlatformIcon
                                key={platform}
                                platform={platform}
                                size={14}
                                className="text-muted-foreground"
                                useColor={false}
                            />
                        ))}
                    </div>
                </div>

                {error && (
                    <div className="mt-6 w-full max-w-2xl mx-auto">
                        <ErrorCard error={error} onRetry={reset} platform={platform} errorCode={errorCode ?? undefined} />
                    </div>
                )}

                <div className="mt-8 w-full max-w-2xl mx-auto">
                    {status === "loading" && <SkeletonResult />}
                    {status === "success" && result && (
                        <ResultCard result={result} onDismiss={reset} />
                    )}
                </div>
            </main>

            <footer className="border-t border-border py-5 text-center text-xs text-muted-foreground">
                Copas.io — Hanya untuk penggunaan pribadi. Hormati hak cipta
                konten kreator.
            </footer>
        </div>
    );
}
