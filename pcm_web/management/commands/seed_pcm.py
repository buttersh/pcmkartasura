from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify

from pcm_web.models import (
    Agenda,
    AmalUsaha,
    Berita,
    Dokumen,
    Pimpinan,
    ProfilOrganisasi,
    Ranting,
    TautanTerkait,
)


POSTS_URL = "https://pdmsukoharjo.or.id/wp-json/wp/v2/posts"
GOOGLE_DRIVE_DOWNLOAD_URL = "https://drive.google.com/uc?export=download&id={file_id}"

SK_DOKUMEN = (
    (
        "SK PDM Sukoharjo Susunan PCM Kartasura 2022–2027",
        "1QjrnkfpO9rEN-XJ3BMWvmjcHD-SI1N3_",
        "Pimpinan Cabang Muhammadiyah Kartasura oleh PDM Sukoharjo",
    ),
    (
        "SK PCM Kartasura Susunan PRM Ngemplak 2022–2027",
        "1y7xbeBTXtC-K-FVkucduWEyfWM_oEf_b",
        "Pimpinan Ranting Muhammadiyah Ngemplak oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Makamhaji 2022–2027",
        "11D_fpsdT6YSnE6lLZ6WoKR49C8djEAEj",
        "Pimpinan Ranting Muhammadiyah Makamhaji oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Ngabeyan 2022–2027",
        "1hbtwQw5lb-TORcQQVJsLeyR06CvGhFAK",
        "Pimpinan Ranting Muhammadiyah Ngabeyan oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Pabelan 2022–2027",
        "1BSIbKV9X0S9rUuenXZSW7vhY_v6IYUoC",
        "Pimpinan Ranting Muhammadiyah Pabelan oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Pucangan 2022–2027",
        "1k3RATuDfd_xiPIGD308kBBOpeQOYBMH7",
        "Pimpinan Ranting Muhammadiyah Pucangan oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Gumpang 2022–2027",
        "1hD4YEhyDClb9ZgIpD7QCsAhNBp3EsP8M",
        "Pimpinan Ranting Muhammadiyah Gumpang oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Ngadirejo 2022–2027",
        "1XZYqc7eIyHGNWkOIoKgnOG0BYYVdp3tt",
        "Pimpinan Ranting Muhammadiyah Ngadirejo oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Kertonatan 2022–2027",
        "12jhHDx0oqukvZr61VhsCbEBNdknxo2EL",
        "Pimpinan Ranting Muhammadiyah Kertonatan oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Wirogunan 2022–2027",
        "1a_C8DgnQpuPzEwVA4i6TzdyDlYyf61z2",
        "Pimpinan Ranting Muhammadiyah Wirogunan oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Kartasura 2022–2027",
        "1q5XqVhhDxyqt1xyDlfNXTTSLMsWqwijo",
        "Pimpinan Ranting Muhammadiyah Kartasura oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Gonilan 2022–2027",
        "1BoU70gewqgQrGXH6LMmvUT10Y_4fXNMd",
        "Pimpinan Ranting Muhammadiyah Gonilan oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Singopuran 2022–2027",
        "1duR7aLQcqgKtuq4gXI46ZQKzbtor0DJN",
        "Pimpinan Ranting Muhammadiyah Singopuran oleh PCM Kartasura",
    ),
)

PIMPINAN_DATA = [
    {
        "nama": "Ihwan Susila, S.E., M.Si., Ph.D.",
        "jabatan": "Ketua",
        "periode": "2022–2027",
        "urutan": 1,
        "foto_file": "ihwan-susila.jpg",
    },
    {
        "nama": "Drs. Abdul Fatah Bintoro, M.Pd.",
        "jabatan": "Sekretaris",
        "periode": "2022–2027",
        "urutan": 2,
        "foto_file": "abdul-fatah-bintoro.jpg",
    },
    {
        "nama": "Prof. Dr. Kuswaji Dwi Priyono, M.Si.",
        "jabatan": "Bendahara",
        "periode": "2022–2027",
        "urutan": 3,
        "foto_file": "kuswaji-dwi-priyono.jpg",
    },
    {
        "nama": "Dr. Abdullah Mahmud, M.Ag.",
        "jabatan": "Wakil Ketua — Tarjih, Tabligh dan Pembinaan Masjid",
        "periode": "2022–2027",
        "urutan": 4,
        "foto_file": "abdullah-mahmud.jpg",
    },
    {
        "nama": "H. Asrori, S.Pd.I.",
        "jabatan": "Wakil Ketua — Pendidikan",
        "periode": "2022–2027",
        "urutan": 5,
        "foto_file": None,
    },
    {
        "nama": "Rahmad Basuki",
        "jabatan": "Wakil Ketua — Pembinaan Kader dan Sumber Daya Insani",
        "periode": "2022–2027",
        "urutan": 6,
        "foto_file": None,
    },
    {
        "nama": "Prof. Dr. H. Bambang Sumardjoko, M.Pd.",
        "jabatan": "Wakil Ketua — PKU dan Kesejahteraan Sosial",
        "periode": "2022–2027",
        "urutan": 7,
        "foto_file": "bambang-sumardjoko.jpg",
    },
    {
        "nama": "Dr. H. Abdul Aziz Nugroho Pratama, M.M.",
        "jabatan": "Wakil Ketua — Ekonomi dan Pemberdayaan Masyarakat",
        "periode": "2022–2027",
        "urutan": 8,
        "foto_file": None,
    },
    {
        "nama": "Drs. Muhammad Widodo, M.Pd.",
        "jabatan": "Wakil Ketua — Hukum, Lingkungan Hidup, Pustaka dan Informasi",
        "periode": "2022–2027",
        "urutan": 9,
        "foto_file": None,
    },
]

RANTING_DATA = [
    {"nama_ranting": "Kartasura", "ketua": "Achmad Fatoni, M.Pd", "alamat": "Kelurahan Kartasura, Kec. Kartasura"},
    {"nama_ranting": "Ngemplak", "ketua": "Suramto, S.Pd.", "alamat": "Desa Ngemplak, Kec. Kartasura"},
    {"nama_ranting": "Pucangan", "ketua": "Drs. H. Maryanto, MM", "alamat": "Kelurahan Pucangan, Kec. Kartasura"},
    {"nama_ranting": "Kertonatan", "ketua": "Drs. Ali Sa'bani, M.Pd.I", "alamat": "Desa Kertonatan, Kec. Kartasura"},
    {"nama_ranting": "Wirogunan", "ketua": "Dr. H. Dzanurusyamsi, M.H.", "alamat": "Desa Wirogunan, Kec. Kartasura"},
    {"nama_ranting": "Ngabeyan", "ketua": "Muhammad Rochjani, S.Pd", "alamat": "Kelurahan Ngabeyan, Kec. Kartasura"},
    {"nama_ranting": "Singopuran", "ketua": "H. Nur Hasan, M.T.", "alamat": "Desa Singopuran, Kec. Kartasura"},
    {"nama_ranting": "Pabelan", "ketua": "apt. Gunawan Setiyadi, M.Sc.", "alamat": "Desa Pabelan, Kec. Kartasura"},
    {"nama_ranting": "Gonilan", "ketua": "Drs. Supriyadi", "alamat": "Desa Gonilan, Kec. Kartasura"},
    {"nama_ranting": "Makamhaji", "ketua": "Drs. Edy Siyamto, M.Si.", "alamat": "Kelurahan Makamhaji, Kec. Kartasura"},
    {"nama_ranting": "Gumpang", "ketua": "Muhammad Anis Sumaji, S.Ag., M.PI", "alamat": "Desa Gumpang, Kec. Kartasura"},
    {"nama_ranting": "Ngadirejo", "ketua": "Agus Mustamar, SH.I.", "alamat": "Desa Ngadirejo, Kec. Kartasura"},
]

AUM_DATA = [
    {
        "nama": "MIM Pucangan Kartasura",
        "bidang": "sekolah",
        "deskripsi": "Madrasah Ibtidaiyah Muhammadiyah unggulan berkarakter Islami di Pucangan.",
        "alamat": "Pucangan, Kartasura, Sukoharjo",
    },
    {
        "nama": "MIM Gonilan Kartasura",
        "bidang": "sekolah",
        "deskripsi": "Madrasah Ibtidaiyah Muhammadiyah berbasis tahfidz dan sains di Gonilan.",
        "alamat": "Gonilan, Kartasura, Sukoharjo",
    },
    {
        "nama": "SMP Muhammadiyah 1 Kartasura",
        "bidang": "sekolah",
        "deskripsi": "Sekolah Menengah Pertama Muhammadiyah dengan program unggulan akademik dan tahfidz.",
        "alamat": "Jl. Ahmad Yani No. 12, Kartasura",
    },
    {
        "nama": "SMP Muhammadiyah 2 Kartasura (SMP Muhduta)",
        "bidang": "sekolah",
        "deskripsi": "SMP Muhammadiyah 2 Kartasura (Muhduta) berprestasi di tingkat kabupaten dan provinsi.",
        "alamat": "Pucangan, Kartasura, Sukoharjo",
    },
    {
        "nama": "SMA Muhammadiyah 2 Kartasura",
        "bidang": "sekolah",
        "deskripsi": "Sekolah Menengah Atas dengan fasilitas laboratorium lengkap dan program kaderisasi IPM.",
        "alamat": "Ngadirejo, Kartasura, Sukoharjo",
    },
    {
        "nama": "Pondok Pesantren Mahasiswa KH Mas Mansur (Shabran UMS)",
        "bidang": "pondok-pesantren",
        "deskripsi": "Kaderisasi ulama tarjih dan mubaligh Muhammadiyah tingkat nasional.",
        "alamat": "Pabelan, Kartasura, Sukoharjo",
    },
    {
        "nama": "Balai Pengobatan PKU Muhammadiyah Kartasura",
        "bidang": "klinik",
        "deskripsi": "Layanan kesehatan primer terpadu untuk masyarakat umum dan dhuafa.",
        "alamat": "Jl. Slamet Riyadi, Kartasura",
    },
    {
        "nama": "Posyandu Lansia Husnul Khatimah 'Aisyiyah",
        "bidang": "klinik",
        "deskripsi": "Pemeriksaan kesehatan rutin dan bimbingan rohani bagi lanjut usia.",
        "alamat": "Gedung Dakwah Muhammadiyah Kartasura",
    },
    {
        "nama": "Panti Asuhan Yatim Muhammadiyah Kartasura",
        "bidang": "panti-asuhan",
        "deskripsi": "Pengasuhan, pendidikan, dan pembinaan anak yatim piatu persyarikatan.",
        "alamat": "Wirogunan, Kartasura, Sukoharjo",
    },
    {
        "nama": "Panti Asuhan Putri 'Aisyiyah Kartasura",
        "bidang": "panti-asuhan",
        "deskripsi": "Lembaga kesejahteraan sosial anak putri dengan pembinaan akhlak mulia dan ketrampilan mandiri.",
        "alamat": "Ngemplak, Kartasura, Sukoharjo",
    },
    {
        "nama": "Masjid Sudalmiyah Suhud UMS",
        "bidang": "masjid",
        "deskripsi": "Pusat ibadah dan kajian Islam terpadu sivitas akademika dan masyarakat Kartasura.",
        "alamat": "Kampus 2 UMS, Pabelan, Kartasura",
    },
    {
        "nama": "Kantor Layanan LazisMu Kartasura",
        "bidang": "lazismu",
        "deskripsi": "Pengelolaan zakat, infaq, dan sedekah untuk pemberdayaan umat dan beasiswa pendidikan.",
        "alamat": "Gedung Dakwah PCM Kartasura, Jl. Slamet Riyadi No. 270B, Gumpang",
    },
    {
        "nama": "BMT Surya Melati Kartasura",
        "bidang": "toko",
        "deskripsi": "Koperasi simpan pinjam syariah untuk penguatan UMKM dan ekonomi warga persyarikatan.",
        "alamat": "Kartasura, Sukoharjo",
    },
]

AGENDA_DATA = [
    {
        "nama_kegiatan": "Pengajian Ahad Pagi Akbar PCM Kartasura",
        "hari_offset": 5,
        "tempat": "Gedung Dakwah Muhammadiyah Kartasura",
        "keterangan": "Kajian rutin se-Kecamatan Kartasura bersama Majelis Tabligh dengan tema Revitalisasi Cabang dan Ranting.",
        "rutin": True,
    },
    {
        "nama_kegiatan": "Rapat Pleno PCM Kartasura Evaluasi Program Semester II",
        "hari_offset": 8,
        "tempat": "Ruang Rapat Utama Gedung Dakwah PCM Kartasura",
        "keterangan": "Membahas sinergi antar-Majelis, AUM, dan persiapan agenda Ramadhan 1448 H.",
        "rutin": False,
    },
    {
        "nama_kegiatan": "Pelatihan Kader Dai Muda IPM Kartasura",
        "hari_offset": 12,
        "tempat": "Aula SMP Muhammadiyah 2 Kartasura (Muhduta)",
        "keterangan": "Pelatihan retorika dakwah dan penguatan ideologi Muhammadiyah bagi pelajar SMP/SMA.",
        "rutin": False,
    },
    {
        "nama_kegiatan": "Musyawarah Cabang (Musycab) PCM Kartasura Periode 2022–2027",
        "hari_offset": -120,
        "tempat": "Auditorium Moh. Djazman UMS",
        "keterangan": "Laporan pertanggungjawaban periode sebelumnya dan pemilihan 9 pimpinan harian periode 2022–2027.",
        "rutin": False,
    },
    {
        "nama_kegiatan": "Resepsi Milad Muhammadiyah ke-112 Ranting Gonilan",
        "hari_offset": -14,
        "tempat": "Halaman Masjid Al-Ikhlas Gonilan",
        "keterangan": "Dihadiri 500 warga persyarikatan dengan santunan dhuafa dan bazar UMKM.",
        "rutin": False,
    },
    {
        "nama_kegiatan": "Workshop Inisiasi Tim P3AK bersama P2M UMS",
        "hari_offset": -20,
        "tempat": "Gedung Pertemuan PRM Jombor",
        "keterangan": "Peningkatan perlindungan perempuan dan anak berbasis komunitas ranting.",
        "rutin": False,
    },
]

TAUTAN_DATA = [
    {
        "nama": "Pimpinan Pusat Muhammadiyah",
        "url": "https://muhammadiyah.or.id",
        "urutan": 1,
    },
    {
        "nama": "PWM Jawa Tengah",
        "url": "https://jateng.muhammadiyah.or.id",
        "urutan": 2,
    },
    {
        "nama": "PDM Kabupaten Sukoharjo",
        "url": "https://pdmsukoharjo.or.id",
        "urutan": 3,
    },
]


def fetch_posts():
    params = {"search": "kartasura", "per_page": 20, "_embed": 1}
    response = requests.get(POSTS_URL, params=params, timeout=20)
    response.raise_for_status()
    posts = response.json()
    if not isinstance(posts, list):
        raise ValueError("Respons WordPress bukan daftar artikel.")
    return posts


def format_article_content(value):
    soup = BeautifulSoup(value or "", "html.parser")
    block_tags = ("p", "h2", "h3", "li")
    blocks = []

    for element in soup.find_all(block_tags):
        if element.find_parent(block_tags):
            continue
        text = element.get_text(" ", strip=True)
        if text:
            blocks.append(text)

    if not blocks:
        text = soup.get_text("\n", strip=True)
        blocks = [line.strip() for line in text.splitlines() if line.strip()]

    return "\n\n".join(blocks)


def clean_html(value):
    return BeautifulSoup(value or "", "html.parser").get_text(" ", strip=True)


def publication_date(post):
    value = post.get("date_gmt") or post.get("date")
    parsed = parse_datetime(value) if value else None
    if parsed is None:
        return timezone.now()
    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def featured_image(post):
    media_items = post.get("_embedded", {}).get("wp:featuredmedia", [])
    if not media_items or not isinstance(media_items[0], dict):
        return ""

    image_url = media_items[0].get("source_url")
    if not image_url:
        return ""

    response = requests.get(image_url, timeout=20)
    response.raise_for_status()
    filename = Path(urlparse(image_url).path).name or f"berita-{post.get('id')}.jpg"
    return ContentFile(response.content, name=filename)


def download_sk_pdf(file_id, filename):
    response = requests.get(
        GOOGLE_DRIVE_DOWNLOAD_URL.format(file_id=file_id),
        timeout=60,
    )
    response.raise_for_status()
    if not response.content.lstrip().startswith(b"%PDF-"):
        raise ValueError("Respons Google Drive bukan berkas PDF.")
    return ContentFile(response.content, name=filename)


def sk_pdf_filename(title):
    normalized_title = title.replace("2022–2027", "2022-2027")
    return f"{slugify(normalized_title)}.pdf"


class Command(BaseCommand):
    help = "Seed data riil PCM Kartasura (Profil, Pimpinan, Ranting, AUM, Agenda, Tautan, Berita, Dokumen)."

    def handle(self, *args, **options):
        self.static_img_dir = (
            Path(__file__).resolve().parents[2] / "static" / "pcm_web" / "images"
        )
        self.seed_profil()
        self.seed_pimpinan()
        self.seed_ranting()
        self.seed_amal_usaha()
        self.seed_agenda()
        self.seed_tautan_terkait()

        try:
            posts = fetch_posts()
        except (requests.RequestException, ValueError) as exc:
            self.stderr.write(self.style.WARNING(f"Gagal mengambil berita WordPress: {exc}"))
        else:
            self.import_news(posts)

        self.import_sk_documents()

    def seed_profil(self):
        profil = ProfilOrganisasi.objects.first()
        hero_file_path = self.static_img_dir / "pimpinan-pcm-hero.jpeg"
        hero_content = None
        if hero_file_path.exists():
            hero_content = ContentFile(hero_file_path.read_bytes(), name="pimpinan-pcm-hero.jpeg")

        defaults = {
            "nama": "Pimpinan Cabang Muhammadiyah Kecamatan Kartasura Kabupaten Sukoharjo",
            "nama_singkat": "PCM Kartasura",
            "tagline": "Istiqomah dan Muhasabah",
            "tentang": (
                "Pimpinan Cabang Muhammadiyah Kartasura adalah organisasi tingkat cabang "
                "di bawah Pimpinan Daerah Muhammadiyah Kabupaten Sukoharjo yang menggerakkan "
                "dakwah Islam amar ma'ruf nahi munkar serta mengelola berbagai Amal Usaha "
                "Muhammadiyah di Kecamatan Kartasura."
            ),
            "sejarah": (
                "Tercatat pada urutan nomor 43 sebagai Gr. (Gerombolan) Kartasura (Kartosoero) "
                "yang telah berdiri sejak akhir tahun 1927 sebagai cabang pertama di wilayah "
                "Sukoharjo sebelum pemisahan administrasi kewilayahan dari Surakarta, dan terus "
                "berkembang hingga memiliki ranting di seluruh 12 kelurahan di Kecamatan "
                "Kartasura serta meresmikan Gedung Dakwah permanen pada 24 Desember 2015."
            ),
            "visi": (
                "Gerakan Islam yang berpedoman pada Alquran dan as-sunnah. Dengan watak tajdid "
                "yang dimilikinya senantiasa istiqamah dan aktif dalam melaksanakan dakwah "
                "Islam amar ma’ruf nahi mungkar di segala bidang."
            ),
            "misi": (
                "Menegakkan keyakinan tauhid yang murni sesuai dengan ajaran Allah swt yang dibawa oleh Rasulullah yang disyariatkan sejak Nabi Nuh hingga Nabi Muhammad SAW.\n"
                "Memahami agama dengan menggunakan akal pikiran sesuai dengan jiwa ajaran Islam untuk menjawab dan menyelesaikan persoalan-persoalan kehidupan yang bersifat duniawi.\n"
                "Menyebarluaskan ajaran Islam yang bersumber pada al-Qur’an sebagai kitab Allah yang terakhir dan Sunnah Nabi untuk umat manusia sebagai penjelasannya.\n"
                "Mewujudkan amalan-amalan agama Islam dalam kehidupan pribadi, keluarga dan Masyarakat, melalui AUM baik Pendidikan, Sosial dan kemasyarakatan."
            ),
            "alamat_sekretariat": (
                "Jl. Slamet Riyadi No. 270B, Sidokerto, Dusun III, Gumpang, Kec. Kartasura, "
                "Kabupaten Sukoharjo, Jawa Tengah, Kotak Pos 57169"
            ),
            "telepon": "08121547207",
            "email": "pcmkartasura@gmail.com",
            "jumlah_anggota_ktam": 364,
        }

        if profil is None:
            if hero_content:
                defaults["gambar_utama"] = hero_content
            ProfilOrganisasi.objects.create(**defaults)
            self.stdout.write(self.style.SUCCESS("Profil PCM Kartasura berhasil dibuat."))
        else:
            for k, v in defaults.items():
                setattr(profil, k, v)
            if hero_content and not profil.gambar_utama:
                profil.gambar_utama = hero_content
            profil.save()
            self.stdout.write(self.style.SUCCESS("Profil PCM Kartasura diperbarui."))

    def seed_pimpinan(self):
        created_count = 0
        for item in PIMPINAN_DATA:
            pimpinan, created = Pimpinan.objects.get_or_create(
                nama=item["nama"],
                defaults={
                    "jabatan": item["jabatan"],
                    "periode": item["periode"],
                    "urutan_tampil": item["urutan"],
                },
            )
            if item.get("foto_file"):
                foto_path = self.static_img_dir / item["foto_file"]
                if foto_path.exists() and not pimpinan.foto:
                    pimpinan.foto.save(
                        item["foto_file"],
                        ContentFile(foto_path.read_bytes()),
                        save=True,
                    )
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"Pimpinan seeded ({len(PIMPINAN_DATA)} data)."))

    def seed_ranting(self):
        for item in RANTING_DATA:
            Ranting.objects.get_or_create(
                nama_ranting=item["nama_ranting"],
                defaults={
                    "ketua": item["ketua"],
                    "alamat": item["alamat"],
                    "telepon": "08121547207",
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Ranting seeded ({len(RANTING_DATA)} PRM)."))

    def seed_amal_usaha(self):
        for item in AUM_DATA:
            AmalUsaha.objects.get_or_create(
                nama=item["nama"],
                defaults={
                    "bidang": item["bidang"],
                    "deskripsi": item["deskripsi"],
                    "alamat": item["alamat"],
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Amal Usaha seeded ({len(AUM_DATA)} AUM)."))

    def seed_agenda(self):
        now = timezone.now()
        for item in AGENDA_DATA:
            waktu = now + timedelta(days=item["hari_offset"])
            Agenda.objects.get_or_create(
                nama_kegiatan=item["nama_kegiatan"],
                defaults={
                    "waktu_mulai": waktu,
                    "tempat": item["tempat"],
                    "keterangan": item["keterangan"],
                    "rutin": item["rutin"],
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Agenda seeded ({len(AGENDA_DATA)} agenda)."))

    def seed_tautan_terkait(self):
        for item in TAUTAN_DATA:
            TautanTerkait.objects.get_or_create(
                nama=item["nama"],
                defaults={
                    "url": item["url"],
                    "urutan": item["urutan"],
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Tautan Terkait seeded ({len(TAUTAN_DATA)} tautan)."))

    def import_news(self, posts):
        posts = [post for post in posts if isinstance(post, dict)]
        source_urls = {post.get("link") for post in posts if post.get("link")}
        old_imports = Berita.objects.filter(
            Q(isi__contains="Sumber asli: https://pdmsukoharjo.or.id/")
            | Q(isi__contains="Sumber: https://pdmsukoharjo.or.id/")
        )
        removed_count = 0
        for berita in old_imports:
            source_marker = (
                "Sumber asli: " if "Sumber asli: " in berita.isi else "Sumber: "
            )
            source_url = berita.isi.rsplit(source_marker, 1)[-1].strip()
            if source_url not in source_urls:
                berita.delete()
                removed_count += 1

        created_count = 0
        existing_count = 0
        for post in posts:
            title = clean_html(post.get("title", {}).get("rendered", ""))[:200]
            if not title:
                continue

            summary = clean_html(post.get("excerpt", {}).get("rendered", ""))
            content = format_article_content(post.get("content", {}).get("rendered", ""))
            source_url = post.get("link", "")
            if source_url:
                content = f"{content}\n\nSumber asli: {source_url}" if content else (
                    f"Sumber asli: {source_url}"
                )

            try:
                image = featured_image(post)
            except requests.RequestException:
                image = ""

            berita, created = Berita.objects.get_or_create(
                judul=title,
                defaults={
                    "ringkasan": summary,
                    "isi": content,
                    "gambar_sampul": image,
                    "tanggal_terbit": publication_date(post),
                    "status_terbit": "terbit",
                },
            )
            if created:
                created_count += 1
            else:
                berita.isi = content
                berita.save(update_fields=["isi"])
                existing_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Impor berita selesai: {created_count} baru, {existing_count} sudah ada."
            )
        )

    def import_sk_documents(self):
        created_count = 0
        existing_count = 0
        failed_count = 0

        for title, file_id, leadership_unit in SK_DOKUMEN:
            filename = sk_pdf_filename(title)
            keterangan = (
                f"Surat keputusan penetapan susunan {leadership_unit} "
                "periode 2022–2027."
            )
            existing = Dokumen.objects.filter(judul=title).first()
            if (
                existing
                and existing.berkas
                and existing.berkas.storage.exists(existing.berkas.name)
                and existing.berkas.name.rsplit("/", 1)[-1] == filename
            ):
                existing_count += 1
                continue

            try:
                pdf_file = download_sk_pdf(file_id, filename)
                dokumen, created = Dokumen.objects.get_or_create(
                    judul=title,
                    defaults={
                        "keterangan": keterangan,
                        "berkas": pdf_file,
                    },
                )
                if created:
                    created_count += 1
                else:
                    dokumen.keterangan = keterangan
                    dokumen.berkas.save(filename, pdf_file, save=False)
                    dokumen.save(update_fields=["keterangan", "berkas"])
                    existing_count += 1
            except (requests.RequestException, ValueError) as exc:
                failed_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Impor SK selesai: {created_count} baru, {existing_count} tersedia, {failed_count} gagal."
            )
        )
