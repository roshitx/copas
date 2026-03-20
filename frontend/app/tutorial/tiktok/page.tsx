import type { Metadata } from "next";
import Link from "next/link";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
    title: "Cara Download Video TikTok | Copas.io",
    description:
        "Panduan lengkap cara download video TikTok tanpa watermark menggunakan Copas.io. Gratis dan mudah.",
};

export default function TikTokTutorial() {
    return (
        <div className="min-h-screen bg-background flex flex-col">
            <SiteHeader />
            <main className="flex-1 px-4 py-10 md:py-14">
                <div className="mx-auto w-full max-w-3xl space-y-10">
                    <div className="space-y-3">
                        <Link
                            href="/tutorial"
                            className="text-sm text-amber-500 hover:text-amber-400 transition-colors"
                        >
                            &larr; Semua Tutorial
                        </Link>
                        <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-foreground">
                            Cara Download Video TikTok
                        </h1>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Download video TikTok dengan mudah dalam beberapa
                            langkah sederhana.
                        </p>
                    </div>

                    <section className="space-y-6">
                        <div className="space-y-4">
                            <div className="flex gap-4">
                                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-amber-500 text-sm font-bold text-zinc-950">
                                    1
                                </div>
                                <div className="space-y-2">
                                    <h2 className="text-lg font-semibold text-foreground">
                                        Buka Video TikTok
                                    </h2>
                                    <p className="text-sm text-muted-foreground leading-relaxed">
                                        Buka aplikasi TikTok atau website
                                        tiktok.com, lalu cari video yang ingin
                                        kamu download.
                                    </p>
                                </div>
                            </div>

                            <div className="flex gap-4">
                                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-amber-500 text-sm font-bold text-zinc-950">
                                    2
                                </div>
                                <div className="space-y-2">
                                    <h2 className="text-lg font-semibold text-foreground">
                                        Salin Link Video
                                    </h2>
                                    <p className="text-sm text-muted-foreground leading-relaxed">
                                        Ketuk tombol &quot;Bagikan&quot; (ikon
                                        panah) di video, lalu pilih &quot;Salin
                                        Link&quot;. Kalau di browser, salin URL
                                        dari address bar.
                                    </p>
                                </div>
                            </div>

                            <div className="flex gap-4">
                                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-amber-500 text-sm font-bold text-zinc-950">
                                    3
                                </div>
                                <div className="space-y-2">
                                    <h2 className="text-lg font-semibold text-foreground">
                                        Tempel di Copas.io
                                    </h2>
                                    <p className="text-sm text-muted-foreground leading-relaxed">
                                        Buka{" "}
                                        <Link
                                            href="/"
                                            className="text-amber-500 underline underline-offset-4 hover:text-amber-400"
                                        >
                                            Copas.io
                                        </Link>
                                        , tempel link video ke kolom input,
                                        lalu tekan Enter atau klik tombol
                                        Download.
                                    </p>
                                </div>
                            </div>

                            <div className="flex gap-4">
                                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-amber-500 text-sm font-bold text-zinc-950">
                                    4
                                </div>
                                <div className="space-y-2">
                                    <h2 className="text-lg font-semibold text-foreground">
                                        Pilih Format & Download
                                    </h2>
                                    <p className="text-sm text-muted-foreground leading-relaxed">
                                        Setelah proses selesai, pilih format
                                        video yang kamu mau, lalu klik untuk
                                        mengunduhnya ke perangkat kamu.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </section>

                    <section className="rounded-xl border border-border bg-card p-5 space-y-3">
                        <h2 className="text-base font-semibold text-foreground">
                            Tips
                        </h2>
                        <ul className="space-y-2 text-sm text-muted-foreground">
                            <li className="flex gap-2">
                                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Pastikan video bersifat publik agar bisa
                                didownload.
                            </li>
                            <li className="flex gap-2">
                                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Copas.io mendukung link TikTok pendek (vm.tiktok.com) maupun link lengkap.
                            </li>
                            <li className="flex gap-2">
                                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Gunakan Ctrl+V / Cmd+V untuk tempel link lebih
                                cepat.
                            </li>
                        </ul>
                    </section>
                </div>
            </main>
            <SiteFooter />
        </div>
    );
}
