import Link from "next/link";

const INFO_LINKS = [
    { href: "/faq", label: "FAQ" },
    { href: "/tutorial", label: "Tutorial" },
    { href: "/about", label: "Tentang" },
] as const;

const LEGAL_LINKS = [
    { href: "/privacy", label: "Kebijakan Privasi" },
    { href: "/terms", label: "Syarat Penggunaan" },
    { href: "/copyright", label: "Hak Cipta & DMCA" },
] as const;

export function SiteFooter() {
    return (
        <footer className="border-t border-border bg-muted/20">
            <div className="max-w-4xl mx-auto px-4 py-10">
                {/* Main footer grid */}
                <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">
                    {/* Brand column */}
                    <div className="space-y-3">
                        <p className="text-base font-bold tracking-tight text-foreground">
                            Copas<span className="text-amber-500">.io</span>
                        </p>
                        <p className="text-sm text-muted-foreground leading-relaxed max-w-[200px]">
                            Unduh video & audio dari berbagai platform, gratis dan tanpa login.
                        </p>
                    </div>

                    {/* Info links column */}
                    <div className="space-y-3">
                        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
                            Informasi
                        </p>
                        <ul className="space-y-2">
                            {INFO_LINKS.map(({ href, label }) => (
                                <li key={href}>
                                    <Link
                                        href={href}
                                        className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                                    >
                                        {label}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Legal links column */}
                    <div className="space-y-3">
                        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
                            Legal
                        </p>
                        <ul className="space-y-2">
                            {LEGAL_LINKS.map(({ href, label }) => (
                                <li key={href}>
                                    <Link
                                        href={href}
                                        className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                                    >
                                        {label}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                {/* Divider + copyright */}
                <div className="mt-10 border-t border-border pt-6 flex flex-col items-center gap-1 sm:flex-row sm:justify-between">
                    <p className="text-xs text-muted-foreground">
                        © {new Date().getFullYear()} Copas.io · Hanya untuk penggunaan pribadi.
                    </p>
                    <p className="text-xs text-muted-foreground">
                        Hormati hak cipta konten kreator.
                    </p>
                </div>
            </div>
        </footer>
    );
}
