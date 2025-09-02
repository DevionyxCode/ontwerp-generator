from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Dict
from core.scrumboard.compiler import ScrumboardExcelExporter

router = APIRouter(tags=["Scrumboard"])


class ScrumboardInput(BaseModel):
    data: Dict[str, List[Dict]]  # JSON structuur van het scrumboard


@router.post("/generate/excel", response_class=Response)
def generate_scrumboard_excel(input_data: ScrumboardInput):
    """
    Endpoint die een JSON Scrumboard omzet naar Excel en het bestand terugstuurt.
    """
    try:
        exporter = ScrumboardExcelExporter(input_data.data)
        excel_bytes = exporter.run()
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=scrumboard.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
