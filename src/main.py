from fastapi import FastAPI
from .database.core import Base, engine
from .api import register_routes
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from fastapi.responses import JSONResponse
from fastapi import Request


app = FastAPI(
    title="Farm"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=['*'],
    allow_methods=['*']
)



Base.metadata.create_all(bind=engine)

#Catch Database(Render) OperationalError Before it hits my code
@app.exception_handler(OperationalError)
async def db_operational_error_handler(request: Request, exc: OperationalError):
    return JSONResponse(
        status_code=503,
        content={"detail": "Database connection failed. Please try again later."},
    )


register_routes(app=app)