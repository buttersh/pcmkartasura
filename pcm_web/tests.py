import tempfile
from datetime import timedelta

from django.contrib.admin.sites import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .admin import PesanMasukAdmin, ProfilOrganisasiAdmin
from .context_processors import profil_dan_tautan
from .forms import KontakForm
from .management.commands.seed_pcm import format_article_content, sk_pdf_filename
from .models import (
    Agenda,
    AmalUsaha,
    Berita,
    Dokumen,
    PesanMasuk,
    Pimpinan,
    ProfilOrganisasi,
    Ranting,
    TautanTerkait,
)


class BeritaDokumenViewTests(TestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.media_dir.cleanup)
        media_settings = override_settings(MEDIA_ROOT=self.media_dir.name)
        media_settings.enable()
        self.addCleanup(media_settings.disable)

    def buat_berita(self, judul='Berita uji', **kwargs):
        defaults = {
            'judul': judul,
            'ringkasan': 'Ringkasan berita uji',
            'isi': 'Isi berita uji',
            'gambar_sampul': SimpleUploadedFile('sampul.jpg', b'isi gambar'),
            'tanggal_terbit': timezone.now() - timedelta(days=1),
            'status_terbit': 'terbit',
        }
        defaults.update(kwargs)
        return Berita.objects.create(**defaults)

    def test_daftar_berita_dan_unduhan_berhasil(self):
        self.buat_berita()
        Dokumen.objects.create(
            judul='Dokumen uji',
            keterangan='Keterangan dokumen uji',
            berkas=SimpleUploadedFile('dokumen.pdf', b'isi dokumen'),
        )

        self.assertEqual(self.client.get(reverse('pcm_web:daftar_berita')).status_code, 200)
        self.assertEqual(self.client.get(reverse('pcm_web:daftar_unduhan')).status_code, 200)

    def test_berita_draf_tidak_dapat_dilihat(self):
        berita = self.buat_berita(status_terbit='draf')
        response = self.client.get(reverse('pcm_web:detail_berita', args=[berita.slug]))
        self.assertEqual(response.status_code, 404)

    def test_berita_masa_depan_tidak_dapat_dilihat(self):
        berita = self.buat_berita(tanggal_terbit=timezone.now() + timedelta(days=1))
        response = self.client.get(reverse('pcm_web:detail_berita', args=[berita.slug]))
        self.assertEqual(response.status_code, 404)

    def test_detail_berita_menampilkan_tiga_berita_lain(self):
        berita = self.buat_berita(judul='Berita utama')
        for nomor in range(4):
            self.buat_berita(judul=f'Berita lain {nomor}')

        response = self.client.get(reverse('pcm_web:detail_berita', args=[berita.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['berita_lainnya']), 3)

    def test_detail_berita_memisahkan_ringkasan_isi_dan_sumber(self):
        source_url = 'https://pdmsukoharjo.or.id/berita-uji/'
        berita = self.buat_berita(
            ringkasan='Ringkasan yang tidak ditampilkan di detail',
            isi=f'Paragraf pertama.\n\nParagraf kedua.\n\nSumber asli: {source_url}',
        )

        response = self.client.get(reverse('pcm_web:detail_berita', args=[berita.slug]))
        self.assertNotContains(response, 'Ringkasan yang tidak ditampilkan di detail')
        self.assertEqual(response.context['isi_artikel'], 'Paragraf pertama.\n\nParagraf kedua.')
        self.assertEqual(response.context['sumber_url'], source_url)
        self.assertContains(response, f'href="{source_url}"')
        self.assertContains(response, 'target="_blank"')

    def test_format_isi_artikel_memisahkan_blok_dan_teks_tanpa_tag(self):
        html = '<p>Pertama</p><h2>Judul bagian</h2><ul><li>Daftar</li></ul>'
        self.assertEqual(
            format_article_content(html),
            'Pertama\n\nJudul bagian\n\nDaftar',
        )
        self.assertEqual(
            format_article_content('Baris pertama\nBaris kedua'),
            'Baris pertama\n\nBaris kedua',
        )

    def test_slug_berita_kembar_dibuat_unik(self):
        berita_pertama = self.buat_berita(judul='Berita Kembar')
        berita_kedua = self.buat_berita(judul='Berita Kembar')
        self.assertEqual(berita_pertama.slug, 'berita-kembar')
        self.assertEqual(berita_kedua.slug, 'berita-kembar-1')

    def test_daftar_berita_menggunakan_enam_item_per_halaman(self):
        for nomor in range(7):
            self.buat_berita(judul=f'Berita {nomor}')

        response = self.client.get(reverse('pcm_web:daftar_berita'))
        self.assertEqual(len(response.context['berita_page']), 6)
        self.assertEqual(response.context['berita_page'].paginator.count, 7)
        self.assertEqual(response.context['berita_page'].paginator.num_pages, 2)

    def test_hal_unduhan_mengelompokkan_dan_menautkan_dokumen(self):
        cabang = Dokumen.objects.create(
            judul='SK PDM Sukoharjo Susunan PCM Kartasura 2022–2027',
            keterangan='Penetapan susunan PCM Kartasura periode 2022–2027.',
            berkas=SimpleUploadedFile('sk-cabang.pdf', b'%PDF-cabang'),
        )
        ranting = Dokumen.objects.create(
            judul='SK PCM Kartasura Susunan PRM Ngemplak 2022–2027',
            keterangan='Penetapan susunan PRM Ngemplak periode 2022–2027.',
            berkas=SimpleUploadedFile('sk-ranting.pdf', b'%PDF-ranting'),
        )

        response = self.client.get(reverse('pcm_web:daftar_unduhan'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SK Tingkat Cabang — PDM Sukoharjo')
        self.assertContains(response, 'SK Pimpinan Ranting Muhammadiyah (PRM)')
        self.assertContains(response, 'Pratinjau')
        self.assertContains(response, 'Unduh PDF')
        self.assertContains(response, 'target="_blank"')
        self.assertContains(response, cabang.berkas.url)
        self.assertContains(response, ranting.berkas.url)

    def test_nama_file_sk_mengandung_tanda_hubung_periode(self):
        self.assertEqual(
            sk_pdf_filename('SK PCM Kartasura Susunan PRM Ngemplak 2022–2027'),
            'sk-pcm-kartasura-susunan-prm-ngemplak-2022-2027.pdf',
        )


class PublicPagesTests(TestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.media_dir.cleanup)
        media_settings = override_settings(MEDIA_ROOT=self.media_dir.name)
        media_settings.enable()
        self.addCleanup(media_settings.disable)

        self.profil = ProfilOrganisasi.objects.create(
            nama='Pimpinan Cabang Muhammadiyah Kartasura',
            nama_singkat='PCM Kartasura',
            tagline='Istiqomah dan Muhasabah',
            tentang='Organisasi dakwah Islam di Kartasura.',
            sejarah='Berdiri sejak akhir 1927.',
            visi='Gerakan Islam tajdid.',
            misi='Menegakkan tauhid.\nMenyebarluaskan Islam.',
            alamat_sekretariat='Jl. Slamet Riyadi No. 270B, Gumpang, Kartasura',
            telepon='08121547207',
            email='pcmkartasura@gmail.com',
            jumlah_anggota_ktam=364,
            gambar_utama=SimpleUploadedFile('hero.jpg', b'hero bytes'),
        )
        self.pimpinan = Pimpinan.objects.create(
            nama='Ihwan Susila, Ph.D.',
            jabatan='Ketua',
            periode='2022–2027',
            urutan_tampil=1,
        )
        self.ranting = Ranting.objects.create(
            nama_ranting='Kartasura',
            ketua='Achmad Fatoni, M.Pd',
            alamat='Kelurahan Kartasura',
            telepon='08121547207',
        )
        self.aum = AmalUsaha.objects.create(
            nama='MIM Pucangan',
            bidang='sekolah',
            deskripsi='Madrasah Ibtidaiyah Muhammadiyah.',
            alamat='Pucangan, Kartasura',
        )
        self.tautan = TautanTerkait.objects.create(
            nama='PP Muhammadiyah',
            url='https://muhammadiyah.or.id',
            urutan=1,
        )

    def test_semua_halaman_publik_berstatus_200(self):
        urls = [
            reverse('pcm_web:beranda'),
            reverse('pcm_web:profil_pcm'),
            reverse('pcm_web:pimpinan_pcm'),
            reverse('pcm_web:ranting'),
            reverse('pcm_web:amal_usaha'),
            reverse('pcm_web:agenda'),
            reverse('pcm_web:daftar_berita'),
            reverse('pcm_web:daftar_unduhan'),
            reverse('pcm_web:kontak'),
            reverse('pcm_web:cari_berita'),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_beranda_memuat_statistik_dan_data_profil(self):
        response = self.client.get(reverse('pcm_web:beranda'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PCM Kartasura')
        self.assertContains(response, '364')
        self.assertEqual(response.context['jumlah_ranting'], 1)
        self.assertEqual(response.context['jumlah_aum'], 1)

    def test_halaman_profil_memuat_misi_sebagai_daftar(self):
        response = self.client.get(reverse('pcm_web:profil_pcm'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Menegakkan tauhid.')
        self.assertContains(response, 'Menyebarluaskan Islam.')
        self.assertEqual(len(response.context['misi_list']), 2)

    def test_halaman_pimpinan_diurutkan_berdasarkan_urutan_tampil(self):
        Pimpinan.objects.create(
            nama='Drs. Abdul Fatah Bintoro',
            jabatan='Sekretaris',
            periode='2022–2027',
            urutan_tampil=2,
        )
        response = self.client.get(reverse('pcm_web:pimpinan_pcm'))
        self.assertEqual(response.status_code, 200)
        pimpinan_list = list(response.context['daftar_pimpinan'])
        self.assertEqual(pimpinan_list[0].nama, 'Ihwan Susila, Ph.D.')
        self.assertEqual(pimpinan_list[1].nama, 'Drs. Abdul Fatah Bintoro')

    def test_halaman_amal_usaha_dikelompokkan_dan_dapat_difilter(self):
        response = self.client.get(reverse('pcm_web:amal_usaha') + '?kategori=sekolah')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'MIM Pucangan')

    def test_agenda_memisahkan_mendatang_dan_selesai(self):
        sekarang = timezone.now()
        Agenda.objects.create(
            nama_kegiatan='Agenda Mendatang',
            waktu_mulai=sekarang + timedelta(days=2),
            tempat='Gedung Dakwah',
        )
        Agenda.objects.create(
            nama_kegiatan='Agenda Selesai',
            waktu_mulai=sekarang - timedelta(days=2),
            tempat='Aula UMS',
        )
        response = self.client.get(reverse('pcm_web:agenda'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['agenda_mendatang']), 1)
        self.assertEqual(len(response.context['agenda_selesai']), 1)


class KontakFormTests(TestCase):
    def test_form_kontak_valid_menyimpan_pesan_dan_pesan_sukses(self):
        data = {
            'nama': 'Ahmad Fauzi',
            'email': 'ahmad@example.com',
            'subjek': 'Pertanyaan Kegiatan',
            'pesan': 'Bagaimana cara mendaftar pengajian Ahad Pagi?',
        }
        form = KontakForm(data=data)
        self.assertTrue(form.is_valid())

        response = self.client.post(reverse('pcm_web:kontak'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Terima kasih, pesan Anda berhasil dikirim!')

        pesan = PesanMasuk.objects.first()
        self.assertIsNotNone(pesan)
        self.assertEqual(pesan.nama, 'Ahmad Fauzi')
        self.assertEqual(pesan.email, 'ahmad@example.com')
        self.assertFalse(pesan.sudah_dibaca)

    def test_form_kontak_kosong_tidak_valid(self):
        data = {'nama': '', 'email': 'bukan-email', 'subjek': '', 'pesan': ''}
        form = KontakForm(data=data)
        self.assertFalse(form.is_valid())


class AdminDanContextProcessorTests(TestCase):
    def test_context_processor_menyediakan_profil_dan_tautan(self):
        profil = ProfilOrganisasi.objects.create(
            nama='PCM Kartasura',
            nama_singkat='PCM KTS',
            tagline='Berdakwah',
            tentang='Tentang',
            sejarah='Sejarah',
            visi='Visi',
            misi='Misi',
            alamat_sekretariat='Alamat',
            telepon='08123',
            email='pcm@example.com',
            jumlah_anggota_ktam=100,
            gambar_utama=SimpleUploadedFile('hero.jpg', b'bytes'),
        )
        tautan = TautanTerkait.objects.create(nama='PP Muhammadiyah', url='https://muhammadiyah.or.id', urutan=1)

        rf = RequestFactory()
        request = rf.get('/')
        ctx = profil_dan_tautan(request)

        self.assertEqual(ctx['profil'], profil)
        self.assertIn(tautan, ctx['tautan_terkait'])

    def test_profil_organisasi_tidak_bisa_ditambah_lebih_dari_satu(self):
        site = AdminSite()
        admin_obj = ProfilOrganisasiAdmin(ProfilOrganisasi, site)
        rf = RequestFactory()
        request = rf.get('/')

        self.assertTrue(admin_obj.has_add_permission(request))

        ProfilOrganisasi.objects.create(
            nama='PCM Kartasura',
            nama_singkat='PCM KTS',
            tagline='Berdakwah',
            tentang='Tentang',
            sejarah='Sejarah',
            visi='Visi',
            misi='Misi',
            alamat_sekretariat='Alamat',
            telepon='08123',
            email='pcm@example.com',
            jumlah_anggota_ktam=100,
            gambar_utama=SimpleUploadedFile('hero.jpg', b'bytes'),
        )

        self.assertFalse(admin_obj.has_add_permission(request))
        self.assertFalse(admin_obj.has_delete_permission(request))

    def test_pesan_masuk_baca_saja_di_admin(self):
        site = AdminSite()
        admin_obj = PesanMasukAdmin(PesanMasuk, site)
        rf = RequestFactory()
        request = rf.get('/')
        self.assertFalse(admin_obj.has_add_permission(request))
