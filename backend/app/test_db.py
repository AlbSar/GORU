import os

from .database import test_connection  # ✅ Alternatif


def print_db_debug_info():
    print("--- Veritabanı Bağlantı Debug Bilgileri ---")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
    print("Aşağıdaki yaygın nedenleri kontrol edin:")
    print("- .env dosyasında DATABASE_URL doğru mu?")
    print("- PostgreSQL servisi çalışıyor mu?")
    print("- Kullanıcı adı, şifre ve veritabanı adı doğru mu?")
    print("- Docker veya Docker Compose ile başlatıldıysa, db servisi hazır mı?")
    print("- Port (5432) açık mı ve çakışma yok mu?")
    print("- Bağlantı sırasında ağ veya firewall engeli var mı?")
    print("--------------------------------------------")


if __name__ == "__main__":
    if test_connection():
        print("Veritabanı bağlantısı başarılı!")
    else:
        print("Veritabanı bağlantısı başarısız!")
        print_db_debug_info()
