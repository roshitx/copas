"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { Clock } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import { HistoryDrawer } from "@/components/history-drawer";
import { Button } from "@/components/ui/button";

const NAV_LINKS = [
    { href: "/faq", label: "FAQ" },
    { href: "/about", label: "Tentang" },
] as const;

interface SiteHeaderProps {
    onHistorySelect?: (url: string) => void;
}

export function SiteHeader({ onHistorySelect }: SiteHeaderProps) {
    const pathname = usePathname();
    const router = useRouter();
    const [historyOpen, setHistoryOpen] = useState(false);

    const handleHistorySelect = (url: string) => {
        setHistoryOpen(false);
        if (onHistorySelect) {
            onHistorySelect(url);
        } else {
            router.push(`/?url=${encodeURIComponent(url)}`);
        }
    };

    return (
        <>
            <header className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md">
                <div className="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">
                    <Link
                        href="/"
                        className="text-base font-bold tracking-tight text-foreground transition-colors hover:text-foreground/80"
                    >
                        Copas<span className="text-amber-500">.io</span>
                    </Link>

                    <div className="flex items-center gap-2">
                        {/* Pill nav */}
                        <nav
                            className="flex items-center rounded-full bg-muted/60 p-1 gap-0.5"
                            aria-label="Navigasi utama"
                        >
                            {NAV_LINKS.map(({ href, label }) => {
                                const isActive = pathname === href;
                                return (
                                    <Link
                                        key={href}
                                        href={href}
                                        className={`rounded-full px-3 py-1.5 text-sm font-medium transition-all duration-150 ${
                                            isActive
                                                ? "bg-background text-foreground shadow-sm"
                                                : "text-muted-foreground hover:text-foreground"
                                        }`}
                                    >
                                        {label}
                                    </Link>
                                );
                            })}
                        </nav>

                        {/* Separator */}
                        <div className="h-5 w-px bg-border mx-1" aria-hidden />

                        {/* Action buttons */}
                        <Button
                            variant="ghost"
                            size="icon"
                            className="h-9 w-9 text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
                            aria-label="Riwayat download"
                            title="Riwayat download"
                            onClick={() => setHistoryOpen(true)}
                        >
                            <Clock className="h-4 w-4" />
                        </Button>

                        <ThemeToggle />
                    </div>
                </div>
            </header>

            <HistoryDrawer
                open={historyOpen}
                onOpenChange={setHistoryOpen}
                onSelect={handleHistorySelect}
            />
        </>
    );
}
