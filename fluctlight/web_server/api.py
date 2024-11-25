from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fluctlight.agent_catalog.catalog_manager import CatalogManager
from fluctlight.utt.web_socket import ConnectionManager
from fluctlight.web_server.restful_routes import router as restful_router


def create_app():
    app = FastAPI()

    # Add CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Change to specific domains in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(restful_router)
    # app.include_router(websocket_router)
    # app.include_router(twilio_router)

    # Initializations
    CatalogManager.initialize()
    ConnectionManager.initialize()

    return app


def main():
    app = create_app()
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
