"use client";

import { useEffect, useState } from "react";

export default function SkeletonLoader() {
  const [activeBlock, setActiveBlock] = useState(0);
  const [loadedBlocks, setLoadedBlocks] = useState(0); // Track how many blocks have been loaded
  const totalBlocks = 5;

  useEffect(() => {
    const startAnimation = () => {
      const interval = setInterval(() => {
        setActiveBlock((prev) => {
          if (prev < totalBlocks) {
            const next = prev + 1;
            setLoadedBlocks(next); // Update loaded blocks count
            return next;
          } else {
            // Animation complete, clear interval and pause
            clearInterval(interval);
            setTimeout(() => {
              setActiveBlock(0); // Reset to start
              setLoadedBlocks(0); // Reset loaded blocks
              startAnimation(); // Restart the animation
            }, 2000);
            return -1; // Clear highlight during pause
          }
        });
      }, 800);

      return interval;
    };

    const interval = startAnimation();
    return () => clearInterval(interval);
  }, []); // Empty dependency array to run only once

  return (
    <div className="w-full max-w-2xl mx-auto p-4 md:p-6 bg-linear-to-br from-slate-900 via-blue-950 to-purple-950 rounded-3xl border border-slate-800 shadow-xl">
      {/* Browser Header */}
      <div className="flex items-center gap-2 mb-4 md:mb-6"></div>

      {/* Content */}
      <div className="space-y-3 md:space-y-4">
        {/* Title */}
        <h2 className="text-lg md:text-xl font-inter text-slate-300 mb-4 md:mb-6">
          Cargando ...
        </h2>

        {/* Top wide block */}
        <div className="relative overflow-hidden">
          <div
            className={`h-10 md:h-12 bg-slate-800/80 rounded-md border-2 border-slate-700 transition-opacity duration-300 ${
              loadedBlocks >= 1 || activeBlock === -1
                ? "opacity-100"
                : "opacity-0"
            }`}
            style={{
              clipPath:
                loadedBlocks >= 1 || activeBlock === -1
                  ? "inset(0 0 0 0)"
                  : "inset(0 100% 0 0)",
              animation:
                activeBlock === 1
                  ? "reveal-block 0.6s ease-out forwards"
                  : "none",
            }}
          />
          {activeBlock === 1 && (
            <div className="absolute inset-0 h-10 md:h-12 bg-transparent rounded-md border-2 border-dashed border-cyan-400/60 animate-grow-in" />
          )}
        </div>

        {/* Middle row - two blocks */}
        <div
          className="grid gap-3 md:gap-4"
          style={{ gridTemplateColumns: "35% 1fr" }}
        >
          <div className="relative overflow-hidden">
            <div
              className={`h-10 md:h-12 bg-slate-800/80 rounded-md border-2 border-slate-700 transition-opacity duration-300 ${
                loadedBlocks >= 2 || activeBlock === -1
                  ? "opacity-100"
                  : "opacity-0"
              }`}
              style={{
                clipPath:
                  loadedBlocks >= 2 || activeBlock === -1
                    ? "inset(0 0 0 0)"
                    : "inset(0 100% 0 0)",
                animation:
                  activeBlock === 2
                    ? "reveal-block 0.6s ease-out forwards"
                    : "none",
              }}
            />
            {activeBlock === 2 && (
              <div className="absolute inset-0 h-10 md:h-12 bg-transparent rounded-md border-2 border-dashed border-cyan-400/60 animate-grow-in" />
            )}
          </div>
          <div className="relative overflow-hidden">
            <div
              className={`h-10 md:h-12 bg-slate-800/80 rounded-md border-2 border-slate-700 transition-opacity duration-300 ${
                loadedBlocks >= 3 || activeBlock === -1
                  ? "opacity-100"
                  : "opacity-0"
              }`}
              style={{
                clipPath:
                  loadedBlocks >= 3 || activeBlock === -1
                    ? "inset(0 0 0 0)"
                    : "inset(0 100% 0 0)",
                animation:
                  activeBlock === 3
                    ? "reveal-block 0.6s ease-out forwards"
                    : "none",
              }}
            />
            {activeBlock === 3 && (
              <div className="absolute inset-0 h-10 md:h-12 bg-transparent rounded-md border-2 border-dashed border-cyan-400/60 animate-grow-in" />
            )}
          </div>
        </div>

        {/* Bottom row - two blocks */}
        <div
          className="grid gap-3 md:gap-4"
          style={{ gridTemplateColumns: "65% 1fr" }}
        >
          <div className="relative overflow-hidden">
            <div
              className={`h-10 md:h-12 bg-slate-800/80 rounded-md border-2 border-slate-700 transition-opacity duration-300 ${
                loadedBlocks >= 4 || activeBlock === -1
                  ? "opacity-100"
                  : "opacity-0"
              }`}
              style={{
                clipPath:
                  loadedBlocks >= 4 || activeBlock === -1
                    ? "inset(0 0 0 0)"
                    : "inset(0 100% 0 0)",
                animation:
                  activeBlock === 4
                    ? "reveal-block 0.6s ease-out forwards"
                    : "none",
              }}
            />
            {activeBlock === 4 && (
              <div className="absolute inset-0 h-10 md:h-12 bg-transparent rounded-md border-2 border-dashed border-cyan-400/60 animate-grow-in" />
            )}
          </div>
          <div className="relative overflow-hidden">
            <div
              className={`h-10 md:h-12 bg-slate-800/80 rounded-md border-2 border-slate-700 transition-opacity duration-300 ${
                loadedBlocks >= 5 || activeBlock === -1
                  ? "opacity-100"
                  : "opacity-0"
              }`}
              style={{
                clipPath:
                  loadedBlocks >= 5 || activeBlock === -1
                    ? "inset(0 0 0 0)"
                    : "inset(0 100% 0 0)",
                animation:
                  activeBlock === 5
                    ? "reveal-block 0.6s ease-out forwards"
                    : "none",
              }}
            />
            {activeBlock === 5 && (
              <div className="absolute inset-0 h-10 md:h-12 bg-transparent rounded-md border-2 border-dashed border-cyan-400/60 animate-grow-in" />
            )}
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes grow-in {
          0% {
            width: 0%;
            opacity: 1;
          }
          100% {
            width: 100%;
            opacity: 1;
          }
        }
        /* Added reveal-block animation for progressive content reveal */
        @keyframes reveal-block {
          0% {
            clip-path: inset(0 100% 0 0);
          }
          100% {
            clip-path: inset(0 0 0 0);
          }
        }
        @keyframes fade-in {
          0% {
            opacity: 0;
          }
          100% {
            opacity: 1;
          }
        }
        .animate-grow-in {
          animation: grow-in 0.6s ease-out forwards;
        }
        .animate-fade-in {
          animation: fade-in 0.3s ease-out forwards;
        }
      `}</style>
    </div>
  );
}
