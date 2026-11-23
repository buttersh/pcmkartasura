from django import forms
from .models import PesanMasuk

class KontakForm(forms.ModelForm):
    class Meta:
        model = PesanMasuk
        fields = ['nama', 'email', 'subjek', 'pesan']
        widgets = {
            'nama': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama lengkap Anda',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'nama@contoh.com',
                'required': True,
            }),
            'subjek': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subjek atau perihal pesan',
                'required': True,
            }),
            'pesan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Tulis pesan Anda di sini...',
                'required': True,
            }),
        }
        labels = {
            'nama': 'Nama Lengkap',
            'email': 'Alamat Email',
            'subjek': 'Subjek',
            'pesan': 'Isi Pesan',
        }
