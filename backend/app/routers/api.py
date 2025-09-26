from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional

from ..models.schemas import AlignmentRequest, AlignmentResponse, RenderRequest, RenderResponse
from ..services.alignment import align_lyrics
from ..services.video import render_karaoke_video
from ..utils.files import save_upload, read_text_file
from ..storage.paths import get_storage_paths


router = APIRouter()


@router.post("/upload")
async def upload(
    audio: UploadFile = File(...),
    lyrics_file: Optional[UploadFile] = File(None),
    lyrics_text: Optional[str] = Form(None),
):
    if lyrics_file is None and (lyrics_text is None or lyrics_text.strip() == ""):
        raise HTTPException(status_code=400, detail="Provide lyrics_text or lyrics_file")

    paths = get_storage_paths()
    audio_path = save_upload(audio, paths.uploads_dir)

    lyrics: str
    if lyrics_file is not None:
        lyrics_path = save_upload(lyrics_file, paths.uploads_dir)
        lyrics = read_text_file(lyrics_path)
    else:
        lyrics = lyrics_text or ""

    return {"audio_path": str(audio_path), "lyrics": lyrics}


@router.post("/align", response_model=AlignmentResponse)
async def align(request: AlignmentRequest):
    result = await align_lyrics(request)
    return result


@router.post("/render", response_model=RenderResponse)
async def render(request: RenderRequest):
    output_path = await render_karaoke_video(request)
    return RenderResponse(output_video=str(output_path))


@router.get("/download")
async def download(path: str):
    return FileResponse(path, filename=path.split("/")[-1])


