"""Write the FastAPI OpenAPI spec to web/openapi.json (then: cd web && npm run types:api)."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from api.main import app
(ROOT / "web" / "openapi.json").write_text(json.dumps(app.openapi(), indent=2))
print("wrote web/openapi.json")
