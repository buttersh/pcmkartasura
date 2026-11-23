from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class ProfilCabang(models.Model):
    nama_pcm = models.CharField(max_length=150, default="Pimpinan Cabang Muhammadiyah Kartasura")
    sejarah = models.TextField(blank=True)
    sambutan_ketua = models.TextField(blank=True)
    foto_ketua = models.ImageField(upload_to="profil/", blank=True, null=True)
    quote_harian = models.TextField(blank=True)
    alamat = models.TextField(blank=True)
    kontak = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Profil Cabang"
        verbose_name_plural = "Profil Cabang"

    def __str__(self):
        return self.nama_pcm


class StrukturPengurus(models.Model):
    TIPE_CHOICES = [("PH", "Pimpinan Harian"), ("Majelis", "Majelis"), ("Ortom", "Organisasi Otonom")]
    nama = models.CharField(max_length=120)
    jabatan = models.CharField(max_length=120)
    tipe = models.CharField(max_length=10, choices=TIPE_CHOICES, default="PH")
    foto = models.ImageField(upload_to="pengurus/", blank=True, null=True)
    urutan = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["urutan", "nama"]
        verbose_name_plural = "Struktur Pengurus"

    def __str__(self):
        return f"{self.nama} - {self.jabatan}"


class AUM(models.Model):
    KATEGORI_CHOICES = [("Pendidikan", "Pendidikan"), ("Ekonomi", "Ekonomi"), ("Kesehatan", "Kesehatan"), ("Sosial", "Sosial")]
    nama = models.CharField(max_length=150)
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES)
    deskripsi = models.TextField(blank=True)
    alamat = models.TextField(blank=True)

    class Meta:
        ordering = ["kategori", "nama"]
        verbose_name = "Amal Usaha Muhammadiyah"
        verbose_name_plural = "Amal Usaha Muhammadiyah"

    def __str__(self):
        return self.nama


class PRM(models.Model):
    nama_desa = models.CharField(max_length=120)
    ketua_ranting = models.CharField(max_length=120, blank=True)
    alamat_sekretariat = models.TextField(blank=True)

    class Meta:
        ordering = ["nama_desa"]
        verbose_name = "Pimpinan Ranting Muhammadiyah"
        verbose_name_plural = "Pimpinan Ranting Muhammadiyah"

    def __str__(self):
        return self.nama_desa


class BeritaInformasi(models.Model):
    judul = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    isi = models.TextField()
    gambar = models.ImageField(upload_to="berita/", blank=True, null=True)
    tanggal_publikasi = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-tanggal_publikasi"]
        verbose_name_plural = "Berita dan Informasi"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.judul) or "berita"
            candidate, number = base, 1
            while BeritaInformasi.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{number}"
                number += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.judul


class PanitiaKegiatan(models.Model):
    nama_kegiatan = models.CharField(max_length=180)
    divisi = models.CharField(max_length=120)
    nama_anggota = models.CharField(max_length=120)
    peran = models.CharField(max_length=120, blank=True)
    tugas_selesai = models.BooleanField(default=False)

    class Meta:
        ordering = ["nama_kegiatan", "divisi", "nama_anggota"]
        verbose_name_plural = "Panitia Kegiatan"

    def __str__(self):
        return f"{self.nama_kegiatan} — {self.nama_anggota}"


# Model lama dipertahankan agar data dan halaman yang sudah ada tetap berfungsi.
class ProfilOrganisasi(models.Model):
    nama = models.CharField(max_length=100)
    nama_singkat = models.CharField(max_length=50)
    tagline = models.CharField(max_length=200)
    tentang = models.TextField()
    sejarah = models.TextField()
    visi = models.TextField()
    misi = models.TextField(help_text="Tulis satu misi per baris")
    alamat_sekretariat = models.TextField()
    telepon = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    jumlah_anggota_ktam = models.IntegerField(default=0)
    gambar_utama = models.ImageField(upload_to="profil/")

    class Meta:
        verbose_name_plural = "Profil Organisasi"

    def save(self, *args, **kwargs):
        if self.pk is None and ProfilOrganisasi.objects.exists():
            raise ValueError("Profil Organisasi hanya boleh memiliki satu baris data.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama


class Pimpinan(models.Model):
    nama = models.CharField(max_length=100)
    jabatan = models.CharField(max_length=100)
    periode = models.CharField(max_length=20, help_text="Misal: 2022-2027")
    foto = models.ImageField(upload_to="pimpinan/", blank=True, null=True)
    urutan_tampil = models.IntegerField(default=0)

    class Meta:
        ordering = ["urutan_tampil"]
        verbose_name_plural = "Pimpinan (lama)"

    def __str__(self):
        return f"{self.nama} - {self.jabatan}"


class Ranting(models.Model):
    nama_ranting = models.CharField(max_length=100)
    ketua = models.CharField(max_length=100)
    alamat = models.TextField()
    telepon = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Ranting (lama)"

    def __str__(self):
        return self.nama_ranting


class AmalUsaha(models.Model):
    BIDANG_CHOICES = [
        ("klinik", "Klinik & Balai Pengobatan"),
        ("lazismu", "LazisMu"),
        ("masjid", "Masjid / Musholla"),
        ("panti-asuhan", "Panti Asuhan"),
        ("pondok-pesantren", "Pondok Pesantren"),
        ("rumah-sakit", "Rumah Sakit"),
        ("sekolah", "Sekolah / Madrasah"),
        ("toko", "Toko"),
    ]
    nama = models.CharField(max_length=100)
    bidang = models.CharField(max_length=20, choices=BIDANG_CHOICES)
    kepala = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Kepala Sekolah / Pimpinan'
    )
    deskripsi = models.TextField()
    alamat = models.TextField()
    link_maps = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Link Google Maps'
    )
    gambar = models.ImageField(
        upload_to='amal_usaha/',
        blank=True,
        null=True,
        verbose_name='Foto Amal Usaha'
    )

    class Meta:
        verbose_name_plural = "Amal Usaha (lama)"

    def __str__(self):
        return f"{self.nama} ({self.get_bidang_display()})"


class BeritaQuerySet(models.QuerySet):
    def terbit(self):
        return self.filter(
            status_terbit="terbit",
            tanggal_terbit__lte=timezone.now(),
        )


class Berita(models.Model):
    STATUS_CHOICES = [("draf", "Draf"), ("terbit", "Terbit")]
    judul = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    ringkasan = models.TextField()
    isi = models.TextField()
    gambar_sampul = models.ImageField(upload_to="berita/")
    tanggal_terbit = models.DateTimeField()
    status_terbit = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draf")

    objects = BeritaQuerySet.as_manager()

    class Meta:
        verbose_name_plural = "Berita (lama)"
        ordering = ["-tanggal_terbit"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.judul) or "berita"
            candidate, number = base, 1
            while Berita.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{number}"
                number += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.judul


class Agenda(models.Model):
    nama_kegiatan = models.CharField(max_length=200)
    waktu_mulai = models.DateTimeField()
    tempat = models.CharField(max_length=200)
    keterangan = models.TextField(blank=True, null=True)
    rutin = models.BooleanField(default=False, help_text="Centang jika ini kegiatan rutin mingguan")

    def __str__(self):
        return self.nama_kegiatan


class Dokumen(models.Model):
    judul = models.CharField(max_length=200)
    keterangan = models.TextField()
    berkas = models.FileField(upload_to="dokumen/")
    tanggal_unggah = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Dokumen"

    def __str__(self):
        return self.judul


class PesanMasuk(models.Model):
    nama = models.CharField(max_length=100)
    email = models.EmailField()
    subjek = models.CharField(max_length=200)
    pesan = models.TextField()
    waktu_kirim = models.DateTimeField(auto_now_add=True)
    sudah_dibaca = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Pesan Masuk"
        ordering = ["-waktu_kirim"]

    def __str__(self):
        return f"Dari: {self.nama} - {self.subjek}"


class TautanTerkait(models.Model):
    nama = models.CharField(max_length=100)
    url = models.URLField()
    urutan = models.IntegerField(default=0)

    class Meta:
        ordering = ["urutan"]
        verbose_name_plural = "Tautan Terkait"

    def __str__(self):
        return self.nama
