# GORU ERP - Geliştirme ve Otomasyon Notları (Deneyim ve Süreç)

Bu notlar, GORU ERP projesinde gerçek bir geliştirme ve ekip çalışması sürecinde yaşadıklarımızı, aldığımız kararları ve öğrendiklerimizi özetliyor. Her madde, doğrudan karşılaştığımız bir ihtiyaç, hata veya iyileştirme fırsatından doğdu. Amacımız, hem kendimize hem de projeyi devralacak herkese, sürecin arka planını ve neden-sonuç ilişkilerini açıkça göstermek.

---

## 1. Otomatik Test ve Build (CI)
- **Her kod değişikliğinde (push/pull request) otomatik olarak testler ve kod derlemesi çalışır.**
- Hatalı kod veya başarısız testler varsa, kod ana projeye eklenmez.
- Bu alışkanlık, ilk başta biraz yavaşlatıcı gibi görünse de, uzun vadede kod kalitesini ve ekip içi güveni ciddi şekilde artırdı.
- *Fayda:* Hatalı kodun canlıya çıkması engellenir, ekipte herkesin kodu test edilmiş olur.

## 2. Docker ile Standart Ortamda Test
- **Kod, Docker image olarak paketlenir ve testler bu image içinde çalıştırılır.**
- Farklı bilgisayarlarda, farklı Python veya kütüphane sürümleriyle yaşanan "bende çalışıyor, sende çalışmıyor" sorunlarıyla çok uğraştık. Docker ile bu sorunları kökten çözdük.
- *Fayda:* Herkesin test sonucu aynı, ortam farkı yok.

## 3. README.md'ye Build ve Coverage Badge Eklendi
- **Projenin ana sayfasında otomatik olarak güncellenen build (başarılı/başarısız) ve test coverage (kapsama) rozetleri yer alır.**
- Bu rozetler, projenin güncel durumu hakkında anında bilgi veriyor ve dışarıdan bakan biri için de güven verici.
- *Fayda:* Projenin güncel durumu herkes tarafından kolayca görülebilir.

## 4. Docker Compose ile Kolay Yerel Geliştirme
- **Tek komutla (docker-compose up --build) hem veritabanı hem backend ayağa kalkar.**
- Özellikle yeni başlayanlar veya projeyi ilk kez klonlayanlar için büyük kolaylık sağladı. Karmaşık kurulum adımlarını ortadan kaldırdık.
- *Fayda:* Yeni başlayan biri bile tek komutla projeyi çalıştırabilir, karmaşık kurulum gerekmez.

## 5. Geleceğe Hazırlık: Otomatik Deploy Şablonu
- **İleride canlıya (production) veya test (staging) sunucusuna otomatik kod gönderme (deploy) için hazır şablon eklendi.**
- Şu an aktif değil, ama ileride kolayca devreye alınabilir. Bu şablonu eklerken, gelecekteki büyümeyi ve ekip değişikliklerini de göz önünde bulundurduk.
- *Fayda:* Proje büyüdüğünde veya ekibe yeni biri katıldığında, canlıya kod gönderme süreci de otomatikleşir.

---

## Kısaca: Bu Güncellemeler Neden Önemli?
- Kodun her zaman test edilmiş, güvenli ve çalışır olmasını sağlar.
- Ekipte herkesin aynı ortamda çalışmasını ve test etmesini kolaylaştırır.
- Projeyi yeni klonlayan biri bile, tek komutla (docker-compose up --build) projeyi çalıştırabilir.
- Projenin güncel durumu (build ve test durumu) anında görülebilir.
- Gelecekte otomatik canlıya alma (deploy) için altyapı hazırdır.

---

Bu notlar, sadece teknik bir özet değil; aynı zamanda bir ekip olarak yaşadığımız gerçek deneyimlerin ve öğrenme sürecimizin bir yansımasıdır. Herhangi bir adımda takılırsanız veya daha fazla detay isterseniz, sürecin arka planını paylaşmaktan mutluluk duyarız!
