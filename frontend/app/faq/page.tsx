import type { Metadata } from "next";
import Link from "next/link";
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "@/components/ui/accordion";

const FAQ_ITEMS = [
    {
        question: "Platform apa saja yang didukung?",
        answer: "Saat ini Copas.io mendukung TikTok, Instagram, YouTube, X (Twitter), Facebook, dan Threads. Kami terus menambah dukungan platform agar proses download makin lengkap.",
    },
    {
        question: "Apakah gratis?",
        answer: "Ya, layanan Copas.io gratis untuk penggunaan pribadi. Kamu tidak perlu login untuk mulai download.",
    },
    {
        question: "Kenapa download gagal?",
        answer: "Biasanya karena link tidak valid, konten privat, konten dibatasi wilayah/usia, atau sumber sedang bermasalah sementara. Coba paste ulang link, cek apakah konten publik, lalu ulangi beberapa saat lagi.",
    },
    {
        question: "Apakah video disimpan di server?",
        answer: "Tidak. Copas.io hanya memproses permintaan download sementara untuk mengirimkan file ke perangkatmu. Kami tidak menyimpan video secara permanen di server.",
    },
    {
        question: "Bagaimana cara download dari TikTok?",
        answer: "Buka TikTok, salin link video, lalu paste ke kolom input di halaman utama Copas.io. Setelah proses selesai, pilih format yang kamu inginkan lalu download.",
    },
    {
        question: "Kenapa video TikTok ada watermark?",
        answer: "Sebagian konten TikTok memang hanya tersedia dalam versi ber-watermark dari sumber aslinya. Hasil yang tersedia mengikuti format yang diberikan oleh platform sumber.",
    },
    {
        question: "Apakah aman digunakan?",
        answer: "Ya, Copas.io tidak meminta login akun media sosial dan tidak meminta data sensitif. Tetap gunakan layanan ini secara bijak dan hormati hak cipta kreator.",
    },
    {
        question: "Bagaimana jika ada masalah?",
        answer: "Kalau kamu menemukan kendala, kirim detail link dan masalahnya ke support@copas.io agar kami bisa bantu cek lebih cepat.",
    },
];

export const metadata: Metadata = {
    title: "Pertanyaan Umum | Copas.io",
    description:
        "FAQ Copas.io: pertanyaan umum seputar dukungan platform, keamanan, proses download, dan bantuan penggunaan.",
};

export default function FaqPage() {
    return (
        <main className="min-h-screen bg-background text-foreground px-4 py-10 md:py-14">
            <div className="mx-auto w-full max-w-3xl">
                <div className="mb-8 space-y-3">
                    <Link
                        href="/"
                        className="inline-flex items-center text-sm text-muted-foreground transition-colors hover:text-foreground"
                    >
                        ← Kembali ke Beranda
                    </Link>
                    <h1 className="text-3xl md:text-4xl font-bold tracking-tight">
                        Pertanyaan Umum
                    </h1>
                    <p className="text-sm md:text-base text-muted-foreground">
                        Temukan jawaban cepat seputar penggunaan Copas.io.
                    </p>
                </div>

                <Accordion type="single" collapsible className="w-full rounded-lg border border-border bg-card px-4 md:px-6">
                    {FAQ_ITEMS.map((item, index) => (
                        <AccordionItem key={item.question} value={`item-${index + 1}`}>
                            <AccordionTrigger className="text-left text-base">
                                {item.question}
                            </AccordionTrigger>
                            <AccordionContent className="text-sm md:text-base text-muted-foreground leading-relaxed">
                                {item.answer}
                            </AccordionContent>
                        </AccordionItem>
                    ))}
                </Accordion>
            </div>
        </main>
    );
}
