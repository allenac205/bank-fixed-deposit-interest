from fastapi import FastAPI
from routes import router


app = FastAPI(docs_url="/")


app.include_router(router)