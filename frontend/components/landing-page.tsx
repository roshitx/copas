"use client";

import dynamic from "next/dynamic";
import { useDownload } from "@/hooks/use-download";
import { UrlInput } from "@/components/url-input";
import { SkeletonResult } from "@/components/skeleton-result";
import { PlatformIcon } from "@/components/platform-icon";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import { useKeyboardShortcuts } from "@/hooks/use-keyboard-shortcuts";
import { ErrorCard } from "@/components/error-card";
import { SUPPORTED_PLATFORMS } from "@/lib/constants";

const ResultCard = dynamic(
    () =>
        import("@/components/result-card").then((m) => ({
            default: m.ResultCard,
        })),
    { ssr: false, loading: () => <SkeletonResult /> },
);

export function LandingPage() {
    const { status, result, error, platform, errorCode, processUrl, reset } = useDownload();

    useKeyboardShortcuts({
        onPaste: processUrl,
        onCancel: reset,
        isLoading: status === "loading",
        canCancel: status !== "idle",
    });

    return (
        <div className="flex flex-col bg-background">
            <SiteHeader onHistorySelect={processUrl} />

            <main className="min-h-[calc(100vh-3.5rem)] flex flex-col items-center justify-center px-4 py-16">
                <div className="w-full max-w-2xl mx-auto flex flex-col items-center gap-5">
                    <div className="text-center space-y-3">
                        <div className="text-xs font-semibold uppercase tracking-widest text-amber-500">
                            Downloader Serba Bisa
                        </div>
                        <h1 className="text-5xl md:text-6xl font-black tracking-tighter text-foreground leading-none">
                            Copas<span className="text-amber-500">.</span>io
                        </h1>
                        <p className="text-base text-muted-foreground max-w-md mx-auto leading-relaxed">
                            Copas link dari TikTok, Instagram, YouTube, X, Facebook,
                            atau Threads. Sisanya kami yang urus.
                        </p>
                    </div>

                    <div className="w-full">
                        <UrlInput
                            onSubmit={processUrl}
                            isLoading={status === "loading"}
                            onReset={reset}
                        />
                    </div>

                    <div className="flex items-center gap-3">
                        {SUPPORTED_PLATFORMS.map((platform) => (
                            <PlatformIcon
                                key={platform}
                                platform={platform}
                                size={13}
                                className="text-muted-foreground/50"
                                useColor={false}
                            />
                        ))}
                    </div>

                    {error && (
                        <div className="w-full">
                            <ErrorCard error={error} onRetry={reset} platform={platform} errorCode={errorCode ?? undefined} />
                        </div>
                    )}

                    {(status === "loading" || (status === "success" && result)) && (
                        <div className="w-full">
                            {status === "loading" && <SkeletonResult />}
                            {status === "success" && result && (
                                <ResultCard result={result} onDismiss={reset} />
                            )}
                        </div>
                    )}
                </div>
            </main>

            <SiteFooter />
        </div>
    );
}
