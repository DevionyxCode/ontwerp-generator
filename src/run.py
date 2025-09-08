# run.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",      # pad naar je FastAPI app (module:app)
        host="127.0.0.1",    # localhost
        port=8090,           # poort waarop de site draait
        reload=True         # auto-reload bij codewijzigingen (debug mode)
    )
