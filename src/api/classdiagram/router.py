from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from core.classdiagram.compiler import DrawioClassDiagramGenerator
from typing import List, Dict

router = APIRouter(tags=["CLASSDIAGRAM"])


class ERDInput(BaseModel):
    data: List[Dict]  # JSON structuur van de database/entities


@router.post("/generate", response_class=Response)
def generate_erd(input_data: ERDInput):
    try:
        erd_generator = DrawioClassDiagramGenerator()
        # De generator verwacht waarschijnlijk een JSON string
        xml_output = erd_generator.run(json_data=input_data.data)

        return Response(
            content=xml_output,
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=erd.drawio"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

