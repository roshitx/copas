## Context
You are continuing development of Copas.io — an all-in-one social media 
content downloader built with Next.js 14 (App Router), TypeScript, 
Tailwind CSS, and shadcn/ui.

The app allows users to paste any social media URL (TikTok, Instagram, 
YouTube, X, Facebook, Threads) and instantly download the media.
No login required. No file stored on server. Free to use.

Primary target users: Indonesian internet users.

## Language & Copywriting Rules
- ALL page content, headings, body copy, and UI text must be in BAHASA INDONESIA
- Tone: santai, ramah, to the point — seperti ngobrol sama teman
- Hindari bahasa formal/kaku atau terlalu legal-heavy
- Gunakan kata "kamu" bukan "Anda"
- Contoh tone yang benar: "Gak perlu daftar, gak perlu login. Tinggal paste, langsung copas."
- Contoh tone yang salah: "Pengguna diwajibkan untuk mematuhi ketentuan penggunaan layanan."

---

## Task
Create the following static pages for Copas.io. Each page must:
- Use Next.js 14 App Router convention (app/[page]/page.tsx)
- Use Tailwind CSS + shadcn/ui for styling
- Match dark mode default design
- Be mobile-first and minimal
- Include proper <title> and <meta description> in Bahasa Indonesia for SEO

---

## Pages to Create

### 1. /faq — "Pertanyaan yang Sering Ditanya"
Gunakan Accordion component dari shadcn/ui. Pertanyaan & jawaban dalam Bahasa Indonesia:
- Platform apa saja yang didukung?
  → TikTok, Instagram, YouTube, X (Twitter), Facebook, dan Threads.
- Apakah Copas.io gratis?
  → Ya, gratis selamanya. Gak ada biaya tersembunyi.
- Perlu buat akun dulu?
  → Enggak perlu. Langsung paste link, langsung download.
- Apakah file disimpan di server kalian?
  → Tidak. File langsung di-stream ke perangkat kamu, kami tidak menyimpan apapun.
- Kenapa download saya gagal?
  → Platform sosmed kadang update sistem mereka. Coba lagi beberapa saat, 
    atau cek apakah link-nya masih aktif.
- Ada batasan download?
  → Ada batasan wajar: 10 request per menit per pengguna, biar semua bisa pakai dengan lancar.
- Format apa yang tersedia?
  → Video: MP4 (360p/720p/1080p), Audio: MP3, Gambar: JPG/PNG. 
    Untuk carousel Instagram, semua foto diunduh sekaligus dalam format ZIP.
- Apakah ini legal?
  → Copas.io hanya membantu mengunduh konten. Kamu bertanggung jawab 
    memastikan penggunaan konten sesuai aturan hak cipta yang berlaku.

### 2. /privacy-policy — "Kebijakan Privasi"
Poin utama dalam Bahasa Indonesia:
- Kami tidak mengumpulkan data pribadi kamu
- Kami tidak menyimpan file yang kamu unduh
- IP address hanya dicatat sementara untuk keperluan rate limiting 
  dan otomatis dihapus setelah 24 jam
- Kami menggunakan Cloudflare sebagai CDN 
  (tunduk pada kebijakan privasi Cloudflare)
- Kami memakai analitik tanpa cookie dan tanpa tracking (privacy-first)
- Tidak ada iklan pihak ketiga
- Tidak ada akun pengguna, tidak ada cookie autentikasi
- Kontak untuk masalah privasi: privacy@copas.io

### 3. /terms-of-service — "Syarat & Ketentuan"
Poin utama dalam Bahasa Indonesia:
- Kamu wajib mematuhi Syarat Penggunaan platform sumber konten
- Dilarang menggunakan Copas.io untuk melanggar hak cipta
- Kami tidak bertanggung jawab atas penggunaan konten yang diunduh
- Layanan disediakan apa adanya tanpa garansi
- Kami berhak membatasi atau memblokir penggunaan yang tidak wajar
- Layanan bisa tidak tersedia sewaktu-waktu karena perubahan platform

### 4. /about — "Tentang Copas.io"
Konten dalam Bahasa Indonesia:
- Apa itu Copas.io: satu tempat untuk download semua konten sosmed
- Kenapa kami bikinnya: capek buka website yang berbeda untuk 
  tiap platform — TikTok satu, Instagram satu, YouTube satu lagi. 
  Copas.io selesaikan itu semua dalam satu input.
- Cara kerja: 3 langkah simpel
  1. Paste link dari sosmed mana aja
  2. Copas.io otomatis deteksi platform & ambil medianya
  3. Pilih format → langsung terunduh ke perangkat kamu
- Open source: kode kami terbuka di GitHub (placeholder: github.com/copasio)
- Janji kami: gratis, tanpa iklan, tanpa login, tanpa tracking

### 5. /dmca — "Laporan DMCA"
Konten dalam Bahasa Indonesia:
- Kami tidak menyimpan atau meng-host konten berhak cipta apapun
- Semua media di-stream langsung dari platform sumber
- Untuk permintaan takedown DMCA, silakan hubungi platform sumber 
  tempat konten tersebut diunggah
- Jika tetap perlu menghubungi kami: dmca@copas.io

---

## Additional Instructions
- Buat shared layout component untuk semua halaman statis ini
  (header + footer konsisten)
- Footer berisi link: FAQ · Tentang · Kebijakan Privasi · 
  Syarat & Ketentuan · DMCA
- Semua label navigasi dan footer juga dalam Bahasa Indonesia
- Gunakan Accordion dari shadcn/ui untuk FAQ
- Gunakan Separator dan Typography dari shadcn/ui untuk halaman legal

## File Structure Expected
app/
├── faq/
│   └── page.tsx
├── about/
│   └── page.tsx
├── privacy-policy/
│   └── page.tsx
├── terms-of-service/
│   └── page.tsx
├── dmca/
│   └── page.tsx
└── components/
    └── static-layout.tsx   ← shared layout untuk semua static pages

## Additional Page to Create

### 6. /cara-pakai — "Cara Pakai Copas.io"

Buat halaman tutorial lengkap cara menggunakan Copas.io dari hulu ke hilir,
per platform, dengan perbedaan langkah untuk pengguna Desktop dan Mobile.

---

#### Design & Component Instructions
- Gunakan Tab component dari shadcn/ui untuk switch antar platform
- Di dalam setiap tab platform, gunakan sub-tab atau toggle: "Mobile" vs "Desktop"
- Setiap langkah ditampilkan sebagai numbered steps yang jelas
- Tambahkan icon platform (gunakan lucide-react atau emoji sebagai placeholder 
  sampai asset tersedia)
- Gunakan Badge component dari shadcn/ui untuk label "Mobile" dan "Desktop"
- Gunakan Card component dari shadcn/ui untuk membungkus setiap step group
- Tambahkan tip/catatan khusus per platform menggunakan 
  Alert component (variant: info) dari shadcn/ui

---

#### Content Per Platform (semua dalam Bahasa Indonesia, tone santai)

---

**TikTok**

Mobile:
1. Buka aplikasi TikTok dan temukan video yang ingin kamu unduh
2. Tap tombol **Share** (ikon panah) di sisi kanan video
3. Tap **Salin Tautan** (Copy Link)
4. Buka Copas.io di browser kamu
5. Paste link di kotak input → tap tombol **Copas!**
6. Pilih format (Video MP4 atau Audio MP3)
7. Tap **Unduh** → file tersimpan otomatis di galeri atau folder Downloads

Desktop:
1. Buka TikTok di browser (tiktok.com)
2. Klik video yang ingin diunduh
3. Klik tombol **Share** → pilih **Copy Link**
4. Buka tab baru, buka Copas.io
5. Paste link di kotak input → klik **Copas!**
6. Pilih format → klik **Unduh**

💡 Tip: TikTok versi desktop kadang tidak menampilkan tombol Share. 
Cukup copy URL dari address bar browser kamu.

---

**Instagram**

Mobile (Reels / Video Post):
1. Buka Instagram dan temukan Reels atau video yang ingin diunduh
2. Tap ikon **titik tiga (⋯)** di pojok kanan atas post
3. Tap **Salin Tautan**
4. Buka Copas.io → paste link → tap **Copas!**
5. Pilih format → tap **Unduh**

Mobile (Stories):
1. Buka Stories yang ingin diunduh
2. Tap ikon **titik tiga (⋯)** di pojok kanan bawah
3. Tap **Salin Tautan**
4. Buka Copas.io → paste → tap **Copas!**

Mobile (Carousel / Foto):
1. Buka post foto atau carousel
2. Tap ikon **titik tiga (⋯)** → **Salin Tautan**
3. Paste di Copas.io → semua foto akan diunduh sekaligus dalam format ZIP

Desktop:
1. Buka Instagram di browser (instagram.com)
2. Klik post yang diinginkan
3. Klik ikon **titik tiga (⋯)** → **Salin Tautan**
4. Paste di Copas.io → klik **Copas!**

💡 Tip: Instagram Stories hanya bisa diunduh jika akun tidak di-private.

---

**YouTube**

Mobile:
1. Buka aplikasi YouTube dan temukan video yang ingin diunduh
2. Tap tombol **Share** (ikon panah) di bawah video
3. Tap **Salin Tautan**
4. Buka Copas.io → paste link → tap **Copas!**
5. Pilih kualitas video (360p / 720p / 1080p) atau Audio MP3
6. Tap **Unduh**

Desktop:
1. Buka YouTube di browser (youtube.com)
2. Di bawah video, klik **Share** → klik **Copy Link**
   Atau cukup copy URL langsung dari address bar
3. Buka Copas.io → paste link → klik **Copas!**
4. Pilih format → klik **Unduh**

💡 Tip: Untuk video panjang, pilih resolusi 720p agar proses lebih cepat.
Video 1080p membutuhkan waktu lebih lama tergantung koneksi internet kamu.

---

**X (Twitter)**

Mobile:
1. Buka aplikasi X dan temukan tweet berisi video/GIF/gambar
2. Tap ikon **Share** (ikon panah di bawah tweet)
3. Tap **Salin Tautan ke Tweet** (Copy link to post)
4. Buka Copas.io → paste → tap **Copas!**
5. Pilih format → tap **Unduh**

Desktop:
1. Buka X di browser (x.com)
2. Klik ikon **Share** di bawah tweet → klik **Copy link**
   Atau klik tanggal/waktu tweet untuk buka halaman post, 
   lalu copy URL dari address bar
3. Paste di Copas.io → klik **Copas!**

💡 Tip: Copas.io hanya bisa mengunduh media dari tweet yang bersifat publik.
Tweet dari akun private tidak dapat diunduh.

---

**Facebook**

Mobile:
1. Buka aplikasi Facebook dan temukan video yang ingin diunduh
2. Tap ikon **titik tiga (⋯)** di pojok kanan atas post
3. Tap **Salin Tautan** (Copy Link)
4. Buka Copas.io → paste → tap **Copas!**
5. Pilih format → tap **Unduh**

Desktop:
1. Buka Facebook di browser
2. Klik tanggal/waktu post untuk membuka halaman post tersendiri
3. Copy URL dari address bar browser
4. Paste di Copas.io → klik **Copas!**

💡 Tip: Video dari grup atau profil private tidak bisa diunduh. 
Pastikan video bisa dilihat tanpa login terlebih dahulu.

---

**Threads**

Mobile:
1. Buka aplikasi Threads dan temukan post berisi video/gambar
2. Tap ikon **Share** (ikon panah)
3. Tap **Salin Tautan**
4. Buka Copas.io → paste → tap **Copas!**
5. Pilih format → tap **Unduh**

Desktop:
1. Buka Threads di browser (threads.net)
2. Klik tanggal/waktu post untuk buka halaman post tersendiri
3. Copy URL dari address bar
4. Paste di Copas.io → klik **Copas!**

💡 Tip: Threads saat ini hanya mendukung unduhan video dan gambar.
Audio terpisah belum tersedia untuk platform ini.

---

#### Bottom CTA Section
Setelah semua tab tutorial, tambahkan section CTA:
- Heading: "Udah ngerti caranya? Langsung cobain!"
- Subtext: "Tinggal paste link di bawah ini — gratis, tanpa daftar."
- Tombol: "Coba Sekarang →" yang link ke halaman utama (/)

---

## Updated File Structure
app/
├── faq/
│   └── page.tsx
├── about/
│   └── page.tsx
├── how-to-use/               ← NEW
│   └── page.tsx
├── privacy-policy/
│   └── page.tsx
├── terms-of-service/
│   └── page.tsx
├── dmca/
│   └── page.tsx
└── components/
    └── static-layout.tsx

## Updated Footer Links
FAQ · Cara Pakai · Tentang · Kebijakan Privasi · Syarat & Ketentuan · DMCA
