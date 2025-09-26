import asyncio
import json
import os
from pathlib import Path
from typing import List

from ..models.schemas import AlignmentRequest, AlignmentResponse, LineTiming, WordTiming
from ..storage.paths import get_storage_paths


def _split_lyrics_into_lines(lyrics: str) -> List[str]:
    return [line.strip() for line in lyrics.splitlines() if line.strip()]


async def _align_with_aeneas(audio_path: str, lyrics: str) -> List[LineTiming]:
    # Lazy import to avoid heavy import at startup
    from aeneas.executetask import ExecuteTask
    from aeneas.task import Task

    paths = get_storage_paths()
    tmp_txt = Path(paths.tmp_dir) / "lyrics.txt"
    tmp_txt.write_text(lyrics, encoding="utf-8")

    task = Task(config_string="task_language=eng|is_text_type=plain|os_task_file_format=json")
    task.audio_file_path_absolute = str(audio_path)
    task.text_file_path_absolute = str(tmp_txt)
    json_out = Path(paths.tmp_dir) / "aeneas_alignment.json"
    task.sync_map_file_path_absolute = str(json_out)

    ExecuteTask(task).execute()

    data = json.loads(json_out.read_text(encoding="utf-8"))
    lines: List[LineTiming] = []
    for fragment in data.get("fragments", []):
        lines.append(
            LineTiming(
                text=fragment.get("lines", [""])[0] if fragment.get("lines") else "",
                start=float(fragment.get("begin", 0.0)),
                end=float(fragment.get("end", 0.0)),
                words=None,
            )
        )
    return lines


async def _align_with_whisper(audio_path: str, lyrics: str) -> List[LineTiming]:
    import whisper  # type: ignore

    model = whisper.load_model("base")
    result = await asyncio.get_event_loop().run_in_executor(None, model.transcribe, audio_path)

    # Very simple DTW-free matching: greedily map lines to segment times by string similarity
    from difflib import SequenceMatcher

    lines = _split_lyrics_into_lines(lyrics)
    timings: List[LineTiming] = []
    segments = result.get("segments", [])
    seg_idx = 0
    for line in lines:
        best_idx = None
        best_score = 0.0
        for i in range(seg_idx, len(segments)):
            seg_text = segments[i].get("text", "")
            score = SequenceMatcher(None, line.lower(), seg_text.lower()).ratio()
            if score > best_score:
                best_score = score
                best_idx = i
        if best_idx is not None:
            seg = segments[best_idx]
            start = float(seg.get("start", 0.0))
            end = float(seg.get("end", start + 2.0))
            timings.append(LineTiming(text=line, start=start, end=end))
            seg_idx = best_idx + 1
        else:
            # Fallback: append with incremental time
            prev_end = timings[-1].end if timings else 0.0
            timings.append(LineTiming(text=line, start=prev_end, end=prev_end + 2.0))
    return timings


def _write_outputs(lines: List[LineTiming]) -> AlignmentResponse:
    paths = get_storage_paths()
    # JSON
    json_path = Path(paths.outputs_dir) / "alignment.json"
    json_path.write_text(
        json.dumps([l.model_dump() for l in lines], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # SRT
    from datetime import timedelta
    import srt  # type: ignore

    def to_td(seconds: float) -> timedelta:
        return timedelta(seconds=seconds)

    subs = [
        srt.Subtitle(index=i + 1, start=to_td(l.start), end=to_td(l.end), content=l.text)
        for i, l in enumerate(lines)
    ]
    srt_path = Path(paths.outputs_dir) / "alignment.srt"
    srt_path.write_text(srt.compose(subs), encoding="utf-8")

    # LRC (line-level)
    def format_lrc_time(t: float) -> str:
        m = int(t // 60)
        s = int(t % 60)
        cs = int((t - int(t)) * 100)
        return f"{m:02d}:{s:02d}.{cs:02d}"

    lrc_lines = [f"[{format_lrc_time(l.start)}]{l.text}" for l in lines]
    lrc_path = Path(paths.outputs_dir) / "alignment.lrc"
    lrc_path.write_text("\n".join(lrc_lines), encoding="utf-8")

    return AlignmentResponse(
        lines=lines,
        srt_path=str(srt_path),
        lrc_path=str(lrc_path),
        json_path=str(json_path),
    )


async def align_lyrics(request: AlignmentRequest) -> AlignmentResponse:
    engine = (request.engine or os.getenv("ALIGNER_ENGINE", "aeneas")).lower()
    if engine == "aeneas":
        lines = await _align_with_aeneas(request.audio_path, request.lyrics)
    else:
        lines = await _align_with_whisper(request.audio_path, request.lyrics)
    return _write_outputs(lines)


