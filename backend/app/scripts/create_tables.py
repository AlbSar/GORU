from ..database import engine, Base

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tüm tablolar güncel modellerle oluşturuldu.")
