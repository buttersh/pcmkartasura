from django import urls
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta  # Tambahan untuk menghitung jarak hari
from django.db.models import Q
from django.templatetags.static import static
from django.utils import timezone
from .models import (Berita, Agenda, PesanMasuk, ProfilOrganisasi,
                     Pimpinan, AUM, PRM, BeritaInformasi, PanitiaKegiatan,
                     AmalUsaha, Ranting)


PROFIL_PCM_DEFAULTS = {
    'nama': 'Pimpinan Cabang Muhammadiyah Kecamatan Kartasura Kabupaten Sukoharjo',
    'nama_singkat': 'PCM Kartasura',
    'tagline': 'Istiqomah dan Muhasabah',
    'tentang': "Pimpinan Cabang Muhammadiyah Kartasura adalah organisasi tingkat cabang di bawah Pimpinan Daerah Muhammadiyah Kabupaten Sukoharjo yang menggerakkan dakwah Islam amar ma'ruf nahi munkar serta mengelola berbagai Amal Usaha Muhammadiyah di Kecamatan Kartasura.",
    'sejarah': 'Tercatat pada urutan nomor 43 sebagai Gr. (Gerombolan) Kartasura (Kartosoero) yang telah berdiri sejak akhir tahun 1927 sebagai cabang pertama di wilayah Sukoharjo sebelum pemisahan administrasi kewilayahan dari Surakarta, dan terus berkembang hingga memiliki ranting di seluruh 12 kelurahan di Kecamatan Kartasura serta meresmikan Gedung Dakwah permanen pada 24 Desember 2015.',
    'visi': 'Gerakan Islam yang berpedoman pada Alquran dan as-sunnah. Dengan watak tajdid yang dimilikinya senantiasa istiqamah dan aktif dalam melaksanakan dakwah Islam amar ma’ruf nahi mungkar di segala bidang.',
    'misi': '\n'.join([
        'Menegakkan keyakinan tauhid yang murni sesuai dengan ajaran Allah swt yang dibawa oleh Rasulullah yang disyariatkan sejak Nabi Nuh hingga Nabi Muhammad SAW.',
        'Memahami agama dengan menggunakan akal pikiran sesuai dengan jiwa ajaran Islam untuk menjawab dan menyelesaikan persoalan-persoalan kehidupan yang bersifat duniawi.',
        'Menyebarluaskan ajaran Islam yang bersumber pada al-Qur’an sebagai kitab Allah yang terakhir dan Sunnah Nabi untuk umat manusia sebagai penjelasannya.',
        'Mewujudkan amalan-amalan agama Islam dalam kehidupan pribadi, keluarga dan Masyarakat, melalui AUM baik Pendidikan, Sosial dan kemasyarakatan.',
    ]),
    'alamat_sekretariat': 'Jl. Slamet Riyadi No. 270B, Sidokerto, Dusun III, Gumpang, Kec. Kartasura, Kabupaten Sukoharjo, Jawa Tengah, Kotak Pos 57169',
    'telepon': '008121547207',
    'email': '',
    'jumlah_anggota_ktam': 364,
}

PIMPINAN_PCM_DEFAULTS = [
    {'nama': 'Ihwan Susila, S.E., M.Si., Ph.D.', 'jabatan': 'Ketua'},
    {'nama': 'Drs. Abdul Fatah Bintoro, M.Pd.', 'jabatan': 'Sekretaris'},
    {'nama': 'Prof. Dr. Kuswaji Dwi Priyono, M.Si.', 'jabatan': 'Bendahara'},
    {'nama': 'Dr. Abdullah Mahmud, M.Ag.', 'jabatan': 'Wakil Ketua — Tarjih, Tabligh dan Pembinaan Masjid'},
    {'nama': 'H. Asrori, S.Pd.I.', 'jabatan': 'Wakil Ketua — Pendidikan'},
    {'nama': 'Rahmad Basuki', 'jabatan': 'Wakil Ketua — Pembinaan Kader dan Sumber Daya Insani'},
    {'nama': 'Prof. Dr. H. Bambang Sumardjoko, M.Pd.', 'jabatan': 'Wakil Ketua — PKU dan Kesejahteraan Sosial'},
    {'nama': 'Dr. H. Abdul Aziz Nugroho Pratama, M.M.', 'jabatan': 'Wakil Ketua — Ekonomi dan Pemberdayaan Masyarakat'},
    {'nama': 'Drs. Muhammad Widodo, M.Pd.', 'jabatan': 'Wakil Ketua — Hukum, Lingkungan Hidup, Pustaka dan Informasi'},
]

PIMPINAN_PHOTO_DEFAULTS = [
    ('ihwan susila', 'pcm_web/images/ihwan-susila.jpg'),
    ('abdul fatah bintoro', 'pcm_web/images/abdul-fatah-bintoro.jpg'),
    ('kuswaji dwi priyono', 'pcm_web/images/kuswaji-dwi-priyono.jpg'),
    ('abdullah mahmud', 'pcm_web/images/abdullah-mahmud.jpg'),
    ('bambang sumardjoko', 'pcm_web/images/bambang-sumardjoko.jpg'),
]

RANTING_PCM_DEFAULTS = [
    {'nama_desa': 'Kartasura', 'ketua_ranting': 'Achmad Fatoni, M.Pd'},
    {'nama_desa': 'Ngemplak', 'ketua_ranting': 'Suramto, S.Pd.'},
    {'nama_desa': 'Pucangan', 'ketua_ranting': 'Drs. H. Maryanto, MM'},
    {'nama_desa': 'Kertonatan', 'ketua_ranting': "Drs. Ali Sa'bani, M.Pd.I"},
    {'nama_desa': 'Wirogunan', 'ketua_ranting': 'Dr. H. Dzanurusyamsi, M.H.'},
    {'nama_desa': 'Ngabeyan', 'ketua_ranting': 'Muhammad Rochjani, S.Pd'},
    {'nama_desa': 'Singopuran', 'ketua_ranting': 'H. Nur Hasan, M.T.'},
    {'nama_desa': 'Pabelan', 'ketua_ranting': 'apt. Gunawan Setiyadi, M.Sc.'},
    {'nama_desa': 'Gonilan', 'ketua_ranting': 'Drs. Supriyadi'},
    {'nama_desa': 'Makamhaji', 'ketua_ranting': 'Drs. Edy Siyamto, M.Si.'},
    {'nama_desa': 'Gumpang', 'ketua_ranting': 'Muhammad Anis Sumaji, S.Ag., M.PI'},
    {'nama_desa': 'Ngadirejo', 'ketua_ranting': 'Agus Mustamar, SH.I.'},
]


def _profil_pcm_untuk_tampilan():
    """Return saved profile data, filling missing fields with supplied PCM details."""
    profil = ProfilOrganisasi.objects.first()
    if profil is None:
        return ProfilOrganisasi(**PROFIL_PCM_DEFAULTS)

    for field, value in PROFIL_PCM_DEFAULTS.items():
        if field in {'misi', 'alamat_sekretariat', 'telepon', 'email'}:
            # These details were explicitly confirmed for the public PCM profile.
            setattr(profil, field, value)
        elif field == 'jumlah_anggota_ktam':
            if not getattr(profil, field):
                setattr(profil, field, value)
        elif not getattr(profil, field):
            setattr(profil, field, value)
    return profil


def _daftar_prm_untuk_tampilan():
    """Merge SK-derived PRM display data with saved rows, without writing to DB."""
    tersimpan = list(PRM.objects.all())
    menurut_nama = {prm.nama_desa.strip().casefold(): prm for prm in tersimpan}
    daftar = []

    for data_default in RANTING_PCM_DEFAULTS:
        nama_kunci = data_default['nama_desa'].casefold()
        prm = menurut_nama.pop(nama_kunci, None)
        if prm is None:
            prm = PRM(**data_default)
        elif not prm.ketua_ranting:
            prm.ketua_ranting = data_default['ketua_ranting']
        daftar.append(prm)

    daftar.extend(menurut_nama.values())
    return daftar

def cari_berita(request):
    # Mengambil kata kunci dari URL (misal: ?q=pengajian)
    query = request.GET.get('q')
    hasil = None
    
    if query:
        # Mencari berita yang judul ATAU isinya mengandung kata kunci, dan statusnya sudah 'terbit'
        hasil = Berita.objects.terbit().filter(
            Q(judul__icontains=query) | Q(isi__icontains=query),
        )
        
    return render(request, 'pcm_web/cari.html', {'query': query, 'hasil': hasil})


def halaman_agenda(request):
    waktu_sekarang = timezone.now()
    
    # --- LOGIKA AGENDA RUTIN (JALAN 2) ---
    # 1. Cari agenda rutin yang jam/tanggalnya sudah terlewat
    agenda_rutin_lewat = Agenda.objects.filter(rutin=True, waktu_mulai__lt=waktu_sekarang)
    
    for agenda in agenda_rutin_lewat:
        # 2. Bikin jadwal baru persis sama, tapi waktunya ditambah 7 hari (minggu depan)
        Agenda.objects.create(
            nama_kegiatan=agenda.nama_kegiatan,
            waktu_mulai=agenda.waktu_mulai + timedelta(days=7),
            tempat=agenda.tempat,
            keterangan=agenda.keterangan,
            rutin=True # Jadwal minggu depan tetap dicentang rutin
        )
        # 3. Jadwal yang lama centang rutinnya dimatikan biar diam manis di tabel 'Selesai'
        agenda.rutin = False
        agenda.save()
    # ------------------------------------
    
    # Memisahkan agenda yang belum terjadi (waktu_mulai >= sekarang)
    agenda_mendatang = Agenda.objects.filter(waktu_mulai__gte=waktu_sekarang).order_by('waktu_mulai')[:5]
    
    # Memisahkan agenda yang sudah lewat (waktu_mulai < sekarang)
    agenda_selesai = Agenda.objects.filter(waktu_mulai__lt=waktu_sekarang).order_by('-waktu_mulai')[:5]
    
    return render(request, 'pcm_web/agenda.html', {
        'agenda_mendatang': agenda_mendatang,
        'agenda_selesai': agenda_selesai
    })


def halaman_kontak(request):
    if request.method == 'POST':
        # Mengambil data dari form HTML
        nama_pengirim = request.POST.get('nama')
        email_pengirim = request.POST.get('email')
        subjek_pesan = request.POST.get('subjek') 
        isi_pesan = request.POST.get('pesan')
        
        # Menyimpan data ke dalam database PesanMasuk
        PesanMasuk.objects.create(
            nama=nama_pengirim, 
            email=email_pengirim, 
            subjek=subjek_pesan, 
            pesan=isi_pesan
        )
        
        # Memunculkan notifikasi sukses
        messages.success(request, 'Terima kasih, pesan Anda berhasil dikirim!')
        return redirect('pcm_web:kontak')

    return render(request, 'pcm_web/kontak.html')

def halaman_amal_usaha(request):
    kategori = request.GET.get('kategori', '')

    # Pemetaan kode kategori URL ke label judul kategori (sesuai BIDANG_CHOICES)
    peta_kategori = {
        'klinik': 'Klinik & Balai Pengobatan',
        'lazismu': 'LazisMu',
        'masjid': 'Masjid / Musholla',
        'panti-asuhan': 'Panti Asuhan',
        'pondok-pesantren': 'Pondok Pesantren',
        'rumah-sakit': 'Rumah Sakit',
        'sekolah': 'Sekolah / Madrasah',
        'toko': 'Toko',
    }

    if kategori in peta_kategori:
        nama_kategori = peta_kategori[kategori]
        daftar_aum = AmalUsaha.objects.filter(bidang=kategori).order_by('nama')
        judul_kategori = f"Amal Usaha Muhammadiyah/'Aisyiyah - {nama_kategori}"
    else:
        nama_kategori = "Amal Usaha Muhammadiyah/'Aisyiyah"
        daftar_aum = AmalUsaha.objects.all().order_by('nama')
        judul_kategori = "Amal Usaha Muhammadiyah/'Aisyiyah"

    context = {
        'daftar_aum': daftar_aum,
        'kategori': kategori,
        'nama_kategori': nama_kategori,
        'judul_kategori': judul_kategori,
    }
    return render(request, 'pcm_web/amal_usaha.html', context)

def halaman_ranting(request):
    # Mengambil semua data ranting diurutkan berdasarkan nama_ranting
    daftar_ranting = Ranting.objects.all().order_by('nama_ranting')
    return render(request, 'pcm_web/ranting.html', {'daftar_ranting': daftar_ranting})


# View untuk menampilkan halaman Beranda (Hero, Sambutan, dan cuplikan Pimpinan)
def beranda(request):
    profil = _profil_pcm_untuk_tampilan()
    daftar_prm = _daftar_prm_untuk_tampilan()
    context = {
        'profil': profil,
        'jumlah_ranting': len(daftar_prm),
        'jumlah_aum': AUM.objects.count() or 70,
        'jumlah_anggota_ktam': profil.jumlah_anggota_ktam,
        'berita_terbaru': BeritaInformasi.objects.order_by('-tanggal_publikasi')[:3],
        'agenda_mendatang': Agenda.objects.filter(
            waktu_mulai__gte=timezone.now()
        ).order_by('waktu_mulai')[:3],
    }
    # Merender halaman beranda.html beserta data dari context
    return render(request, 'pcm_web/beranda.html', context)


def dashboard_panitia(request):
    tugas = PanitiaKegiatan.objects.all()
    total = tugas.count()
    selesai = tugas.filter(tugas_selesai=True).count()
    persentase = round(selesai * 100 / total) if total else 0
    return render(request, 'pcm_web/dashboard_panitia.html', {
        'statistik_panitia': tugas,
        'total_tugas': total,
        'tugas_selesai': selesai,
        'persentase_kesiapan': persentase,
    })

# View untuk menampilkan satu profil PCM
def profil_pcm(request):
    profil = _profil_pcm_untuk_tampilan()
    misi_list = [baris.strip() for baris in profil.misi.splitlines() if baris.strip()] if profil else []
    context = {
        'profil': profil,
        'misi_list': misi_list,
    }
    # Merender halaman profil.html beserta data lengkapnya
    return render(request, 'pcm_web/profil.html', context)


def pimpinan_pcm(request):
    daftar_pimpinan = list(Pimpinan.objects.order_by('urutan_tampil', 'nama'))
    if not daftar_pimpinan:
        daftar_pimpinan = [
            Pimpinan(nama=data['nama'], jabatan=data['jabatan'],
                     periode='Muktamar ke-48', urutan_tampil=urutan)
            for urutan, data in enumerate(PIMPINAN_PCM_DEFAULTS, start=1)
        ]
    for pimpinan in daftar_pimpinan:
        if not pimpinan.foto:
            nama_normal = pimpinan.nama.casefold()
            for nama_kunci, path_foto in PIMPINAN_PHOTO_DEFAULTS:
                if nama_kunci in nama_normal:
                    pimpinan.foto_default_url = static(path_foto)
                    break
    return render(request, 'pcm_web/pimpinan.html', {
        'daftar_pimpinan': daftar_pimpinan,
    })
