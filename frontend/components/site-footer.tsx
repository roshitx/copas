import Link from "next/link";

const FOOTER_LINKS = [
    { href: "/faq", label: "FAQ" },
    { href: "/about", label: "Tentang" },
    { href: "/privacy", label: "Kebijakan Privasi" },
    { href: "/terms", label: "Syarat Penggunaan" },
    { href: "/copyright", label: "Hak Cipta & DMCA" },
] as const;

export function SiteFooter() {
    return (
        <footer className="border-t border-border py-8">
            <div className="max-w-4xl mx-auto px-4">
                <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
                    <p className="text-xs text-muted-foreground">
                        Copas.io · Hanya untuk penggunaan pribadi. Hormati hak
                        cipta konten kreator.
                    </p>
                    <nav className="flex flex-wrap items-center gap-4">
                        {FOOTER_LINKS.map(({ href, label }) => (
                            <Link
                                key={href}
                                href={href}
                                className="text-xs text-muted-foreground transition-colors hover:text-foreground"
                            >
                                {label}
                            </Link>
                        ))}
                    </nav>
                </div>
            </div>
        </footer>
    );
}
