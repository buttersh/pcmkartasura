import requests
from django.core.cache import cache
from django.utils import timezone
from .models import ProfilOrganisasi, TautanTerkait

BULAN_HIJRIAH = {
    1: "Muharram",
    2: "Safar",
    3: "Rabiul Awal",
    4: "Rabiul Akhir",
    5: "Jumadil Awal",
    6: "Jumadil Akhir",
    7: "Rajab",
    8: "Syakban",
    9: "Ramadan",
    10: "Syawal",
    11: "Zulkaidah",
    12: "Zulhijah",
}


def profil_dan_tautan(request):
    profil = ProfilOrganisasi.objects.first()
    tautan_terkait = TautanTerkait.objects.all().order_by('urutan')
    return {
        'profil_organisasi': profil,
        'profil': profil,
        'tautan_terkait': tautan_terkait,
    }


def jadwal_shalat(request):
    cache_key = f"jadwal_shalat_surakarta:{timezone.localdate().isoformat()}"
    cached = cache.get(cache_key)
    if cached is not None:
        return {'jadwal_shalat': cached or None}

    url = "https://api.aladhan.com/v1/timingsByCity?city=Surakarta&country=Indonesia&method=99&methodSettings=18,null,18"

    jadwal = None
    try:
        response = requests.get(url, timeout=4)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                timings = data['data']['timings']
                hijri = data['data']['date'].get('hijri') or {}
                bulan_num = hijri.get('month', {}).get('number')
                bulan_nama = BULAN_HIJRIAH.get(bulan_num, hijri.get('month', {}).get('en', ''))
                hijri_day = hijri.get('day', '')
                hijri_year = hijri.get('year', '')
                hijri_formatted = f"{int(hijri_day)} {bulan_nama} {hijri_year} H" if hijri_day and bulan_nama and hijri_year else ""
                jadwal = {
                    'tanggal': data['data']['date']['readable'],
                    'hijri_tanggal': hijri_formatted,
                    'hijri_bulan_ke': bulan_num or 0,
                    'hijri_tahun': hijri_year,
                    'imsak': timings['Imsak'][:5],
                    'subuh': timings['Fajr'][:5],
                    'terbit': timings['Sunrise'][:5],
                    'dzuhur': timings['Dhuhr'][:5],
                    'ashar': timings['Asr'][:5],
                    'maghrib': timings['Maghrib'][:5],
                    'isya': timings['Isha'][:5],
                }
    except (requests.RequestException, ValueError, KeyError):
        pass

    cache.set(cache_key, jadwal or {}, 60 * 60 * 6 if jadwal else 60 * 5)
    return {'jadwal_shalat': jadwal}
