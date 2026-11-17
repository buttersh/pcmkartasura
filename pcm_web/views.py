from datetime import timedelta

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.utils import timezone

from .forms import KontakForm
from .models import (
    AUM,
    PRM,
    Agenda,
    AmalUsaha,
    Berita,
    BeritaInformasi,
    Dokumen,
    PanitiaKegiatan,
    PesanMasuk,
    Pimpinan,
    ProfilCabang,
    ProfilOrganisasi,
    Ranting,
    StrukturPengurus,
    TautanTerkait,
)

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
    'telepon': '08121547207',
    'email': 'pcmkartasura@gmail.com',
    'jumlah_anggota_ktam': 364,
}

PIMPINAN_PCM_DEFAULTS = [
    {'nama': 'Ihwan Susila, S.E., M.Si., Ph.D.', 'jabatan': 'Ketua', 'urutan': 1},
    {'nama': 'Drs. Abdul Fatah Bintoro, M.Pd.', 'jabatan': 'Sekretaris', 'urutan': 2},
    {'nama': 'Prof. Dr. Kuswaji Dwi Priyono, M.Si.', 'jabatan': 'Bendahara', 'urutan': 3},
    {'nama': 'Dr. Abdullah Mahmud, M.Ag.', 'jabatan': 'Wakil Ketua — Tarjih, Tabligh dan Pembinaan Masjid', 'urutan': 4},
    {'nama': 'H. Asrori, S.Pd.I.', 'jabatan': 'Wakil Ketua — Pendidikan', 'urutan': 5},
    {'nama': 'Rahmad Basuki', 'jabatan': 'Wakil Ketua — Pembinaan Kader dan Sumber Daya Insani', 'urutan': 6},
    {'nama': 'Prof. Dr. H. Bambang Sumardjoko, M.Pd.', 'jabatan': 'Wakil Ketua — PKU dan Kesejahteraan Sosial', 'urutan': 7},
    {'nama': 'Dr. H. Abdul Aziz Nugroho Pratama, M.M.', 'jabatan': 'Wakil Ketua — Ekonomi dan Pemberdayaan Masyarakat', 'urutan': 8},
    {'nama': 'Drs. Muhammad Widodo, M.Pd.', 'jabatan': 'Wakil Ketua — Hukum, Lingkungan Hidup, Pustaka dan Informasi', 'urutan': 9},
]

PIMPINAN_PHOTO_DEFAULTS = [
    ('ihwan susila', 'pcm_web/images/ihwan-susila.jpg'),
    ('abdul fatah bintoro', 'pcm_web/images/abdul-fatah-bintoro.jpg'),
    ('kuswaji dwi priyono', 'pcm_web/images/kuswaji-dwi-priyono.jpg'),
    ('abdullah mahmud', 'pcm_web/images/abdullah-mahmud.jpg'),
    ('bambang sumardjoko', 'pcm_web/images/bambang-sumardjoko.jpg'),
]

RANTING_PCM_DEFAULTS = [
    {'nama_ranting': 'Kartasura', 'ketua': 'Achmad Fatoni, M.Pd', 'alamat': 'Kelurahan Kartasura, Kec. Kartasura'},
    {'nama_ranting': 'Ngemplak', 'ketua': 'Suramto, S.Pd.', 'alamat': 'Desa Ngemplak, Kec. Kartasura'},
    {'nama_ranting': 'Pucangan', 'ketua': 'Drs. H. Maryanto, MM', 'alamat': 'Kelurahan Pucangan, Kec. Kartasura'},
    {'nama_ranting': 'Kertonatan', 'ketua': "Drs. Ali Sa'bani, M.Pd.I", 'alamat': 'Desa Kertonatan, Kec. Kartasura'},
    {'nama_ranting': 'Wirogunan', 'ketua': 'Dr. H. Dzanurusyamsi, M.H.', 'alamat': 'Desa Wirogunan, Kec. Kartasura'},
    {'nama_ranting': 'Ngabeyan', 'ketua': 'Muhammad Rochjani, S.Pd', 'alamat': 'Kelurahan Ngabeyan, Kec. Kartasura'},
    {'nama_ranting': 'Singopuran', 'ketua': 'H. Nur Hasan, M.T.', 'alamat': 'Desa Singopuran, Kec. Kartasura'},
    {'nama_ranting': 'Pabelan', 'ketua': 'apt. Gunawan Setiyadi, M.Sc.', 'alamat': 'Desa Pabelan, Kec. Kartasura'},
    {'nama_ranting': 'Gonilan', 'ketua': 'Drs. Supriyadi', 'alamat': 'Desa Gonilan, Kec. Kartasura'},
    {'nama_ranting': 'Makamhaji', 'ketua': 'Drs. Edy Siyamto, M.Si.', 'alamat': 'Kelurahan Makamhaji, Kec. Kartasura'},
    {'nama_ranting': 'Gumpang', 'ketua': 'Muhammad Anis Sumaji, S.Ag., M.PI', 'alamat': 'Desa Gumpang, Kec. Kartasura'},
    {'nama_ranting': 'Ngadirejo', 'ketua': 'Agus Mustamar, SH.I.', 'alamat': 'Desa Ngadirejo, Kec. Kartasura'},
]


def _profil_pcm_untuk_tampilan():
    profil = ProfilOrganisasi.objects.first()
    if profil is None:
        profil = ProfilOrganisasi(**PROFIL_PCM_DEFAULTS)
    return profil


def beranda(request):
    profil = _profil_pcm_untuk_tampilan()
    jumlah_ranting = Ranting.objects.count()
    if not jumlah_ranting:
        jumlah_ranting = len(RANTING_PCM_DEFAULTS)

    jumlah_aum = AmalUsaha.objects.count()
    if not jumlah_aum:
        jumlah_aum = AUM.objects.count() or 70

    berita_terbaru = Berita.objects.terbit()[:3]
    if not berita_terbaru.exists():
        berita_terbaru = BeritaInformasi.objects.order_by('-tanggal_publikasi')[:3]

    agenda_mendatang = Agenda.objects.filter(
        waktu_mulai__gte=timezone.now()
    ).order_by('waktu_mulai')[:3]

    gambar_hero = ""
    if getattr(profil, 'gambar_utama', None):
        try:
            gambar_hero = profil.gambar_utama.url
        except Exception:
            gambar_hero = static('pcm_web/images/pimpinan-pcm-hero.jpeg')
    else:
        gambar_hero = static('pcm_web/images/pimpinan-pcm-hero.jpeg')

    context = {
        'profil': profil,
        'gambar_hero': gambar_hero,
        'jumlah_ranting': jumlah_ranting,
        'jumlah_aum': jumlah_aum,
        'jumlah_anggota_ktam': getattr(profil, 'jumlah_anggota_ktam', 364),
        'berita_terbaru': berita_terbaru,
        'agenda_mendatang': agenda_mendatang,
    }
    return render(request, 'pcm_web/beranda.html', context)


def profil_pcm(request):
    profil = _profil_pcm_untuk_tampilan()
    misi_list = [baris.strip() for baris in profil.misi.splitlines() if baris.strip()] if profil and profil.misi else []
    context = {
        'profil': profil,
        'misi_list': misi_list,
    }
    return render(request, 'pcm_web/profil.html', context)


def pimpinan_pcm(request):
    daftar_pimpinan = list(Pimpinan.objects.order_by('urutan_tampil', 'nama'))
    if not daftar_pimpinan:
        daftar_pimpinan = [
            Pimpinan(
                nama=data['nama'],
                jabatan=data['jabatan'],
                periode='2022–2027',
                urutan_tampil=data['urutan'],
            )
            for data in PIMPINAN_PCM_DEFAULTS
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


def halaman_ranting(request):
    daftar_ranting = list(Ranting.objects.all().order_by('nama_ranting'))
    if not daftar_ranting:
        daftar_ranting = [
            Ranting(
                nama_ranting=d['nama_ranting'],
                ketua=d['ketua'],
                alamat=d['alamat'],
            )
            for d in RANTING_PCM_DEFAULTS
        ]
    return render(request, 'pcm_web/ranting.html', {'daftar_ranting': daftar_ranting})


def halaman_amal_usaha(request):
    kategori = request.GET.get('kategori', '').strip()

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
        daftar_aum = AmalUsaha.objects.all().order_by('bidang', 'nama')
        judul_kategori = "Amal Usaha Muhammadiyah/'Aisyiyah"

    context = {
        'daftar_aum': daftar_aum,
        'kategori': kategori,
        'nama_kategori': nama_kategori,
        'judul_kategori': judul_kategori,
    }
    return render(request, 'pcm_web/amal_usaha.html', context)


def daftar_berita(request):
    paginator = Paginator(Berita.objects.terbit(), 6)
    berita_page = paginator.get_page(request.GET.get('page'))
    return render(request, 'pcm_web/berita_list.html', {'berita_page': berita_page})


def detail_berita(request, slug):
    berita = get_object_or_404(Berita.objects.terbit(), slug=slug)
    berita_lainnya = Berita.objects.terbit().exclude(pk=berita.pk)[:3]
    isi_artikel = berita.isi
    sumber_url = ""
    source_marker = "Sumber asli: "
    if source_marker in isi_artikel:
        isi_artikel, sumber_url = isi_artikel.rsplit(source_marker, 1)
        isi_artikel = isi_artikel.rstrip()
        sumber_url = sumber_url.strip()

    return render(
        request,
        'pcm_web/berita_detail.html',
        {
            'berita': berita,
            'berita_lainnya': berita_lainnya,
            'isi_artikel': isi_artikel,
            'sumber_url': sumber_url,
        },
    )


def daftar_unduhan(request):
    dokumen_list = list(Dokumen.objects.order_by('judul'))
    dokumen_cabang = [
        dokumen for dokumen in dokumen_list
        if dokumen.judul.startswith('SK PDM Sukoharjo')
    ]
    dokumen_ranting = [
        dokumen for dokumen in dokumen_list
        if dokumen.judul.startswith('SK PCM Kartasura Susunan PRM')
    ]
    dokumen_lainnya = [
        dokumen for dokumen in dokumen_list
        if dokumen not in dokumen_cabang and dokumen not in dokumen_ranting
    ]
    document_sections = [
        {
            'title': 'SK Tingkat Cabang — PDM Sukoharjo',
            'badge': 'Cabang · 2022–2027',
            'documents': dokumen_cabang,
        },
        {
            'title': 'SK Pimpinan Ranting Muhammadiyah (PRM)',
            'badge': 'PRM · 2022–2027',
            'documents': dokumen_ranting,
        },
        {
            'title': 'Dokumen Resmi Lainnya',
            'badge': 'Dokumen resmi',
            'documents': dokumen_lainnya,
        },
    ]
    return render(
        request,
        'pcm_web/unduhan.html',
        {
            'dokumen_list': dokumen_list,
            'document_sections': document_sections,
        },
    )


def halaman_agenda(request):
    waktu_sekarang = timezone.now()

    # Logika Agenda Rutin Mingguan
    agenda_rutin_lewat = Agenda.objects.filter(rutin=True, waktu_mulai__lt=waktu_sekarang)
    for agenda in agenda_rutin_lewat:
        Agenda.objects.create(
            nama_kegiatan=agenda.nama_kegiatan,
            waktu_mulai=agenda.waktu_mulai + timedelta(days=7),
            tempat=agenda.tempat,
            keterangan=agenda.keterangan,
            rutin=True,
        )
        agenda.rutin = False
        agenda.save(update_fields=['rutin'])

    # Agenda Mendatang dan Agenda Selesai dipisah
    agenda_mendatang = Agenda.objects.filter(waktu_mulai__gte=waktu_sekarang).order_by('waktu_mulai')
    agenda_selesai = Agenda.objects.filter(waktu_mulai__lt=waktu_sekarang).order_by('-waktu_mulai')

    return render(request, 'pcm_web/agenda.html', {
        'agenda_mendatang': agenda_mendatang,
        'agenda_selesai': agenda_selesai,
    })


def halaman_kontak(request):
    if request.method == 'POST':
        form = KontakForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Terima kasih, pesan Anda berhasil dikirim!')
            return redirect('pcm_web:kontak')
        else:
            messages.error(request, 'Mohon periksa kembali isian formulir Anda.')
    else:
        form = KontakForm()

    return render(request, 'pcm_web/kontak.html', {'form': form})


def cari_berita(request):
    query = request.GET.get('q', '').strip()
    hasil = None

    if query:
        hasil = Berita.objects.terbit().filter(
            Q(judul__icontains=query) | Q(isi__icontains=query) | Q(ringkasan__icontains=query)
        )

    return render(request, 'pcm_web/cari.html', {'query': query, 'hasil': hasil})


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
