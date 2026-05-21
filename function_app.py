import json
import logging

import azure.functions as func

from src.infrastructure.config import Config
from src.infrastructure.container import Container

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

_config = Config.from_env()
_container = Container(_config)


@app.route(route="boilerplate", methods=["GET", "POST"])
def boilerplate_function(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("[boilerplate_function] HTTP trigger received.")
    try:
        body = req.get_json()
        document_url = body.get("document_url")
        document_id = body.get("document_id")

        if not document_url or not document_id:
            return func.HttpResponse(
                json.dumps({"error": "document_url and document_id are required."}),
                status_code=400,
                mimetype="application/json",
            )

        entity = _container.boilerplate_service.process_document(
            document_url=document_url,
            document_id=document_id,
        )

        return func.HttpResponse(
            json.dumps(entity.to_dict()),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logging.error(f"[boilerplate_function] Error: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
        )
