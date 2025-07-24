from database import test_connection

if test_connection():
    print("Veritabanı bağlantısı başarılı!")
else:
    print("Veritabanı bağlantısı başarısız!")
