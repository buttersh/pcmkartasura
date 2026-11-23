from django.urls import path
from . import views

app_name = 'pcm_web'

urlpatterns = [
    path('', views.beranda, name='beranda'),
    path('profil/', views.profil_pcm, name='profil_pcm'),
    path('profil/detail/', views.profil_pcm, name='profil'),
    path('pimpinan/', views.pimpinan_pcm, name='pimpinan_pcm'),
    path('pimpinan/detail/', views.pimpinan_pcm, name='pimpinan'),
    path('ranting/', views.halaman_ranting, name='ranting'),
    path('amal-usaha/', views.halaman_amal_usaha, name='amal_usaha'),
    path('berita/', views.daftar_berita, name='daftar_berita'),
    path('berita/semua/', views.daftar_berita, name='berita'),
    path('berita/<slug:slug>/', views.detail_berita, name='detail_berita'),
    path('agenda/', views.halaman_agenda, name='agenda'),
    path('unduhan/', views.daftar_unduhan, name='daftar_unduhan'),
    path('kontak/', views.halaman_kontak, name='kontak'),
    path('cari/', views.cari_berita, name='cari_berita'),
    path('dashboard/panitia/', views.dashboard_panitia, name='dashboard_panitia'),
]
