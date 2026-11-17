from django.contrib import admin
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
    ProfilCabang,
    StrukturPengurus,
    AUM,
    PRM,
    BeritaInformasi,
    PanitiaKegiatan,
)

admin.site.site_header = "Admin Website PCM Kartasura"
admin.site.site_title = "Admin PCM Kartasura"
admin.site.index_title = "Panel Kelola Website PCM Kartasura"


@admin.register(ProfilOrganisasi)
class ProfilOrganisasiAdmin(admin.ModelAdmin):
    list_display = ('nama_singkat', 'telepon', 'email', 'jumlah_anggota_ktam')

    def has_add_permission(self, request):
        return not ProfilOrganisasi.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Pimpinan)
class PimpinanAdmin(admin.ModelAdmin):
    list_display = ('nama', 'jabatan', 'periode', 'urutan_tampil')
    ordering = ('urutan_tampil', 'nama')
    search_fields = ('nama', 'jabatan', 'periode')


@admin.register(Ranting)
class RantingAdmin(admin.ModelAdmin):
    list_display = ('nama_ranting', 'ketua', 'telepon', 'alamat')
    search_fields = ('nama_ranting', 'ketua', 'alamat')


@admin.register(AmalUsaha)
class AmalUsahaAdmin(admin.ModelAdmin):
    list_display = ('nama', 'bidang', 'alamat', 'deskripsi')
    list_filter = ('bidang',)
    search_fields = ('nama', 'alamat', 'deskripsi')


@admin.register(Berita)
class BeritaAdmin(admin.ModelAdmin):
    list_display = ('judul', 'tanggal_terbit', 'status_terbit')
    list_filter = ('status_terbit', 'tanggal_terbit')
    search_fields = ('judul', 'ringkasan', 'isi')
    prepopulated_fields = {'slug': ('judul',)}
    date_hierarchy = 'tanggal_terbit'


@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    list_display = ('nama_kegiatan', 'waktu_mulai', 'tempat', 'rutin')
    list_filter = ('rutin', 'waktu_mulai')
    search_fields = ('nama_kegiatan', 'tempat', 'keterangan')


@admin.register(Dokumen)
class DokumenAdmin(admin.ModelAdmin):
    list_display = ('judul', 'tanggal_unggah')
    list_filter = ('tanggal_unggah',)
    search_fields = ('judul', 'keterangan')


@admin.register(PesanMasuk)
class PesanMasukAdmin(admin.ModelAdmin):
    list_display = ('nama', 'email', 'subjek', 'waktu_kirim', 'sudah_dibaca')
    list_filter = ('sudah_dibaca', 'waktu_kirim')
    search_fields = ('nama', 'email', 'subjek', 'pesan')
    readonly_fields = ('nama', 'email', 'subjek', 'pesan', 'waktu_kirim')

    def has_add_permission(self, request):
        return False


@admin.register(TautanTerkait)
class TautanTerkaitAdmin(admin.ModelAdmin):
    list_display = ('nama', 'url', 'urutan')
    ordering = ('urutan',)
    search_fields = ('nama', 'url')


# Model tambahan untuk kompatibilitas jika masih ada data
admin.site.register([ProfilCabang, StrukturPengurus, AUM, PRM, BeritaInformasi, PanitiaKegiatan])
