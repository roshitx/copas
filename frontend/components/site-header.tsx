"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ThemeToggle } from "@/components/theme-toggle";

const NAV_LINKS = [
    { href: "/faq", label: "FAQ" },
    { href: "/about", label: "Tentang" },
] as const;

export function SiteHeader() {
    const pathname = usePathname();

    return (
        <header className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md">
            <div className="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">
                <Link
                    href="/"
                    className="text-base font-bold tracking-tight text-foreground transition-colors hover:text-foreground/80"
                >
                    Copas<span className="text-amber-500">.io</span>
                </Link>
                <nav className="flex items-center gap-4">
                    {NAV_LINKS.map(({ href, label }) => (
                        <Link
                            key={href}
                            href={href}
                            className={`text-sm transition-colors hover:text-foreground ${
                                pathname === href
                                    ? "text-foreground font-medium"
                                    : "text-muted-foreground"
                            }`}
                        >
                            {label}
                        </Link>
                    ))}
                    <ThemeToggle />
                </nav>
            </div>
        </header>
    );
}
