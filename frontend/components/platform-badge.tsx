"use client";
import type { Platform } from "@/types";
import { PLATFORM_LABELS } from "@/lib/platform-detector";
import { PlatformIcon } from "@/components/platform-icon";

interface PlatformBadgeProps {
    platform: Platform;
    className?: string;
}

export function PlatformBadge({ platform, className }: PlatformBadgeProps) {
    if (platform === "unknown") return null;
    return (
        <div
            className={`inline-flex items-center gap-1.5 rounded-full border border-zinc-700/50 bg-zinc-800/80 px-2.5 py-1 text-xs font-medium text-zinc-300 animate-in fade-in duration-200 ${className ?? ""}`}
        >
            <PlatformIcon platform={platform} size={11} useColor={true} />
            {PLATFORM_LABELS[platform]}
        </div>
    );
}
