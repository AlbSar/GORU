from fastapi import FastAPI
from .routes import router

app = FastAPI(title="GORU ERP Backend")

app.include_router(router)


@app.get("/")
def read_root():
    return {"message": "GORU ERP Backend API çalışıyor!"}
