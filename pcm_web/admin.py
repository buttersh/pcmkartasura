from django.contrib import admin
from .models import (
    Agenda,
    PesanMasuk,
    ProfilCabang,
    StrukturPengurus,
    AUM,
    PRM,
    BeritaInformasi,
    PanitiaKegiatan,
    ProfilOrganisasi,
    Pimpinan,
    AmalUsaha,
    Ranting,
    Berita,
    Dokumen,
)

admin.site.register(Agenda)
admin.site.register(PesanMasuk)


# Koneksi dengan ProfilOrganisasi dan Pimpinan
@admin.register(ProfilOrganisasi)
class ProfilOrganisasiAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not ProfilOrganisasi.objects.exists()


@admin.register(AmalUsaha)
class AmalUsahaAdmin(admin.ModelAdmin):
    list_display = ('nama', 'bidang', 'alamat', 'deskripsi')
    fields = ('nama', 'bidang', 'alamat', 'deskripsi')
    list_filter = ('bidang',)
    search_fields = ('nama', 'alamat', 'deskripsi')


@admin.register(Ranting)
class RantingAdmin(admin.ModelAdmin):
    list_display = ('nama_ranting', 'ketua', 'telepon', 'alamat')
    search_fields = ('nama_ranting', 'ketua', 'alamat')


@admin.register(Berita)
class BeritaAdmin(admin.ModelAdmin):
    list_display = ('judul', 'tanggal_terbit', 'status_terbit')
    list_filter = ('status_terbit', 'tanggal_terbit')
    search_fields = ('judul', 'ringkasan', 'isi')
    prepopulated_fields = {'slug': ('judul',)}
    date_hierarchy = 'tanggal_terbit'


@admin.register(Dokumen)
class DokumenAdmin(admin.ModelAdmin):
    list_display = ('judul', 'tanggal_unggah')
    list_filter = ('tanggal_unggah',)
    search_fields = ('judul', 'keterangan')


admin.site.register(Pimpinan)
admin.site.register([ProfilCabang, StrukturPengurus, AUM, PRM, BeritaInformasi, PanitiaKegiatan])
