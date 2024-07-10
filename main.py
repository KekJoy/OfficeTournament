from fastapi import FastAPI

app = FastAPI(title="Office Tournament")


@app.get("/")
async def root():
    return {"message": "Hello World"}
