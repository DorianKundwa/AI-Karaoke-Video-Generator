import asyncio
from pathlib import Path
from typing import Tuple

from moviepy.editor import (
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
)

from ..models.schemas import RenderRequest
from ..storage.paths import get_storage_paths


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))  # type: ignore


async def render_karaoke_video(request: RenderRequest) -> Path:
    paths = get_storage_paths()
    width, height = request.width, request.height

    if request.background_image_path:
        bg = ImageClip(request.background_image_path).resize(newsize=(width, height))
        duration = None
    else:
        bg = ColorClip(size=(width, height), color=_hex_to_rgb(request.background_color))
        duration = None

    # Determine total duration from alignment or audio
    end_time = 0.0
    for l in request.alignment.lines:
        end_time = max(end_time, l.end)

    audio_clip = None
    if request.audio_path:
        audio_clip = AudioFileClip(request.audio_path)
        end_time = max(end_time, audio_clip.duration)

    if duration is None:
        bg = bg.set_duration(end_time)

    clips = [bg]

    # Create line-by-line TextClips with highlight effect by overlaying two TextClips and animating mask
    text_color = request.text_color
    highlight_color = request.highlight_color

    margin_y = 200
    line_height = 60
    font_size = 48
    font = "Arial"

    for idx, line in enumerate(request.alignment.lines):
        y = height - margin_y - (len(request.alignment.lines) - idx) * (line_height + 10)
        base = TextClip(
            txt=line.text,
            fontsize=font_size,
            color=text_color,
            method="caption",
            align="center",
            size=(width - 200, None),
            font=font,
        ).set_position(("center", y)).set_start(line.start).set_end(line.end)

        # Highlight: show same text in highlight_color, but reveal over time via crop that expands
        def make_highlight(t):
            # progress from 0..1 across the line duration
            progress = max(0.0, min(1.0, (t - line.start) / max(0.001, (line.end - line.start))))
            w = int((width - 200) * progress)
            return TextClip(
                txt=line.text,
                fontsize=font_size,
                color=highlight_color,
                method="caption",
                align="center",
                size=(width - 200, None),
                font=font,
            ).crop(x1=0, y1=0, x2=w, y2=base.size[1])

        highlight = base.fl(make_highlight, apply_to=["mask"])  # animate mask

        clips.append(base)
        clips.append(highlight)

    video = CompositeVideoClip(clips, size=(width, height))
    if audio_clip is not None:
        video = video.set_audio(audio_clip)

    out_path = Path(paths.outputs_dir) / "karaoke.mp4"

    def _write():
        video.write_videofile(
            str(out_path),
            fps=request.fps,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            threads=4,
        )

    await asyncio.get_event_loop().run_in_executor(None, _write)
    video.close()
    if audio_clip is not None:
        audio_clip.close()

    return out_path


