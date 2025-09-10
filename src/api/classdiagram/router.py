from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from core.classdiagram.compiler import DrawioClassDiagramGenerator
from typing import List, Dict

router = APIRouter(tags=["CLASSDIAGRAM"])


class classInput(BaseModel):
    data: Dict  # Verwacht nu een dict met 'classes' en 'relations'


@router.post("/generate", response_class=Response)
def generate_class(input_data: classInput):
    try:
        class_generator = DrawioClassDiagramGenerator()
        # De generator verwacht waarschijnlijk een JSON string
        xml_output = class_generator.run(json_data=input_data.data)

        return Response(
            content=xml_output,
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=class.drawio"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

