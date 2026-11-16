from django.urls import path
from . import views

# Daftar routing URL utama aplikasi
urlpatterns = [
    path('dashboard/panitia/', views.dashboard_panitia, name='dashboard_panitia'),
    path('cari/', views.cari_berita, name='cari_berita'),
    path('agenda/', views.halaman_agenda, name='agenda'),
    path('kontak/', views.halaman_kontak, name='kontak'),
    path('amal-usaha/', views.halaman_amal_usaha, name='amal_usaha'),
    path('ranting/', views.halaman_ranting, name='ranting'),
    # Rute halaman utama (Beranda) yang mengarah ke fungsi beranda di views.py
    path('', views.beranda, name='beranda'),
    path('profil/', views.profil_pcm, name='profil_pcm'),
    path('pimpinan/', views.pimpinan_pcm, name='pimpinan_pcm'),
]

