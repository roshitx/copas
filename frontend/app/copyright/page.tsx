import type { Metadata } from "next";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
    title: "Hak Cipta & DMCA | Copas.io",
    description:
        "Informasi hak cipta, kebijakan DMCA, dan prosedur pelaporan pelanggaran konten di Copas.io.",
};

export default function CopyrightPage() {
    return (
        <div className="min-h-screen bg-background flex flex-col">
            <SiteHeader />
            <main className="flex-1 px-4 py-10 md:py-14">
                <div className="mx-auto w-full max-w-3xl space-y-10">
                    <div className="space-y-3">
                        <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-foreground">
                            Hak Cipta &amp; DMCA
                        </h1>
                        <p className="text-sm text-muted-foreground">
                            Terakhir diperbarui: Maret 2026
                        </p>
                    </div>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            1. Pengantar
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Copas.io menghormati hak kekayaan intelektual dan
                            hak cipta kreator konten. Layanan ini dibuat sebagai
                            alat bantu untuk penggunaan pribadi, bukan untuk
                            melanggar hak cipta siapa pun.
                        </p>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            2. Cara Kerja Copas.io
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Copas.io bekerja sebagai perantara teknis yang
                            memproses URL dari pengguna untuk mengekstrak tautan
                            media yang tersedia secara publik. Beberapa hal yang
                            tidak kami lakukan:
                        </p>
                        <ul className="space-y-3 text-sm md:text-base text-muted-foreground leading-relaxed">
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Menyimpan salinan konten di server kami
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Menghosting atau mendistribusikan ulang konten
                                berhak cipta
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Menghapus atau mengubah watermark dan metadata
                                konten
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Melewati sistem pembatasan akses (DRM) platform
                            </li>
                        </ul>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            3. Tanggung Jawab Pengguna
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Dengan menggunakan Copas.io, kamu menyetujui bahwa:
                        </p>
                        <ul className="space-y-3 text-sm md:text-base text-muted-foreground leading-relaxed">
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Kamu hanya mengunduh konten untuk penggunaan
                                pribadi
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Kamu tidak akan mendistribusikan ulang konten
                                berhak cipta tanpa izin pemilik
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Kamu bertanggung jawab penuh atas penggunaan
                                konten yang diunduh
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Kamu akan menghormati persyaratan layanan
                                platform sumber
                            </li>
                        </ul>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            4. Kebijakan DMCA
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Meskipun Copas.io tidak menyimpan konten, kami
                            menghormati proses DMCA (Digital Millennium Copyright
                            Act). Kalau kamu pemilik hak cipta dan merasa
                            layanan kami digunakan untuk melanggar hak kamu,
                            silakan hubungi kami.
                        </p>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            5. Cara Mengajukan Laporan DMCA
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Untuk mengajukan permintaan penghapusan DMCA, kirim
                            email ke{" "}
                            <a
                                href="mailto:dmca@copas.io"
                                className="text-amber-500 underline underline-offset-4 transition-colors hover:text-amber-400"
                            >
                                dmca@copas.io
                            </a>{" "}
                            dengan informasi berikut:
                        </p>
                        <div className="rounded-lg border border-border bg-card p-5 space-y-3">
                            <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                                <strong className="text-foreground">a.</strong>{" "}
                                Identifikasi karya berhak cipta yang kamu klaim
                                dilanggar
                            </p>
                            <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                                <strong className="text-foreground">b.</strong>{" "}
                                URL konten asli yang dimaksud
                            </p>
                            <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                                <strong className="text-foreground">c.</strong>{" "}
                                Informasi kontak kamu (nama, email, nomor
                                telepon)
                            </p>
                            <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                                <strong className="text-foreground">d.</strong>{" "}
                                Pernyataan dengan itikad baik bahwa penggunaan
                                tersebut tidak diizinkan oleh pemilik hak cipta
                            </p>
                            <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                                <strong className="text-foreground">e.</strong>{" "}
                                Pernyataan bahwa informasi yang kamu berikan
                                akurat, di bawah ancaman hukuman sumpah palsu
                            </p>
                        </div>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            6. Tindakan yang Kami Ambil
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Setelah menerima laporan DMCA yang valid, kami akan:
                        </p>
                        <ul className="space-y-3 text-sm md:text-base text-muted-foreground leading-relaxed">
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Meninjau laporan dalam waktu yang wajar
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Memblokir URL spesifik yang dilaporkan jika
                                diperlukan
                            </li>
                            <li className="flex gap-3">
                                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                                Menghubungi pelapor untuk konfirmasi tindakan
                                yang diambil
                            </li>
                        </ul>
                    </section>

                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold text-foreground">
                            7. Penggunaan yang Wajar (Fair Use)
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Copas.io mengakui prinsip penggunaan wajar (fair use)
                            yang memungkinkan penggunaan terbatas konten berhak
                            cipta untuk tujuan tertentu seperti pendidikan,
                            komentar, kritik, dan penggunaan pribadi
                            non-komersial.
                        </p>
                    </section>

                    <section className="rounded-lg border border-border bg-card p-5 space-y-3">
                        <h2 className="text-lg font-semibold text-foreground">
                            Kontak
                        </h2>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Untuk laporan DMCA:{" "}
                            <a
                                href="mailto:dmca@copas.io"
                                className="text-amber-500 underline underline-offset-4 transition-colors hover:text-amber-400"
                            >
                                dmca@copas.io
                            </a>
                        </p>
                        <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                            Untuk pertanyaan umum:{" "}
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
