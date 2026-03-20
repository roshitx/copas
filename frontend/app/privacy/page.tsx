import type { Metadata } from "next";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
    title: "Kebijakan Privasi | Copas.io",
    description:
        "Kebijakan privasi Copas.io: bagaimana kami menangani data dan melindungi privasi pengguna.",
};

export default function PrivacyPage() {
    return (
        <div className="min-h-screen bg-background flex flex-col">
            <SiteHeader />
            <main className="flex-1 px-4 py-10 md:py-14">
                <div className="mx-auto w-full max-w-3xl space-y-10">
                    <div className="space-y-3">
                        <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-foreground">
                            Kebijakan Privasi
                        </h1>
                        <p className="text-sm text-muted-foreground">
                            Terakhir diperbarui: Maret 2026
                        </p>
                    </div>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            1. Pendahuluan
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Copas.io (&quot;kami&quot;, &quot;layanan&quot;)
                            menghargai privasi setiap pengguna. Halaman ini
                            menjelaskan bagaimana kami mengumpulkan, menggunakan,
                            dan melindungi informasi saat kamu memakai layanan
                            kami.
                        </p>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            2. Data yang Kami Kumpulkan
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Copas.io dibangun dengan prinsip{" "}
                            <strong className="text-foreground">
                                minimal data
                            </strong>
                            . Kami tidak meminta login, tidak mengumpulkan data
                            pribadi, dan tidak menggunakan cookie pelacak.
                        </p>
                        <ul className="space-y-3 text-sm md:text-base text-muted-foreground leading-relaxed">
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                <span>
                                    <strong className="text-foreground">
                                        URL yang dikirimkan
                                    </strong>{" "}
                                    diproses secara real-time untuk ekstraksi
                                    media, lalu dihapus. Tidak disimpan secara
                                    permanen.
                                </span>
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                <span>
                                    <strong className="text-foreground">
                                        Data teknis dasar
                                    </strong>{" "}
                                    seperti alamat IP dan user-agent browser
                                    dikumpulkan otomatis oleh server untuk
                                    rate limiting dan keamanan.
                                </span>
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                <span>
                                    <strong className="text-foreground">
                                        Cache sementara
                                    </strong>{" "}
                                    dari hasil ekstraksi disimpan beberapa menit
                                    untuk mempercepat permintaan berulang, lalu
                                    otomatis dihapus.
                                </span>
                            </li>
                        </ul>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            3. Data yang Tidak Kami Kumpulkan
                        </h2>
                        <ul className="space-y-3 text-sm md:text-base text-muted-foreground leading-relaxed">
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Nama, email, atau informasi identitas pribadi
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Kredensial akun media sosial
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Riwayat download (tidak ada fitur akun atau login)
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Data pembayaran (layanan ini sepenuhnya gratis)
                            </li>
                        </ul>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            4. Penyimpanan Video
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Copas.io{" "}
                            <strong className="text-foreground">
                                tidak menyimpan
                            </strong>{" "}
                            file video, gambar, atau audio di server kami. Semua
                            konten diproses secara streaming langsung dari
                            sumber asli ke perangkat kamu.
                        </p>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            5. Cookie dan Penyimpanan Lokal
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Kami hanya menggunakan localStorage di browser untuk
                            menyimpan preferensi tema (terang/gelap). Tidak ada
                            cookie pelacak, cookie iklan, atau cookie pihak
                            ketiga.
                        </p>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            6. Layanan Pihak Ketiga
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Copas.io mengakses konten dari platform media sosial
                            pihak ketiga (TikTok, Instagram, YouTube, dll.)
                            berdasarkan URL yang kamu berikan. Kami tidak
                            berafiliasi dengan platform tersebut dan tidak
                            bertanggung jawab atas kebijakan privasi mereka.
                        </p>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            7. Keamanan
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Kami menerapkan rate limiting, validasi input, dan
                            koneksi terenkripsi (HTTPS) untuk melindungi layanan
                            dan pengguna.
                        </p>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            8. Perubahan Kebijakan
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Kebijakan privasi ini bisa berubah sewaktu-waktu.
                            Kalau ada perubahan, kami akan update di halaman ini
                            beserta tanggal pembaruan terbaru.
                        </p>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            9. Hubungi Kami
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Kalau kamu punya pertanyaan soal kebijakan privasi
                            ini, hubungi kami di{" "}
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
