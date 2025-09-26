export type AlignmentLine = {
  text: string;
  start: number;
  end: number;
};

export type AlignmentResponse = {
  lines: AlignmentLine[];
  srt_path?: string;
  lrc_path?: string;
  json_path?: string;
};

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function uploadAudioAndLyrics(audio: File, lyrics?: File, lyricsText?: string) {
  const form = new FormData();
  form.append("audio", audio);
  if (lyrics) form.append("lyrics_file", lyrics);
  if (lyricsText) form.append("lyrics_text", lyricsText);
  const res = await fetch(`${BASE_URL}/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error("Upload failed");
  return res.json() as Promise<{ audio_path: string; lyrics: string }>;
}

export async function alignLyrics(audio_path: string, lyrics: string, engine = "aeneas") {
  const res = await fetch(`${BASE_URL}/align`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ audio_path, lyrics, engine }),
  });
  if (!res.ok) throw new Error("Align failed");
  return res.json() as Promise<AlignmentResponse>;
}

export async function renderVideo(payload: {
  alignment: AlignmentResponse;
  background_color?: string;
  text_color?: string;
  highlight_color?: string;
  width?: number;
  height?: number;
  fps?: number;
  audio_path?: string;
  background_image_path?: string;
}) {
  const res = await fetch(`${BASE_URL}/render`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Render failed");
  return res.json() as Promise<{ output_video: string }>;
}


