# Gerçek Zamanlı Sözdizimi Renklendirici 🖍️

Bu proje, **Python** ile sıfırdan geliştirilen, dilbilgisi-tabanlı gerçek zamanlı bir syntax-highlighting aracıdır.  
Arka planda kendi **Lexer → Parser → GUI** zincirimiz çalışır; hazır kütüphane kullanılmaz. Renklendirme şeması modern *dark mode* estetiğiyle merkezi bir “ModernTheme” sınıfı üzerinden yönetilir.

## 🔑 Ana Özellikler
- **Özel statik-tipli örnek dil**: C ailesinin temel sözdizimini ve kontrol yapıları-fonksiyonlarını içerir.
- **Lexer** – durum diyagramı yaklaşımıyla karakter karakter tarar, token listesi döndürür.
- **Recursive-descent Parser** – operatör önceliği ve hata senkronizasyonu dâhil ayrıntılı AST üretir.
- **Tkinter GUI** – satır numaraları, anlık hata iletisi, <KeyRelease> tetiklemeli otomatik renklendirme.

## 📺 Youtube Videosu
[![YouTube](https://youtu.be/YykB6CrarkI)

## 📄 Raporlar
| Belge | Biçim | Link |
|-------|-------|------|
| Programlama Dilleri **Ana Raporu** | PDF | [`docs/Programlama_Dilleri_Ana_Rapor.pdf`](docs/Programlama_Dilleri_Ana_Rapor.pdf) |
| Programlama Dilleri **Makale** | PDF | [`docs/Programlama_Dilleri_Makale.pdf`](docs/Programlama_Dilleri_Makale.pdf) |

> Detaylı teknik mimari ve metodoloji bu iki raporda sunulmuştur.

