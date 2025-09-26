from typing import List, Optional
from pydantic import BaseModel, Field


class WordTiming(BaseModel):
    word: str
    start: float
    end: float


class LineTiming(BaseModel):
    text: str
    start: float
    end: float
    words: Optional[List[WordTiming]] = None


class AlignmentRequest(BaseModel):
    audio_path: str = Field(..., description="Path to uploaded audio file")
    lyrics: str = Field(..., description="Raw lyrics text")
    engine: str = Field(default="aeneas", description="aeneas|whisper")


class AlignmentResponse(BaseModel):
    lines: List[LineTiming]
    srt_path: Optional[str] = None
    lrc_path: Optional[str] = None
    json_path: Optional[str] = None


class RenderRequest(BaseModel):
    alignment: AlignmentResponse
    background_color: str = "#000000"
    text_color: str = "#FFFFFF"
    highlight_color: str = "#FFD700"
    width: int = 1920
    height: int = 1080
    fps: int = 30
    audio_path: Optional[str] = None
    background_image_path: Optional[str] = None


class RenderResponse(BaseModel):
    output_video: str


