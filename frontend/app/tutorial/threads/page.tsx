import type { Metadata } from "next";
import Link from "next/link";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
    title: "Cara Download dari Threads | Copas.io",
    description:
        "Panduan download foto dan video dari Threads menggunakan Copas.io.",
};

export default function ThreadsTutorial() {
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
                            Cara Download dari Threads
                        </h1>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Download foto dan video dari postingan Threads.
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
                                        Buka Postingan Threads
                                    </h2>
                                    <p className="text-sm text-muted-foreground leading-relaxed">
                                        Buka aplikasi Threads atau
                                        threads.net dan temukan postingan yang
                                        berisi media yang ingin kamu download.
                                    </p>
                                </div>
                            </div>

                            <div className="flex gap-4">
                                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-amber-500 text-sm font-bold text-zinc-950">
                                    2
                                </div>
                                <div className="space-y-2">
                                    <h2 className="text-lg font-semibold text-foreground">
                                        Salin Link
                                    </h2>
                                    <p className="text-sm text-muted-foreground leading-relaxed">
                                        Ketuk ikon &quot;Bagikan&quot; di
                                        postingan, lalu pilih &quot;Salin
                                        Tautan&quot;.
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
                                        </Link>{" "}
                                        dan tempel link Threads ke kolom input.
                                    </p>
                                </div>
                            </div>

                            <div className="flex gap-4">
                                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-amber-500 text-sm font-bold text-zinc-950">
                                    4
                                </div>
                                <div className="space-y-2">
                                    <h2 className="text-lg font-semibold text-foreground">
                                        Download
                                    </h2>
                                    <p className="text-sm text-muted-foreground leading-relaxed">
                                        Pilih format yang tersedia (foto atau
                                        video) dan klik untuk download.
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
                                Postingan Threads harus publik.
                            </li>
                            <li className="flex gap-2">
                                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Threads dari Meta menggunakan infrastruktur
                                yang sama dengan Instagram, jadi proses
                                download-nya cepat.
                            </li>
                        </ul>
                    </section>
                </div>
            </main>
            <SiteFooter />
        </div>
    );
}
