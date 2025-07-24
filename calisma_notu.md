# GORU ERP - Geliştirme ve Otomasyon Güncellemeleri (Özet ve Açıklama)

## 1. Otomatik Test ve Build (CI)
- **Her kod değişikliğinde (push/pull request) otomatik olarak testler ve kod derlemesi çalışır.**
- Hatalı kod veya başarısız testler varsa, kod ana projeye eklenmez.
- Böylece kodun her zaman çalışır ve güvenli olması sağlanır.
- *Fayda:* Hatalı kodun canlıya çıkması engellenir, ekipte herkesin kodu test edilmiş olur.

## 2. Docker ile Standart Ortamda Test
- **Kod, Docker image olarak paketlenir ve testler bu image içinde çalıştırılır.**
- Herkesin bilgisayarında farklı Python veya kütüphane sürümleri olsa bile, testler her zaman aynı ortamda koşar.
- *Fayda:* "Bende çalışıyor, sende çalışmıyor" sorunları ortadan kalkar.

## 3. README.md'ye Build ve Coverage Badge Eklendi
- **Projenin ana sayfasında otomatik olarak güncellenen build (başarılı/başarısız) ve test coverage (kapsama) rozetleri yer alır.**
- *Fayda:* Projenin güncel durumu herkes tarafından kolayca görülebilir.

## 4. Docker Compose ile Kolay Yerel Geliştirme
- **Tek komutla (docker-compose up --build) hem veritabanı hem backend ayağa kalkar.**
- Testler de aynı ortamda kolayca çalıştırılabilir.
- *Fayda:* Yeni başlayan biri bile tek komutla projeyi çalıştırabilir, karmaşık kurulum gerekmez.

## 5. Geleceğe Hazırlık: Otomatik Deploy Şablonu
- **İleride canlıya (production) veya test (staging) sunucusuna otomatik kod gönderme (deploy) için hazır şablon eklendi.**
- Şu an aktif değil, ama ileride kolayca devreye alınabilir.
- *Fayda:* Proje büyüdüğünde veya ekibe yeni biri katıldığında, canlıya kod gönderme süreci de otomatikleşir.

---

## Kısaca: Bu Güncellemeler Ne İşe Yarar?
- Kodun her zaman test edilmiş, güvenli ve çalışır olmasını sağlar.
- Ekipte herkesin aynı ortamda çalışmasını ve test etmesini kolaylaştırır.
- Projeyi yeni klonlayan biri bile, tek komutla (docker-compose up --build) projeyi çalıştırabilir.
- Projenin güncel durumu (build ve test durumu) anında görülebilir.
- Gelecekte otomatik canlıya alma (deploy) için altyapı hazırdır.
