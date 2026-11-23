# Website Resmi PCM Kartasura (Tugas Pemrograman Web berbasis Framework)

Repositori ini berisi kode sumber pembangunan dan implementasi website **Pimpinan Cabang Muhammadiyah (PCM) Kartasura, Kabupaten Sukoharjo** menggunakan **Django 6.x**, **uv**, **PostgreSQL**, dan **Docker**.

Website ini dikembangkan dengan data riil untuk memperkenalkan PCM Kartasura, struktur pimpinan, daftar 12 ranting (PRM), amal usaha (AUM), menyajikan berita dan agenda kegiatan, menyediakan dokumen Surat Keputusan (SK) resmi untuk diunduh, serta menerima pesan dari masyarakat.

---

## 📌 Fitur Utama Website (Bagian A)

1. **Beranda (`/`)**:
   - Hero banner interaktif dengan nama, tagline, dan foto pimpinan PCM Kartasura.
   - Kartu statistik riil: Jumlah Ranting (12 PRM), Jumlah AUM (70+), dan Jumlah Anggota ber-KTAM (364).
   - 3 Berita terbaru terbit dan 3 Agenda mendatang.
2. **Profil Organisasi (`/profil/`)**:
   - Profil lengkap, sejarah pendirian PCM Kartasura sejak 1927, visi, serta misi (ditampilkan rapi bernomor).
   - Informasi kontak resmi sekretariat PCM Kartasura.
3. **Pimpinan PCM (`/pimpinan/`)**:
   - Struktur 9 Pimpinan Harian PCM Kartasura Periode 2022–2027 lengkap dengan foto, jabatan, dan urutan resmi.
4. **Daftar Ranting (`/ranting/`)**:
   - Direktori 12 Pimpinan Ranting Muhammadiyah (PRM) se-Kecamatan Kartasura beserta nama ketua dan alamat.
5. **Amal Usaha Muhammadiyah (`/amal-usaha/`)**:
   - Direktori AUM yang dikelompokkan berdasarkan bidang (Pendidikan, Kesehatan, Sosial, Ekonomi) dengan fitur filter interaktif.
6. **Berita Terkini (`/berita/` & `/berita/<slug>/`)**:
   - Daftar berita terbit dengan paginasi **6 berita per halaman**.
   - Halaman detail berita dengan pemisahan ringkasan, isi, dan sumber asli berita, serta rekomendasi 3 berita lainnya.
   - Proteksi otomatis (HTTP 404) untuk berita berstatus draf atau bertanggal di masa depan.
7. **Agenda Kegiatan (`/agenda/`)**:
   - Pemisahan jelas antara agenda mendatang dan agenda yang sudah terlaksana.
8. **Unduhan Dokumen SK (`/unduhan/`)**:
   - Pengelompokan dokumen SK Tingkat Cabang (PDM Sukoharjo) dan SK Pimpinan Ranting (PRM) Periode 2022–2027.
   - Tombol pratinjau dokumen dan unduh berkas PDF.
9. **Kontak Sekretariat (`/kontak/`)**:
   - Formulir pesan masyarakat berbasis `ModelForm` dengan validasi lengkap dan notifikasi sukses (`messages` framework).
10. **Pencarian Informasi (`/cari/`)**:
    - Pencarian cepat berita dan informasi persyarikatan berdasarkan kata kunci.
11. **Panel Admin Django**:
    - Kustomisasi header admin: *"Admin Website PCM Kartasura"*.
    - Pembatasan Profil Organisasi (maksimal 1 baris, tidak dapat dihapus).
    - Berita dengan `prepopulated_fields` slug dan `date_hierarchy`.
    - Pesan masuk bersifat baca-saja (*read-only*) untuk menjaga integritas pesan masyarakat.
12. **Konsep Teknis Django**:
    - Penggunaan `app_name = 'pcm_web'` (namespacing URL) dan `{% url %}` pada seluruh template.
    - Context processor `profil_dan_tautan` yang menyediakan data profil dan tautan persyarikatan ke seluruh template secara otomatis.
    - Context processor `jadwal_shalat` terintegrasi API Aladhan (Surakarta) secara real-time.
    - `seed_pcm` management command untuk mengisi seluruh data riil PCM Kartasura dalam sekali eksekusi.

---

## 🚀 Panduan Menjalankan di Komputer Lokal

### Prasyarat
- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) (manajer paket Python super cepat)

### Langkah Menjalankan
1. **Clone repositori**:
   ```bash
   git clone https://github.com/buttersh/pcmkartasura.git
   cd pcmkartasura
   ```

2. **Buat file `.env`**:
   ```bash
   cp .env.example .env
   ```

3. **Install dependensi & jalankan migrasi database**:
   ```bash
   uv sync
   uv run python manage.py migrate
   ```

4. **Isi data awal riil PCM Kartasura (`seed_pcm`)**:
   ```bash
   uv run python manage.py seed_pcm
   ```

5. **Jalankan server pengembangan**:
   ```bash
   uv run python manage.py runserver
   ```
   Buka browser di: [http://127.0.0.1:8000](http://127.0.0.1:8000)

6. **Menjalankan Pengujian Unit (Testing)**:
   ```bash
   uv run python manage.py test
   ```

---

## 🐳 Menjalankan dengan Docker & PostgreSQL (Bagian B)

Seluruh konfigurasi kontainer telah disiapkan sehingga siapa pun dapat menjalankan website lengkap beserta database PostgreSQL hanya dengan **satu perintah**:

```bash
docker compose up --build
```
Buka browser di: [http://localhost:8000](http://localhost:8000)

### Arsitektur Docker:
- **`db`**: Image `postgres:17-alpine` dengan penyimpanan persisten pada named volume `postgres_data` dan pemeriksaan kesiapan (`healthcheck: pg_isready`).
- **`web`**: Dibangun secara otomatis dari `Dockerfile` berbasis `python:3.13-slim` dengan manajer dependensi `uv`, menjalankan `collectstatic` saat build, user keamanan non-root (`appuser`), menunggu service database sehat, menjalankan migrasi database otomatis, dan menyajikan aplikasi via server WSGI **Gunicorn** dengan port dari variabel `PORT` (default: 8000).
- **Penyimpanan Media Persisten**: Menggunakan named volume `media_data` agar seluruh file dokumen SK dan gambar yang diunggah tetap aman meskipun kontainer direstart.
- **Pembersihan Data Volume**: Menjalankan `docker compose down -v` akan menghapus seluruh data volume database dan media untuk reset total ke kondisi awal.

---

## ☁️ Deployment ke Cloud (Bagian C)

Website ini siap dideploy ke platform cloud modern seperti **Railway** atau **Render**:
1. Gunakan file `Dockerfile` yang telah disediakan.
2. Tambahkan database PostgreSQL cloud (misalnya Supabase atau Neon).
3. Set environment variable pada dashboard cloud:
   - `SECRET_KEY`: string acak aman untuk produksi.
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: domain aplikasi Anda (misal `pcm-kartasura.up.railway.app`).
   - `CSRF_TRUSTED_ORIGINS`: `https://pcm-kartasura.up.railway.app`
   - `DATABASE_URL`: URL koneksi PostgreSQL cloud dari Supabase/Neon/Railway.
4. Static files disajikan secara optimal dengan kompresi gzip/brotli menggunakan **WhiteNoise**.

---

## 📄 Sumber Data Riil dan Bukti Izin (Bagian D)

Semua data pimpinan, ranting, dan dokumen SK diperoleh dan digunakan atas izin resmi pengurus:

> **Catatan Izin:** Penggunaan data susunan pengurus dan dokumen SK resmi ini telah disetujui oleh **Drs. Abdul Fatah Bintoro, M.Pd.** (Sekretaris PCM Kartasura).  
> **Atribusi Logo:** Logo Muhammadiyah karya K. H. Siradj Dahlan, vektor oleh Hibensis, via Wikimedia Commons, lisensi CC BY-SA 4.0.

### Tabel Sumber Berita PDM Sukoharjo

| Judul Berita | URL Sumber | Tanggal Diambil |
| --- | --- | --- |
| Tingkatkan Perlindungan Perempuan dan Anak, Tim P2M UMS bersama PRM & PRA Jombor Gelar Workshop Inisiasi Tim P3AK | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/tingkatkan-perlindungan-perempuan-dan-anak-tim-p2m-ums-bersama-prm-pra-jombor-gelar-workshop-inisiasi-tim-p3ak/) | 16 November 2026 |
| SMP Ahmad Dahlan Juara Umum Pandu Pengenal Hizbul Wathan Tingkat Kabupaten Sukoharjo 2026 | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/smp-ahmad-dahlan-juara-umum-pandu-pengenal-hizbul-wathan-tingkat-kabupaten-sukoharjo-2026/) | 16 November 2026 |
| KBIHU Armina PDM Sukoharjo Hadir di Blimbing, Siapkan Pendampingan Jemaah Haji 2027 | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/kbihu-armina-pdm-sukoharjo-hadir-di-blimbing-siapkan-pendampingan-jemaah-haji-2027/) | 16 November 2026 |
| Enam Kader Nasyiatul Aisyiyah Sukoharjo Hadiri Musykerwil II PWNA Jawa Tengah | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/enam-kader-nasyiatul-aisyiyah-sukoharjo-hadiri-musykerwil-ii-pwna-jawa-tengah/) | 16 November 2026 |
| Pelatihan Dai Pelajar Muhammadiyah 2 PD IPM Sukoharjo: Dakwah Pelajar | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/pelatihan-dai-pelajar-muhammadiyah-2-pd-ipm-sukoharjo-dakwah-pelajar/) | 16 November 2026 |
| 17 SMP/MTs Muhammadiyah se-Kabupaten Sukoharjo Ikuti Try Out Tes Kemampuan Akademik | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/17-smp-mts-muhammadiyah-se-kabupaten-sukoharjo-ikuti-try-out-tes-kemampuan-akademik/) | 16 November 2026 |
| Melacak Jejak Muhammadiyah Di Kabupaten Sukoharjo | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/melacak-jejak-muhammadiyah-di-kabupaten-sukoharjo/) | 16 November 2026 |
| Anggota Kokam Dibacok Saat Menuju Pengajian, Pemuda Muhammadiyah Tuntut Polisi Bertindak | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/anggota-kokam-dibacok-saat-menuju-pengajian-pemuda-muhammadiyah-tuntut-polisi-bertindak/) | 16 November 2026 |
| IPM Kartasura Gelar Training of Trainers, Cetak Fasilitator Kaderisasi Muda | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/ipm-kartasura-gelar-training-of-trainers-cetak-fasilitator-kaderisasi-muda/) | 16 November 2026 |
| Asa Muhammadiyah Membangun Negeri | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/asa-muhammadiyah-membangun-negeri/) | 16 November 2026 |
| Anggota Dikdasmen Aisyiyah Kartasura Raih Gelar Doktor, Dorong Kesejahteraan Guru Aisyiyah | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/anggota-dikdasmen-aisyiyah-kartasura-raih-gelar-doktor-dorong-kesejahteraan-guru-aisyiyah/) | 16 November 2026 |
| PK IMM H.M. Misbach Gelar Harsa ke-6, Tebar Kebahagiaan dan Pengabdian di Ngemplak Sukoharjo | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/pk-imm-h-m-misbach-gelar-harsa-ke-6-tebar-kebahagiaan-dan-pengabdian-di-ngemplak-sukoharjo/) | 16 November 2026 |
| SMP Muhduta Adakan Outing Class ke UNS: Belajar Langsung di Perpustakaan dan Laboratorium | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/smp-muhduta-adakan-outing-class-ke-uns-belajar-langsung-di-perpustakaan-dan-laboratorium/) | 16 November 2026 |
| Kunjungan Kapolres ke UMS, Perkuat Sinergi Keamanan dan Kemitraan Kampus | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/kunjungan-kapolres-ke-ums-perkuat-sinergi-keamanan-dan-kemitraan-kampus/) | 16 November 2026 |
| Dipimpin Kader Muhammadiyah, Desa ini Raih Penghargaan Anti Korupsi Terbaik se-Jawa Tengah | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/dipimpin-kader-muhammadiyah-desa-ini-raih-penghargaan-anti-korupsi-terbaik-se-jawa-tengah/) | 16 November 2026 |
| Semangat Kompetisi Ratusan Murid di Olympic Ahmad Dahlan V Sukoharjo | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/semangat-kompetisi-ratusan-murid-di-olympic-ahmad-dahlan-v-sukoharjo/) | 16 November 2026 |
| Gerakan Peduli Lingkungan, Mahasiswa Ilkom UMS Gelar Kampanye Pentingnya Memilah Sampah | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/gerakan-peduli-lingkungan-mahasiswa-ilkom-ums-gelar-kampanye-pentingnya-memilah-sampah/) | 16 November 2026 |
| Mahasiswa Fisioterapi UMS Lakukan Deteksi Permasalahan Postur di 8 SD dan TK di Kartasura | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/mahasiswa-fisioterapi-ums-lakukan-deteksi-permasalahan-postur-di-8-sd-dan-tk-di-kartasura/) | 16 November 2026 |
| MPKU PDM Sukoharjo Gelar Rapat Kerja Bahas Rencana Strategis 2025-2029 | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/mpku-pdm-sukoharjo-gelar-rapat-kerja-bahas-rencana-strategis-2025-2029/) | 16 November 2026 |
| 500 Warga Persyarikatan Muhammadiyah Ranting Gonilan memperingati Milad Muhammadiyah ke-112 | [pdmsukoharjo.or.id](https://pdmsukoharjo.or.id/500-warga-persyarikatan-muhammadiyah-ranting-gonilan-memperingati-milad-muhammadiyah-ke-112/) | 16 November 2026 |

### Tabel Sumber Dokumen Surat Keputusan (SK)

| Data Dokumen | Tautan Berkas SK Resmi | Tanggal Diambil |
| --- | --- | --- |
| SK PDM Sukoharjo Susunan PCM Kartasura 2022–2027 | [Google Drive](https://drive.google.com/file/d/1QjrnkfpO9rEN-XJ3BMWvmjcHD-SI1N3_/view?usp=drive_link) | 16 November 2026 |
| SK PCM Kartasura Susunan PRM Ngemplak 2022–2027 | [Google Drive](https://drive.google.com/file/d/1y7xbeBTXtC-K-FVkucduWEyfWM_oEf_b/view?usp=drive_link) | 16 November 2026 |
| SK PCM Kartasura Susunan PRM Makamhaji 2022–2027 | [Google Drive](https://drive.google.com/file/d/11D_fpsdT6YSnE6lLZ6WoKR49C8djEAEj/view?usp=drive_link) | 16 November 2026 |
| SK PCM Kartasura Susunan PRM Ngabeyan 2022–2027 | [Google Drive](https://drive.google.com/file/d/1hbtwQw5lb-TORcQQVJsLeyR06CvGhFAK/view?usp=drive_link) | 16 November 2026 |
| SK PCM Kartasura Susunan PRM Pabelan 2022–2027 | [Google Drive](https://drive.google.com/file/d/1BSIbKV9X0S9rUuenXZSW7vhY_v6IYUoC/view?usp=drive_link) | 16 November 2026 |
| SK PCM Kartasura Susunan PRM Pucangan 2022–2027 | [Google Drive](https://drive.google.com/file/d/1k3RATuDfd_xiPIGD308kBBOpeQOYBMH7/view?usp=drive_link) | 16 November 2026 |
| SK PCM Kartasura Susunan PRM Gumpang 2022–2027 | [Google Drive](https://drive.google.com/file/d/1hD4YEhyDClb9ZgIpD7QCsAhNBp3EsP8M/view?usp=drive_link) | 16 November 2026 |
| SK PCM Kartasura Susunan PRM Ngadirejo 2022–2027 | [Google Drive](https://drive.google.com/file/d/1XZYqc7eIyHGNWkOIoKgnOG0BYYVdp3tt/view?usp=drive_link) | 16 November 2026 |
| SK PCM Kartasura Susunan PRM Kertonatan 2022–2027 | [Google Drive](https://drive.google.com/file/d/12jhHDx0oqukvZr61VhsCbEBNdknxo2EL/view?usp=drive_link) | 16 November 2026 |
| SK PCM Kartasura Susunan PRM Wirogunan 2022–2027 | [Google Drive](https://drive.google.com/file/d/1a_C8DgnQpuPzEwVA4i6TzdyDlYyf61z2/view?usp=drive_link) | 16 November 2026 |
| SK PCM Kartasura Susunan PRM Kartasura 2022–2027 | [Google Drive](https://drive.google.com/file/d/1q5XqVhhDxyqt1xyDlfNXTTSLMsWqwijo/view?usp=drive_link) | 16 November 2026 |
| SK PCM Kartasura Susunan PRM Gonilan 2022–2027 | [Google Drive](https://drive.google.com/file/d/1BoU70gewqgQrGXH6LMmvUT10Y_4fXNMd/view?usp=drive_link) | 16 November 2026 |
| SK PCM Kartasura Susunan PRM Singopuran 2022–2027 | [Google Drive](https://drive.google.com/file/d/1duR7aLQcqgKtuq4gXI46ZQKzbtor0DJN/view?usp=drive_link) | 16 November 2026 |
