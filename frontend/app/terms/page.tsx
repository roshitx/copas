import type { Metadata } from "next";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
    title: "Syarat Penggunaan | Copas.io",
    description:
        "Syarat dan ketentuan penggunaan layanan Copas.io.",
};

export default function TermsPage() {
    return (
        <div className="min-h-screen bg-background flex flex-col">
            <SiteHeader />
            <main className="flex-1 px-4 py-10 md:py-14">
                <div className="mx-auto w-full max-w-3xl space-y-10">
                    <div className="space-y-3">
                        <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-foreground">
                            Syarat Penggunaan
                        </h1>
                        <p className="text-sm text-muted-foreground">
                            Terakhir diperbarui: Maret 2026
                        </p>
                    </div>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            1. Penerimaan Syarat
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Dengan menggunakan Copas.io, kamu dianggap setuju
                            dengan seluruh syarat yang tercantum di halaman ini.
                            Kalau kamu tidak setuju, jangan gunakan layanan ini.
                        </p>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            2. Penggunaan yang Diizinkan
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Copas.io hanya boleh digunakan untuk keperluan
                            pribadi dan non-komersial. Kamu tidak diperbolehkan:
                        </p>
                        <ul className="space-y-3 text-sm md:text-base text-muted-foreground leading-relaxed">
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Mendistribusikan ulang konten yang diunduh tanpa
                                izin pemilik
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Membangun produk atau layanan komersial di atas
                                Copas.io
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Menggunakan bot, scraper, atau alat otomatis
                                untuk mengakses layanan secara massal
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Berusaha melewati batasan rate limiting atau
                                sistem keamanan lainnya
                            </li>
                        </ul>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            3. Konten yang Bisa Diproses
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Copas.io hanya memproses URL dari konten yang
                            tersedia secara publik di platform sumber. Konten
                            privat, konten berbayar, atau konten yang dilindungi
                            DRM di luar cakupan layanan ini.
                        </p>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Kami tidak menjamin bahwa semua URL bisa diproses.
                            Ketersediaan tergantung pada platform sumber dan
                            format konten yang mereka sediakan.
                        </p>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            4. Batasan Tanggung Jawab
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Copas.io disediakan &quot;apa adanya&quot; tanpa
                            jaminan dalam bentuk apa pun. Kami tidak bertanggung
                            jawab atas:
                        </p>
                        <ul className="space-y-3 text-sm md:text-base text-muted-foreground leading-relaxed">
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Konten yang diunduh oleh pengguna dan bagaimana
                                konten tersebut digunakan
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Kerugian langsung atau tidak langsung yang timbul
                                dari penggunaan layanan
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Gangguan layanan, downtime, atau kesalahan teknis
                            </li>
                        </ul>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            5. Ketersediaan Layanan
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Kami tidak menjamin layanan berjalan 24/7 tanpa
                            gangguan. Copas.io bisa berubah, ditangguhkan, atau
                            dihentikan sewaktu-waktu tanpa pemberitahuan
                            sebelumnya.
                        </p>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            6. Perubahan Syarat
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Syarat penggunaan ini bisa kami perbarui
                            sewaktu-waktu. Perubahan berlaku sejak dipublikasikan
                            di halaman ini. Dengan terus menggunakan layanan
                            setelah perubahan, kamu dianggap menyetujui syarat
                            yang baru.
                        </p>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            7. Hubungi Kami
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Kalau ada pertanyaan soal syarat penggunaan ini,
                            hubungi kami di{" "}
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
