import os
import uvicorn
from core.DebugLog import log_error

def main() -> None:
    try:
        app = os.environ['UVICORN_APP']
        host = os.environ['UVICORN_HOST']
        port = int(os.environ['UVICORN_PORT'])
        reload_ = True
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload_,
            log_level=os.environ['UVICORN_LOG_LEVEL'],
        )
    except Exception as ex:
        log_error(f"Error: {ex}")
        print(f"Error: {ex}")

if __name__ == "__main__":
    main()