import requests
from .models import ProfilOrganisasi, TautanTerkait

def profil_dan_tautan(request):
    profil = ProfilOrganisasi.objects.first()
    tautan_terkait = TautanTerkait.objects.all().order_by('urutan')
    return {
        'profil_organisasi': profil,
        'profil': profil,
        'tautan_terkait': tautan_terkait,
    }

def jadwal_shalat(request):
    url = "https://api.aladhan.com/v1/timingsByCity?city=Surakarta&country=Indonesia&method=99&methodSettings=18,null,18"
    
    jadwal = None
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                timings = data['data']['timings']
                jadwal = {
                    'tanggal': data['data']['date']['readable'],
                    'imsak': timings['Imsak'],
                    'subuh': timings['Fajr'],
                    'terbit': timings['Sunrise'],
                    'dzuhur': timings['Dhuhr'],
                    'ashar': timings['Asr'],
                    'maghrib': timings['Maghrib'],
                    'isya': timings['Isha']
                }
    except requests.RequestException:
        pass
        
    return {'jadwal_shalat': jadwal}
