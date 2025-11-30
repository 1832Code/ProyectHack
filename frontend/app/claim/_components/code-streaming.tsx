"use client";

import { useEffect, useState } from "react";

interface CodeSegment {
  id: number;
  width: number; // pixel width
  color: string;
  animated: boolean;
}

interface CodeLine {
  id: number;
  segments: CodeSegment[];
  indent: number;
  completed: boolean;
}

const codeColors = [
  "bg-cyan-400/90",
  "bg-slate-400/80",
  "bg-cyan-300/80",
  "bg-violet-400/90",
  "bg-indigo-400/80",
  "bg-slate-500",
];

const linePatterns = [
  {
    segments: [
      { width: 80, color: 0 },
      { width: 60, color: 1 },
      { width: 20, color: 2 },
      { width: 120, color: 3 },
    ],
    indent: 0,
  },
  {
    segments: [
      { width: 100, color: 1 },
      { width: 140, color: 4 },
    ],
    indent: 1,
  },
  {
    segments: [
      { width: 160, color: 2 },
      { width: 90, color: 1 },
      { width: 12, color: 0 },
    ],
    indent: 1,
  },
  {
    segments: [
      { width: 70, color: 3 },
      { width: 12, color: 1 },
    ],
    indent: 2,
  },
  { segments: [{ width: 120, color: 4 }], indent: 2 },
  { segments: [{ width: 90, color: 1 }], indent: 2 },
  { segments: [{ width: 110, color: 2 }], indent: 2 },
  { segments: [{ width: 12, color: 0 }], indent: 1 },
  {
    segments: [
      { width: 140, color: 1 },
      { width: 80, color: 3 },
    ],
    indent: 0,
  },
];

export default function CodeStreaming() {
  const [lines, setLines] = useState<CodeLine[]>([]);
  const [currentLine, setCurrentLine] = useState<CodeLine | null>(null);
  const [headerDots, setHeaderDots] = useState(0);

  useEffect(() => {
    let lineId = 0;
    let patternIndex = 0;
    let animationRunning = true;

    const animateHeader = () => {
      if (!animationRunning) return;
      setHeaderDots((prev) => (prev + 1) % 4);
      setTimeout(animateHeader, 800);
    };
    animateHeader();

    const startNewLine = () => {
      if (!animationRunning) return;

      const pattern = linePatterns[patternIndex % linePatterns.length];

      const newLine: CodeLine = {
        id: lineId++,
        segments: pattern.segments.map((seg, index) => ({
          id: index,
          width: seg.width,
          color: codeColors[seg.color],
          animated: false,
        })),
        indent: pattern.indent,
        completed: false,
      };

      setCurrentLine(newLine);
      patternIndex++;

      let segmentIndex = 0;
      const animateNextSegment = () => {
        if (segmentIndex >= newLine.segments.length) {
          setLines((prevLines) => [
            ...prevLines.slice(-11),
            { ...newLine, completed: true },
          ]);
          setCurrentLine(null);

          setTimeout(() => {
            if (animationRunning) {
              startNewLine();
            }
          }, 150);
          return;
        }

        setCurrentLine((prev) => {
          if (!prev) return prev;
          if (segmentIndex >= prev.segments.length) return prev;

          const updated = { ...prev };
          updated.segments = [...prev.segments];
          updated.segments[segmentIndex] = {
            ...prev.segments[segmentIndex],
            animated: true,
          };
          return updated;
        });

        segmentIndex++;
        setTimeout(animateNextSegment, 150 + segmentIndex * 50);
      };

      setTimeout(animateNextSegment, 100);
    };

    startNewLine();

    return () => {
      animationRunning = false;
    };
  }, []);

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-linear-to-br from-slate-900/60 via-blue-950/30 to-purple-950/40 rounded-md border border-slate-800 overflow-hidden shadow-xl">
        <div className="bg-transparent/20 px-3 md:px-4 py-2 md:py-3 border-b border-slate-700 flex items-center gap-2 backdrop-blur-sm">
          <div className="flex gap-2"></div>
          <div className="ml-4 text-slate-300 text-sm font-mono flex items-center gap-1">
            <span>component.tsx</span>
            <div className="flex gap-1 ml-2">
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className={`w-1 h-1 rounded-full transition-all duration-300 ${
                    i < headerDots ? "bg-cyan-400/90" : "bg-slate-600"
                  }`}
                />
              ))}
            </div>
          </div>
        </div>

        <div className="bg-linear-to-t from-transparent to-slate-900/80 p-3 md:p-4 h-48 md:h-64 relative flex flex-col justify-end overflow-hidden">
          <div className="space-y-2 md:space-y-3">
            {lines.map((line, index) => (
              <div
                key={line.id}
                className="flex items-center gap-2 transition-all duration-300 ease-out"
                style={{
                  transform: `translateY(${-(lines.length - 1 - index) * 2}px)`,
                  opacity: Math.max(0.3, 1 - (lines.length - 1 - index) * 0.08),
                  marginLeft: `${line.indent * 16}px`,
                }}
              >
                {line.segments.map((segment) => (
                  <div
                    key={segment.id}
                    className={`h-3 md:h-4 rounded-sm ${segment.color} shadow-[0_1px_8px_rgba(99,102,241,0.06)]`}
                    style={{ width: `${segment.width * 0.8}px` }}
                  />
                ))}
              </div>
            ))}

            {currentLine && (
              <div
                className="flex items-center gap-2"
                style={{ marginLeft: `${currentLine.indent * 16}px` }}
              >
                {currentLine.segments.map((segment) => (
                  <div
                    key={segment.id}
                    className={`h-3 md:h-4 rounded-sm ${
                      segment.color
                    } transition-all duration-500 ease-out ${
                      segment.animated ? "opacity-100" : "opacity-0"
                    }`}
                    style={{
                      width: segment.animated
                        ? `${segment.width * 0.8}px`
                        : "0px",
                      boxShadow: segment.animated
                        ? "0 6px 18px rgba(99,102,241,0.12)"
                        : undefined,
                    }}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
