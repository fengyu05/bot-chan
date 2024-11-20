

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fluctlight.agent_catalog.catalog_manager import CatalogManager
from fluctlight.web_server.restful_routes import router as restful_router
from fluctlight.utt.web_socket import ConnectionManager



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # Change to domains if you deploy this to production
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(restful_router)
#app.include_router(websocket_router)
#app.include_router(twilio_router)

# initializations
CatalogManager.initialize()
ConnectionManager.initialize()


