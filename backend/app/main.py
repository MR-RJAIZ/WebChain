from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api.router import api_router


app = FastAPI(
    title="WebChain API",
    version="0.1.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# API ROUTES
# =========================================================

app.include_router(api_router)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "message": "WebChain backend is running"
    }


# =========================================================
# CUSTOM OPENAPI
# =========================================================

def custom_openapi():

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description="WebChain decentralized website hosting API",
        routes=app.routes,
    )

    # Find the publish request schema dynamically.
    schemas = openapi_schema.get(
        "components",
        {}
    ).get(
        "schemas",
        {}
    )

    for schema in schemas.values():

        properties = schema.get(
            "properties",
            {}
        )

        if "files" in properties:

            files_schema = properties["files"]

            if files_schema.get("type") == "array":

                files_schema["items"] = {
                    "type": "string",
                    "format": "binary",
                }

    app.openapi_schema = openapi_schema

    return app.openapi_schema


app.openapi = custom_openapi