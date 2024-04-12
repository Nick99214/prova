import os
import uvicorn
from fastapi import FastAPI
from routers import SamplerService
from utility.Utils import get_project_root
from config import config

app = FastAPI()
app.include_router(SamplerService.router)

if __name__ == "__main__":
    cwd = get_project_root()
    settings = config.Settings()

    if not os.path.isdir(os.path.join(cwd, 'logs')):
        os.makedirs(os.path.join(cwd, 'logs'))
    # run uvicorn server
    uvicorn.run(app, host=settings.UVICORN_HOST, port=settings.UVICORN_PORT,
                log_config=os.path.join(cwd, "resources", "log.ini"))
