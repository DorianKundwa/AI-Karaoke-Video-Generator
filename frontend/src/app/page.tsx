"use client";
import { useMemo, useState } from "react";
import { uploadAudioAndLyrics, alignLyrics, renderVideo, type AlignmentResponse } from "@/lib/api";
import PreviewCanvas from "@/components/PreviewCanvas";

export default function Page() {
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [lyricsFile, setLyricsFile] = useState<File | null>(null);
  const [lyricsText, setLyricsText] = useState<string>("");
  const [uploadResult, setUploadResult] = useState<{ audio_path: string; lyrics: string } | null>(null);
  const [alignment, setAlignment] = useState<AlignmentResponse | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  const audioUrl = useMemo(() => (audioFile ? URL.createObjectURL(audioFile) : ""), [audioFile]);

  async function handleUpload() {
    if (!audioFile) return;
    const res = await uploadAudioAndLyrics(audioFile, lyricsFile ?? undefined, lyricsText || undefined);
    setUploadResult(res);
    setLyricsText(res.lyrics);
  }

  async function handleAlign() {
    if (!uploadResult) return;
    const res = await alignLyrics(uploadResult.audio_path, lyricsText || uploadResult.lyrics, "aeneas");
    setAlignment(res);
  }

  async function handleRender() {
    if (!alignment || !uploadResult) return;
    const res = await renderVideo({ alignment, audio_path: uploadResult.audio_path });
    const url = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"}/download?path=${encodeURIComponent(res.output_video)}`;
    setVideoUrl(url);
  }

  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: 24 }}>
      <h1>AI Karaoke</h1>

      <section style={{ display: "grid", gap: 12, marginBottom: 24 }}>
        <label>
          Audio (mp3/wav)
          <input type="file" accept="audio/*" onChange={(e) => setAudioFile(e.target.files?.[0] ?? null)} />
        </label>
        <label>
          Lyrics (.txt optional)
          <input type="file" accept=".txt" onChange={(e) => setLyricsFile(e.target.files?.[0] ?? null)} />
        </label>
        <textarea
          placeholder="Paste lyrics here"
          value={lyricsText}
          onChange={(e) => setLyricsText(e.target.value)}
          rows={8}
          style={{ width: "100%" }}
        />
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={handleUpload} disabled={!audioFile}>1) Upload</button>
          <button onClick={handleAlign} disabled={!uploadResult}>2) Align</button>
          <button onClick={handleRender} disabled={!alignment}>3) Render</button>
          {videoUrl && (
            <a href={videoUrl} target="_blank" rel="noreferrer">Download MP4</a>
          )}
        </div>
      </section>

      {audioFile && alignment && (
        <PreviewCanvas audioUrl={audioUrl} alignment={alignment.lines} />
      )}
    </main>
  );
}


