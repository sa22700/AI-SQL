import os
import uvicorn

def main() -> None:
    app = os.environ['UVICORN_APP']
    host = os.environ['UVICORN_HOST']
    port = int(os.environ['UVICORN_PORT'])
    reload_ = os.environ['UVICORN_RELOAD']

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload_,
        log_level=os.environ['UVICORN_LOG_LEVEL'],
    )

if __name__ == "__main__":
    main()