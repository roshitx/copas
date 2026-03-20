import type { Metadata } from "next";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import { PlatformIcon } from "@/components/platform-icon";
import { SUPPORTED_PLATFORMS } from "@/lib/constants";

export const metadata: Metadata = {
    title: "Tentang Kami | Copas.io",
    description:
        "Kenali Copas.io, layanan download media sosial gratis yang bisa langsung dipakai tanpa login.",
};

export default function AboutPage() {
    return (
        <div className="min-h-screen bg-background flex flex-col">
            <SiteHeader />
            <main className="flex-1 px-4 py-10 md:py-14">
                <div className="mx-auto w-full max-w-3xl space-y-10">
                    <div className="space-y-3">
                        <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-foreground">
                            Tentang Copas.io
                        </h1>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Alat bantu download media sosial yang simpel dan
                            langsung ke intinya.
                        </p>
                    </div>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            Apa Itu Copas.io?
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Copas.io adalah layanan gratis untuk mengunduh video,
                            gambar, dan audio dari platform media sosial populer.
                            TikTok, Instagram, YouTube, X (Twitter), Facebook,
                            dan Threads, semuanya didukung.
                        </p>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Cara pakainya? Tempel link konten yang kamu mau,
                            pilih format, lalu download. Nggak perlu login,
                            nggak perlu ribet.
                        </p>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            Kenapa Copas.io?
                        </h2>
                        <ul className="space-y-3 text-sm md:text-base text-muted-foreground leading-relaxed">
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                <span>
                                    <strong className="text-foreground">
                                        Gratis sepenuhnya
                                    </strong>{" "}
                                    tanpa biaya tersembunyi atau langganan.
                                </span>
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                <span>
                                    <strong className="text-foreground">
                                        Tanpa login
                                    </strong>,
                                    langsung pakai tanpa perlu bikin akun.
                                </span>
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                <span>
                                    <strong className="text-foreground">
                                        Multi-platform
                                    </strong>,
                                    mendukung 6 platform media sosial besar.
                                </span>
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                <span>
                                    <strong className="text-foreground">
                                        Cepat dan ringan
                                    </strong>,
                                    dibangun untuk kecepatan, bukan untuk jual iklan.
                                </span>
                            </li>
                        </ul>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            Platform yang Didukung
                        </h2>
                        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                            {(() => {
                                const displayNames: Record<string, string> = {
                                    tiktok: "TikTok",
                                    instagram: "Instagram",
                                    youtube: "YouTube",
                                    twitter: "X (Twitter)",
                                    facebook: "Facebook",
                                    threads: "Threads",
                                };
                                return SUPPORTED_PLATFORMS.map((platform) => (
                                    <div
                                        key={platform}
                                        className="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3 text-sm font-medium text-foreground"
                                    >
                                        <PlatformIcon platform={platform} size={20} />
                                        <span>{displayNames[platform]}</span>
                                    </div>
                                ));
                            })()}
                        </div>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            Catatan
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Copas.io dibuat untuk penggunaan pribadi. Kami
                            menghormati hak cipta kreator konten dan berharap
                            kamu juga mencantumkan kredit kalau membagikan ulang
                            konten yang sudah diunduh.
                        </p>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Kami tidak menyimpan video atau data pribadi kamu
                            di server. Setiap permintaan diproses secara
                            real-time dan tidak disimpan secara permanen.
                        </p>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            Kontak
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Punya pertanyaan, saran, atau nemuin kendala?
                            Hubungi kami di{" "}
                            <a
                                href="mailto:support@copas.io"
                                className="text-amber-500 underline underline-offset-4 transition-colors hover:text-amber-400"
                            >
                                support@copas.io
                            </a>
                        </p>
                    </section>
                </div>
            </main>
            <SiteFooter />
        </div>
    );
}
