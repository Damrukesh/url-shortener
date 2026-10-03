from fastapi import FastAPI

app = FastAPI(title="URL Shortener")

@app.get("/health")
def health():
    return "Ready bro"