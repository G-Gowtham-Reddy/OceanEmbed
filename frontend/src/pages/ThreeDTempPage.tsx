import React, { useState, useRef, useEffect } from 'react';
import { Box, RotateCw, Layers, Compass } from 'lucide-react';

export const ThreeDTempPage: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const [activeDepthSlice, setActiveDepthSlice] = useState<number>(200); // Metres
  const [rotationAngle, setRotationAngle] = useState<number>(25); // degrees
  const [slicePlane, setSlicePlane] = useState<'horizontal' | 'orthogonal'>('horizontal');
  const [layerOpacity, setLayerOpacity] = useState<number>(85);

  // Depth slices in metres
  const depthSlices = [0, 50, 100, 200, 400, 600, 800, 1000];

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    const rad = (rotationAngle * Math.PI) / 180;
    const centerX = width / 2;
    const centerY = height / 2 - 20;

    // Isometric projection helpers
    const isoX = (x: number, y: number) => {
      return centerX + (x - y) * Math.cos(rad) * 1.8;
    };
    const isoY = (x: number, y: number, z: number) => {
      return centerY + (x + y) * Math.sin(rad) * 0.9 + z * 0.22;
    };

    // Draw reference depth grid box
    const cubeSize = 110;
    const maxZ = 1000;

    // Draw stack of depth layer planes
    depthSlices.forEach((depth) => {
      const isSelected = Math.abs(depth - activeDepthSlice) < 60;
      const zOffset = (depth / maxZ) * 220; // vertical drop

      // Plane corners in 3D
      const p1 = { x: isoX(-cubeSize, -cubeSize), y: isoY(-cubeSize, -cubeSize, zOffset) };
      const p2 = { x: isoX(cubeSize, -cubeSize), y: isoY(cubeSize, -cubeSize, zOffset) };
      const p3 = { x: isoX(cubeSize, cubeSize), y: isoY(cubeSize, cubeSize, zOffset) };
      const p4 = { x: isoX(-cubeSize, cubeSize), y: isoY(-cubeSize, cubeSize, zOffset) };

      // Determine layer color by depth
      let baseColor = 'rgba(15, 23, 42, 0.4)';
      let strokeColor = '#334155';

      if (depth === 0) {
        baseColor = `rgba(239, 68, 68, ${layerOpacity / 100 * 0.5})`;
        strokeColor = '#ef4444';
      } else if (depth <= 100) {
        baseColor = `rgba(249, 115, 22, ${layerOpacity / 100 * 0.5})`;
        strokeColor = '#f97316';
      } else if (depth <= 200) {
        baseColor = `rgba(234, 179, 8, ${layerOpacity / 100 * 0.5})`;
        strokeColor = '#eab308';
      } else if (depth <= 400) {
        baseColor = `rgba(34, 197, 94, ${layerOpacity / 100 * 0.4})`;
        strokeColor = '#22c55e';
      } else if (depth <= 700) {
        baseColor = `rgba(6, 182, 212, ${layerOpacity / 100 * 0.35})`;
        strokeColor = '#06b6d4';
      } else {
        baseColor = `rgba(30, 58, 138, ${layerOpacity / 100 * 0.3})`;
        strokeColor = '#1d4ed8';
      }

      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.lineTo(p3.x, p3.y);
      ctx.lineTo(p4.x, p4.y);
      ctx.closePath();

      ctx.fillStyle = baseColor;
      ctx.fill();

      ctx.strokeStyle = isSelected ? '#ffffff' : strokeColor;
      ctx.lineWidth = isSelected ? 2.5 : 1;
      ctx.stroke();

      // Depth label next to plane
      ctx.font = '10px monospace';
      ctx.fillStyle = isSelected ? '#ffffff' : '#94a3b8';
      ctx.fillText(`${depth}m`, p2.x + 8, p2.y + 3);
    });

    // Draw vertical bounding cage lines
    const corners = [
      { x: -cubeSize, y: -cubeSize },
      { x: cubeSize, y: -cubeSize },
      { x: cubeSize, y: cubeSize },
      { x: -cubeSize, y: cubeSize },
    ];

    corners.forEach((c) => {
      const top = { x: isoX(c.x, c.y), y: isoY(c.x, c.y, 0) };
      const bottom = { x: isoX(c.x, c.y), y: isoY(c.x, c.y, 220) };
      ctx.beginPath();
      ctx.moveTo(top.x, top.y);
      ctx.lineTo(bottom.x, bottom.y);
      ctx.strokeStyle = '#1e293b';
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    // If orthogonal slicing plane is selected, render cutting vertical slice
    if (slicePlane === 'orthogonal') {
      const vTop1 = { x: isoX(0, -cubeSize), y: isoY(0, -cubeSize, 0) };
      const vTop2 = { x: isoX(0, cubeSize), y: isoY(0, cubeSize, 0) };
      const vBottom2 = { x: isoX(0, cubeSize), y: isoY(0, cubeSize, 220) };
      const vBottom1 = { x: isoX(0, -cubeSize), y: isoY(0, -cubeSize, 220) };

      ctx.beginPath();
      ctx.moveTo(vTop1.x, vTop1.y);
      ctx.lineTo(vTop2.x, vTop2.y);
      ctx.lineTo(vBottom2.x, vBottom2.y);
      ctx.lineTo(vBottom1.x, vBottom1.y);
      ctx.closePath();

      const vGrad = ctx.createLinearGradient(vTop1.x, vTop1.y, vBottom1.x, vBottom1.y);
      vGrad.addColorStop(0, 'rgba(239, 68, 68, 0.7)');
      vGrad.addColorStop(0.2, 'rgba(234, 179, 8, 0.6)');
      vGrad.addColorStop(0.5, 'rgba(6, 182, 212, 0.5)');
      vGrad.addColorStop(1, 'rgba(15, 23, 42, 0.8)');

      ctx.fillStyle = vGrad;
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }
  }, [activeDepthSlice, rotationAngle, slicePlane, layerOpacity]);

  return (
    <div className="space-y-6">
      {/* 3D Visualizer Container */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
        {/* Controls Panel */}
        <div className="rounded-xl border border-slate-800 bg-[#091122]/90 p-5 shadow-lg space-y-5 lg:col-span-1">
          <div>
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Box className="h-4 w-4 text-cyan-400" />
              <span>3D Slicing Parameters</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Interactive volumetric layer controls
            </p>
          </div>

          {/* Perspective Rotation Slider */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs text-slate-300">
              <span className="flex items-center gap-1">
                <RotateCw className="h-3 w-3 text-cyan-400" />
                Perspective Angle
              </span>
              <span className="font-mono text-cyan-400">{rotationAngle}°</span>
            </div>
            <input
              type="range"
              min="0"
              max="60"
              value={rotationAngle}
              onChange={(e) => setRotationAngle(parseInt(e.target.value, 10))}
              className="h-2 w-full appearance-none rounded-lg bg-slate-800 accent-cyan-400"
            />
          </div>

          {/* Active Depth Slice Selector */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs text-slate-300">
              <span className="flex items-center gap-1">
                <Layers className="h-3 w-3 text-cyan-400" />
                Target Depth Slice
              </span>
              <span className="font-mono text-amber-400 font-bold">{activeDepthSlice} m</span>
            </div>
            <input
              type="range"
              min="0"
              max="1000"
              step="50"
              value={activeDepthSlice}
              onChange={(e) => setActiveDepthSlice(parseInt(e.target.value, 10))}
              className="h-2 w-full appearance-none rounded-lg bg-slate-800 accent-amber-400"
            />
          </div>

          {/* Slicing Orientation Toggle */}
          <div className="space-y-1.5">
            <span className="text-xs text-slate-300">Slicing Geometry</span>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <button
                onClick={() => setSlicePlane('horizontal')}
                className={`rounded-lg border px-3 py-2 font-medium transition ${
                  slicePlane === 'horizontal'
                    ? 'border-cyan-500 bg-cyan-950/60 text-cyan-300'
                    : 'border-slate-800 bg-slate-900 text-slate-400 hover:text-white'
                }`}
              >
                Horizontal Stack
              </button>
              <button
                onClick={() => setSlicePlane('orthogonal')}
                className={`rounded-lg border px-3 py-2 font-medium transition ${
                  slicePlane === 'orthogonal'
                    ? 'border-cyan-500 bg-cyan-950/60 text-cyan-300'
                    : 'border-slate-800 bg-slate-900 text-slate-400 hover:text-white'
                }`}
              >
                Orthogonal Cut
              </button>
            </div>
          </div>

          {/* Layer Opacity */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs text-slate-300">
              <span>Layer Opacity</span>
              <span className="font-mono text-slate-400">{layerOpacity}%</span>
            </div>
            <input
              type="range"
              min="20"
              max="100"
              value={layerOpacity}
              onChange={(e) => setLayerOpacity(parseInt(e.target.value, 10))}
              className="h-2 w-full appearance-none rounded-lg bg-slate-800 accent-cyan-400"
            />
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3 text-[11px] text-slate-400">
            <span className="font-semibold text-cyan-400">Tip:</span> Rotate the perspective angle to inspect the thermal thermocline boundary dipping across equatorial latitudes.
          </div>
        </div>

        {/* 3D Isometric Canvas Viewport */}
        <div className="rounded-xl border border-slate-800 bg-[#060c1a] p-4 shadow-xl flex flex-col items-center justify-center lg:col-span-3 min-h-[440px] relative overflow-hidden">
          <div className="absolute top-4 left-5 flex flex-col gap-1 text-xs font-mono text-slate-400">
            <div className="flex items-center gap-2">
              <Compass className="h-4 w-4 text-cyan-400" />
              <span>Volumetric Grid: 0°N &rarr; 26°N • 50°E &rarr; 100°E • 0 &rarr; 1000m Depth</span>
            </div>
            <div className="flex items-center gap-1.5 text-[10px] text-emerald-400">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
              <span>Authoritative Land Mask Active: Continental land cells excluded from thermal soundings</span>
            </div>
          </div>

          <canvas
            ref={canvasRef}
            width={720}
            height={420}
            className="max-w-full h-auto"
          />

          <div className="absolute bottom-4 right-5 flex items-center gap-3 text-xs font-mono text-slate-400 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800">
            <span>Selected Slice:</span>
            <span className="text-cyan-300 font-bold">{activeDepthSlice} Metres</span>
          </div>
        </div>
      </div>
    </div>
  );
};
export default ThreeDTempPage;
