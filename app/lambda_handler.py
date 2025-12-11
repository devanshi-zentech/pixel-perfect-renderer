from mangum import Mangum
from app.main import app

# Create Mangum handler with enable_lifespan=True so FastAPI lifespan events run
handler = Mangum(app)
