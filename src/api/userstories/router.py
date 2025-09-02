from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from core.userstories.compiler import UserStoryCompiler

router = APIRouter(tags=["UserStory Compiler"])


class UserStoryInput(BaseModel):
    data: List[Dict]  # JSON user stories


@router.post("/generate/txt", response_class=Response)
def compile_to_txt(input_data: UserStoryInput):
    try:
        compiler = UserStoryCompiler(input_data.data)
        txt_bytes = compiler.to_txt()

        return Response(
            content=txt_bytes,
            media_type="text/plain",
            headers={"Content-Disposition": "attachment; filename=userstories.txt"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/docx", response_class=Response)
def compile_to_docx(input_data: UserStoryInput):
    try:
        compiler = UserStoryCompiler(input_data.data)
        docx_bytes = compiler.to_docx()

        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=userstories.docx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/string", response_class=Response)
def compile_to_string(input_data: UserStoryInput):
    try:
        compiler = UserStoryCompiler(input_data.data)
        string_output = compiler.to_string()

        return Response(
            content=string_output,
            media_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
