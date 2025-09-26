"use client";
import { useEffect, useRef } from "react";
import type { AlignmentLine } from "@/lib/api";

type Props = {
  audioUrl: string;
  alignment: AlignmentLine[];
  width?: number;
  height?: number;
};

export default function PreviewCanvas({ audioUrl, alignment, width = 960, height = 540 }: Props) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    const audio = new Audio(audioUrl);
    audioRef.current = audio;

    let raf = 0;
    function draw() {
      const t = audio.currentTime;
      ctx.fillStyle = "#000";
      ctx.fillRect(0, 0, width, height);

      const current = alignment.find((l) => t >= l.start && t <= l.end);
      const upcoming = alignment.find((l) => l.start > (current?.end ?? t));

      ctx.textAlign = "center";
      ctx.font = "bold 28px Arial";

      if (current) {
        const progress = Math.max(0, Math.min(1, (t - current.start) / Math.max(0.001, current.end - current.start))));
        // base text
        ctx.fillStyle = "#ffffff";
        ctx.fillText(current.text, width / 2, height / 2);
        // highlight overlay via clip
        const measure = ctx.measureText(current.text);
        const textWidth = measure.width;
        const startX = width / 2 - textWidth / 2;
        ctx.save();
        ctx.beginPath();
        ctx.rect(startX, height / 2 - 30, textWidth * progress, 50);
        ctx.clip();
        ctx.fillStyle = "#ffd700";
        ctx.fillText(current.text, width / 2, height / 2);
        ctx.restore();
      }

      if (upcoming) {
        ctx.fillStyle = "#888";
        ctx.fillText(upcoming.text, width / 2, height / 2 + 60);
      }

      raf = requestAnimationFrame(draw);
    }
    raf = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(raf);
  }, [audioUrl, alignment, width, height]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <canvas ref={canvasRef} width={width} height={height} style={{ width: "100%", height: "auto", background: "#000" }} />
      <audio ref={audioRef} src={audioUrl} controls />
    </div>
  );
}


