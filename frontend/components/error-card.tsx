"use client";

import { AlertCircle, RefreshCw, MessageSquareWarning } from "lucide-react";
import type { Platform } from "@/types";
import {
  getPlatformErrorMessage,
  getPlatformErrorConfig,
} from "@/lib/error-messages";
import { PlatformBadge } from "@/components/platform-badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ErrorCardProps {
  error: string | null | undefined;
  onRetry?: () => void;
  className?: string;
  platform?: Platform;
  errorCode?: string;
}

export function ErrorCard({
  error,
  onRetry,
  className,
  platform,
  errorCode,
}: ErrorCardProps) {
  if (!error) return null;

  const handleRetry = () => {
    onRetry?.();
    // Focus the URL input after a short delay to allow state reset
    setTimeout(() => {
      const urlInput = document.querySelector(
        'input[type="text"][inputmode="url"]'
      ) as HTMLInputElement | null;
      urlInput?.focus();
    }, 0);
  };

  const mailtoLink = `mailto:auliarasyidalzahrawi@gmail.com?subject=${encodeURIComponent(
    "[Copas.io] Laporan Error"
  )}&body=${encodeURIComponent(
    `Halo tim Copas.io,\n\nSaya mengalami error saat menggunakan layanan:\n\n${error}\n\nURL yang saya coba: ${
      typeof window !== "undefined" ? window.location.href : ""
    }\n\nTerima kasih.`
  )}`;

  // Get platform-specific content if platform is provided
  const hasPlatformContext = platform && platform !== "unknown";
  const platformConfig = hasPlatformContext
    ? getPlatformErrorConfig(platform)
    : null;
  const contextualMessage = hasPlatformContext
    ? getPlatformErrorMessage(platform, errorCode)
    : null;
  const suggestedActions = platformConfig?.suggestedActions.slice(0, 3) ?? [];

  return (
    <Card
      role="alert"
      aria-live="polite"
      className={cn(
        "border-destructive/50 bg-destructive/10 text-destructive dark:bg-destructive/10",
        className
      )}
    >
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <AlertCircle className="h-5 w-5 text-destructive" aria-hidden="true" />
          <CardTitle className="text-base font-semibold text-destructive">
            Terjadi Kesalahan
          </CardTitle>
        </div>
        <CardDescription className="text-destructive/80">
          Maaf, kami tidak dapat memproses permintaan Anda saat ini.
        </CardDescription>
      </CardHeader>

      <CardContent className="pb-4 space-y-4">
        {/* Platform context section */}
        {hasPlatformContext && platformConfig && (
          <div className="space-y-3">
            {/* Platform badge */}
            <div className="flex items-center gap-2">
              <PlatformBadge platform={platform} />
            </div>

            {/* Contextual message */}
            {contextualMessage && (
              <p className="text-sm font-medium text-amber-400/90">
                {contextualMessage}
              </p>
            )}

            {/* Divider */}
            <div className="border-t border-destructive/20" />
          </div>
        )}

        {/* Generic error message */}
        <p className="text-sm font-medium text-zinc-300">{error}</p>

        {/* Suggested actions */}
        {suggestedActions.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs font-medium text-zinc-400">
              Saran tindakan:
            </p>
            <ul className="space-y-1.5">
              {suggestedActions.map((action, index) => (
                <li
                  key={index}
                  className="flex items-start gap-2 text-xs text-zinc-400"
                >
                  <span className="mt-0.5 h-1 w-1 rounded-full bg-zinc-400" aria-hidden="true" />
                  <span>{action}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>

      <CardFooter className="flex items-center justify-between gap-3 pt-0">
        <a
          href={mailtoLink}
          className="inline-flex items-center gap-1.5 text-xs text-destructive/70 hover:text-destructive transition-colors"
          target="_blank"
          rel="noopener noreferrer"
        >
          <MessageSquareWarning className="h-3.5 w-3.5" aria-hidden="true" />
          Laporkan masalah
        </a>
        {onRetry && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleRetry}
            className="border-destructive/30 bg-destructive/5 text-destructive hover:bg-destructive/10 hover:text-destructive"
          >
            <RefreshCw className="mr-1.5 h-3.5 w-3.5" aria-hidden="true" />
            Coba lagi
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
