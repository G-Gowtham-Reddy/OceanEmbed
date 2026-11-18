import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RotateCw, Maximize2, Layers, Compass, Waves } from 'lucide-react';

export interface DepthProfilePoint {
  depth: number;
  temperature: number;
}

export interface ThreeDOceanModelProps {
  profile?: DepthProfilePoint[];
  regionName?: string;
  coordinates?: string;
  surfaceTemp?: number;
  mld?: number;
  thermoclineDepth?: number;
  targetDepthTemp?: number;
  maxDepth?: number;
}

// Map temperature (°C) to realistic ocean thermal color
function getThermalColor(temp: number, minT: number = 2, maxT: number = 30): { r: number; g: number; b: number; hex: string } {
  const norm = Math.max(0, Math.min(1, (temp - minT) / (maxT - minT || 1)));
  let r: number, g: number, b: number;

  if (norm > 0.8) {
    // 25 - 30°C: Warm tropical amber to orange-red
    const t = (norm - 0.8) / 0.2;
    r = Math.round(245 + t * 10);
    g = Math.round(158 - t * 68);
    b = Math.round(11 - t * 11);
  } else if (norm > 0.55) {
    // 18 - 25°C: Golden yellow to amber
    const t = (norm - 0.55) / 0.25;
    r = Math.round(210 + t * 35);
    g = Math.round(195 - t * 37);
    b = Math.round(40 - t * 29);
  } else if (norm > 0.35) {
    // 12 - 18°C: Light turquoise to green-yellow
    const t = (norm - 0.35) / 0.2;
    r = Math.round(34 + t * 176);
    g = Math.round(197 - t * 2);
    b = Math.round(140 - t * 100);
  } else if (norm > 0.15) {
    // 6 - 12°C: Cyan to teal
    const t = (norm - 0.15) / 0.2;
    r = Math.round(6 + t * 28);
    g = Math.round(140 + t * 57);
    b = Math.round(214 - t * 74);
  } else {
    // 2 - 6°C: Abyssal deep oceanic blue
    const t = norm / 0.15;
    r = Math.round(3 + t * 3);
    g = Math.round(15 + t * 125);
    b = Math.round(50 + t * 164);
  }

  const hex = `rgb(${r},${g},${b})`;
  return { r, g, b, hex };
}

// Generate dynamic 2D canvas texture matching the actual temperature profile
function createDynamicThermalTexture(profile?: DepthProfilePoint[], maxDepth: number = 1500): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 1024;
  const ctx = canvas.getContext('2d')!;

  const validProfile = (profile && profile.length > 0)
    ? [...profile].sort((a, b) => a.depth - b.depth)
    : [
        { depth: 0, temperature: 28.5 },
        { depth: 50, temperature: 27.8 },
        { depth: 100, temperature: 24.2 },
        { depth: 200, temperature: 18.5 },
        { depth: 500, temperature: 11.4 },
        { depth: 1000, temperature: 6.2 },
        { depth: 1500, temperature: 3.8 },
      ];

  const temps = validProfile.map((p) => p.temperature);
  const minT = Math.min(...temps, 2);
  const maxT = Math.max(...temps, 30);

  // Helper to interpolate temperature at any depth 0..maxDepth
  const getTempAtDepth = (d: number): number => {
    if (d <= validProfile[0].depth) return validProfile[0].temperature;
    if (d >= validProfile[validProfile.length - 1].depth) {
      return validProfile[validProfile.length - 1].temperature;
    }
    for (let i = 0; i < validProfile.length - 1; i++) {
      if (d >= validProfile[i].depth && d <= validProfile[i + 1].depth) {
        const factor = (d - validProfile[i].depth) / (validProfile[i + 1].depth - validProfile[i].depth);
        return validProfile[i].temperature + factor * (validProfile[i + 1].temperature - validProfile[i].temperature);
      }
    }
    return 10;
  };

  // 1. Create smooth multi-stop linear gradient
  const grad = ctx.createLinearGradient(0, 0, 0, 1024);
  const steps = 30;
  for (let s = 0; s <= steps; s++) {
    const ratio = s / steps;
    const currentDepth = ratio * maxDepth;
    const temp = getTempAtDepth(currentDepth);
    const { hex } = getThermalColor(temp, minT, maxT);
    grad.addColorStop(ratio, hex);
  }

  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 512, 1024);

  // 2. Overlay subtle hydrodynamic shear turbulence
  ctx.save();
  for (let i = 0; i < 7; i++) {
    const yCenter = (150 + i * 110) * (1024 / 1000);
    const radGrad = ctx.createRadialGradient(256 + Math.sin(i * 1.5) * 80, yCenter, 20, 256, yCenter, 220);
    radGrad.addColorStop(0, 'rgba(255, 255, 255, 0.09)');
    radGrad.addColorStop(0.5, 'rgba(6, 182, 212, 0.05)');
    radGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = radGrad;
    ctx.fillRect(0, yCenter - 140, 512, 280);
  }
  ctx.restore();

  // 3. Draw fine oceanic isotherm contour lines
  ctx.lineWidth = 1.0;
  for (let y = 15; y < 1024; y += 14) {
    const depthFrac = y / 1024;
    ctx.beginPath();
    ctx.strokeStyle = `rgba(255, 255, 255, ${0.12 - depthFrac * 0.08})`;
    for (let x = 0; x <= 512; x += 16) {
      const wave = Math.sin(x * 0.025 + y * 0.04) * (4.0 * (1.0 - depthFrac * 0.5));
      if (x === 0) ctx.moveTo(x, y + wave);
      else ctx.lineTo(x, y + wave);
    }
    ctx.stroke();
  }

  // 4. Highlighted key depth transition markers
  const keyDepths = [150, 500, 1000];
  keyDepths.forEach((kd) => {
    if (kd <= maxDepth) {
      const yPos = (kd / maxDepth) * 1024;
      ctx.beginPath();
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.28)';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.moveTo(0, yPos);
      ctx.lineTo(512, yPos);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  });

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.ClampToEdgeWrapping;
  texture.wrapT = THREE.ClampToEdgeWrapping;
  texture.minFilter = THREE.LinearFilter;
  texture.magFilter = THREE.LinearFilter;
  return texture;
}

export const ThreeDOceanModel: React.FC<ThreeDOceanModelProps> = ({
  profile,
  regionName = 'Equatorial Indian Ocean',
  coordinates = '0°N - 10°S, 60°E - 90°E',
  surfaceTemp,
  mld,
  thermoclineDepth,
  targetDepthTemp,
  maxDepth = 1500,
}) => {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const [autoRotate, setAutoRotate] = useState<boolean>(true);
  const [showCage, setShowCage] = useState<boolean>(true);

  // References to keep Three.js entities
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const cageRef = useRef<THREE.LineSegments | null>(null);
  const sideMatRef = useRef<THREE.MeshPhongMaterial | null>(null);
  const depthLabelsRef = useRef<{ [key: number]: string }>({});

  // Compute temperatures for depth markers from the profile
  const getTempAt = (d: number): number => {
    if (!profile || profile.length === 0) {
      if (d === 0) return surfaceTemp ?? 28.5;
      if (d === 500) return 11.4;
      if (d === 1000) return 6.2;
      if (d === 1500) return targetDepthTemp ?? 3.8;
      return 10;
    }
    const match = profile.find((p) => Math.abs(p.depth - d) < 15);
    if (match) return match.temperature;
    // Interpolate
    const sorted = [...profile].sort((a, b) => a.depth - b.depth);
    if (d <= sorted[0].depth) return sorted[0].temperature;
    if (d >= sorted[sorted.length - 1].depth) return sorted[sorted.length - 1].temperature;
    for (let i = 0; i < sorted.length - 1; i++) {
      if (d >= sorted[i].depth && d <= sorted[i + 1].depth) {
        const factor = (d - sorted[i].depth) / (sorted[i + 1].depth - sorted[i].depth);
        return Number((sorted[i].temperature + factor * (sorted[i + 1].temperature - sorted[i].temperature)).toFixed(1));
      }
    }
    return 10;
  };

  const temp0m = (surfaceTemp ?? getTempAt(0)).toFixed(1);
  const temp500m = getTempAt(500).toFixed(1);
  const temp1000m = getTempAt(1000).toFixed(1);
  const temp1500m = (targetDepthTemp ?? getTempAt(1500)).toFixed(1);

  depthLabelsRef.current = {
    0: `${temp0m}°C`,
    500: `${temp500m}°C`,
    1000: `${temp1000m}°C`,
    1500: `${temp1500m}°C`,
  };

  // Update dynamic texture when profile changes
  useEffect(() => {
    if (sideMatRef.current) {
      const newTexture = createDynamicThermalTexture(profile, maxDepth);
      if (sideMatRef.current.map) {
        sideMatRef.current.map.dispose();
      }
      sideMatRef.current.map = newTexture;
      sideMatRef.current.needsUpdate = true;
    }
  }, [profile, maxDepth]);

  // Main Three.js Scene Setup
  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight;

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x060913);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 1000);
    camera.position.set(15.5, 9.2, 17.5);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.1;
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(0, 0, 0);
    controls.maxDistance = 45;
    controls.minDistance = 6;
    controls.autoRotate = autoRotate;
    controls.autoRotateSpeed = 0.5;
    controlsRef.current = controls;

    // 2. Lighting
    const ambLight = new THREE.AmbientLight(0xdff2ff, 1.25);
    scene.add(ambLight);

    const sunLight = new THREE.DirectionalLight(0xfff7e6, 2.8);
    sunLight.position.set(20, 32, 18);
    scene.add(sunLight);

    const blueRim = new THREE.DirectionalLight(0x00d4ff, 1.6);
    blueRim.position.set(-22, -10, -20);
    scene.add(blueRim);

    const deepLight = new THREE.PointLight(0x0284c7, 1.8, 30);
    deepLight.position.set(0, -5, 0);
    scene.add(deepLight);

    // 3. Materials
    const initialTexture = createDynamicThermalTexture(profile, maxDepth);
    const cutawaySideMat = new THREE.MeshPhongMaterial({
      map: initialTexture,
      transparent: true,
      opacity: 0.78,
      shininess: 45,
      specular: new THREE.Color(0x38bdf8),
      side: THREE.DoubleSide,
      depthWrite: true,
    });
    sideMatRef.current = cutawaySideMat;

    const bottomMat = new THREE.MeshPhongMaterial({
      color: 0x010814,
      shininess: 15,
      side: THREE.DoubleSide,
    });

    // 4. Vertical Ocean Column Walls (Translucent)
    const boxSize = 12.0;
    const halfBox = boxSize / 2;

    const wallGeomZ = new THREE.PlaneGeometry(boxSize, boxSize);
    const wallFront = new THREE.Mesh(wallGeomZ, cutawaySideMat);
    wallFront.position.set(0, 0, halfBox);
    scene.add(wallFront);

    const wallBack = new THREE.Mesh(wallGeomZ, cutawaySideMat);
    wallBack.position.set(0, 0, -halfBox);
    scene.add(wallBack);

    const wallGeomX = new THREE.PlaneGeometry(boxSize, boxSize);
    const wallRight = new THREE.Mesh(wallGeomX, cutawaySideMat);
    wallRight.position.set(halfBox, 0, 0);
    wallRight.rotation.y = Math.PI / 2;
    scene.add(wallRight);

    const wallLeft = new THREE.Mesh(wallGeomX, cutawaySideMat);
    wallLeft.position.set(-halfBox, 0, 0);
    wallLeft.rotation.y = Math.PI / 2;
    scene.add(wallLeft);

    const seabedMesh = new THREE.Mesh(new THREE.PlaneGeometry(boxSize, boxSize), bottomMat);
    seabedMesh.rotation.x = Math.PI / 2;
    seabedMesh.position.y = -halfBox;
    scene.add(seabedMesh);

    // 5. Procedural Seabed Craggy Rocks & Marine Kelp Plants
    const rockMat = new THREE.MeshPhongMaterial({
      color: 0x0f172a,
      roughness: 0.85,
      shininess: 10,
    });
    const rockGeo = new THREE.DodecahedronGeometry(0.7, 1);
    for (let r = 0; r < 10; r++) {
      const rock = new THREE.Mesh(rockGeo, rockMat);
      const rx = (Math.sin(r * 2.3) * 0.75) * (halfBox - 1.2);
      const rz = (Math.cos(r * 1.9) * 0.75) * (halfBox - 1.2);
      const scale = 0.5 + Math.abs(Math.sin(r * 3.1)) * 0.8;
      rock.scale.set(scale * 1.4, scale * 0.8, scale * 1.2);
      rock.position.set(rx, -halfBox + (scale * 0.4), rz);
      rock.rotation.set(r * 0.5, r * 1.2, r * 0.8);
      scene.add(rock);
    }

    // Kelp Flora Clusters
    const kelpClusters: THREE.Group[] = [];
    const kelpMat = new THREE.MeshPhongMaterial({
      color: 0x0d9488,
      emissive: 0x042f2e,
      shininess: 20,
      side: THREE.DoubleSide,
    });
    for (let k = 0; k < 7; k++) {
      const cluster = new THREE.Group();
      const kx = (Math.sin(k * 1.7 + 0.5) * 0.7) * (halfBox - 1.5);
      const kz = (Math.cos(k * 2.1 + 0.8) * 0.7) * (halfBox - 1.5);
      const bladeCount = 5 + (k % 3);
      for (let b = 0; b < bladeCount; b++) {
        const bladeGeo = new THREE.PlaneGeometry(0.12, 1.8 + (b % 4) * 0.4, 1, 6);
        const blade = new THREE.Mesh(bladeGeo, kelpMat);
        blade.position.set((b - 2) * 0.08, 0.9 + (b % 4) * 0.2, (b % 2) * 0.08);
        blade.rotation.y = (b * Math.PI) / 3;
        cluster.add(blade);
      }
      cluster.position.set(kx, -halfBox, kz);
      scene.add(cluster);
      kelpClusters.push(cluster);
    }

    // 6. Dynamic Top Animated Wave Surface Mesh
    const waveRes = 48;
    const waveGeom = new THREE.PlaneGeometry(boxSize, boxSize, waveRes, waveRes);
    waveGeom.rotateX(-Math.PI / 2);
    const wavePosAttr = waveGeom.attributes.position;
    const waveOrigY = new Float32Array(wavePosAttr.count);
    for (let i = 0; i < wavePosAttr.count; i++) {
      waveOrigY[i] = wavePosAttr.getY(i);
    }

    const waveMat = new THREE.MeshPhongMaterial({
      color: 0x0284c7,
      emissive: 0x032845,
      shininess: 120,
      specular: new THREE.Color(0xffffff),
      transparent: true,
      opacity: 0.88,
      side: THREE.DoubleSide,
      depthWrite: true,
    });
    const waveMesh = new THREE.Mesh(waveGeom, waveMat);
    waveMesh.position.y = halfBox;
    scene.add(waveMesh);

    // 7. Realistic Surface Argo Float Model (~2m scale at corner X=6, Z=6)
    const floatGroup = new THREE.Group();
    floatGroup.position.set(halfBox, halfBox, halfBox);

    // Submerged yellow hull
    const hullMat = new THREE.MeshPhongMaterial({ color: 0xf59e0b, shininess: 80 });
    const hullMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.9, 24), hullMat);
    hullMesh.position.y = -0.35;
    floatGroup.add(hullMesh);

    // Black bottom collar
    const collarMat = new THREE.MeshPhongMaterial({ color: 0x111827, shininess: 40 });
    const collarMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.13, 0.18, 24), collarMat);
    collarMesh.position.y = -0.78;
    floatGroup.add(collarMesh);

    // Stabilizer damping disk
    const diskMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.25, 0.04, 24), collarMat);
    diskMesh.position.y = -0.87;
    floatGroup.add(diskMesh);

    // Top cap & antenna mast
    const capMat = new THREE.MeshPhongMaterial({ color: 0x38bdf8, shininess: 90 });
    const capMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.12, 0.12, 24), capMat);
    capMesh.position.y = 0.12;
    floatGroup.add(capMesh);

    const mastMat = new THREE.MeshBasicMaterial({ color: 0xe2e8f0 });
    const mastMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.45, 12), mastMat);
    mastMesh.position.y = 0.38;
    floatGroup.add(mastMesh);

    // Blinking satellite beacon LED
    const ledMat = new THREE.MeshBasicMaterial({ color: 0x22c55e });
    const ledMesh = new THREE.Mesh(new THREE.SphereGeometry(0.04, 12, 12), ledMat);
    ledMesh.position.y = 0.62;
    floatGroup.add(ledMesh);

    scene.add(floatGroup);

    // 8. Vertical Profiling Sounding Beam (0m down to 1500m)
    const beamGeom = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(halfBox, halfBox, halfBox),
      new THREE.Vector3(halfBox, -halfBox, halfBox),
    ]);
    const beamMat = new THREE.LineDashedMaterial({
      color: 0x38bdf8,
      dashSize: 0.35,
      gapSize: 0.18,
      linewidth: 2,
    });
    const soundingBeam = new THREE.Line(beamGeom, beamMat);
    soundingBeam.computeLineDistances();
    scene.add(soundingBeam);

    // 9. Glowing Depth Rings along Sounding Beam
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      wireframe: true,
      transparent: true,
      opacity: 0.65,
    });
    const depthLevels = [0, 500, 1000, 1500];
    depthLevels.forEach((depth) => {
      const ringFrac = depth / maxDepth;
      const ringY = halfBox - ringFrac * boxSize;
      const ringGeo = new THREE.TorusGeometry(0.75 + (depth === 0 ? 0.3 : 0), 0.02, 8, 36);
      ringGeo.rotateX(Math.PI / 2);
      const ringMesh = new THREE.Mesh(ringGeo, ringMat);
      ringMesh.position.set(halfBox, ringY, halfBox);
      scene.add(ringMesh);
    });

    // 10. Wireframe Structural Bounding Cage
    const cageBox = new THREE.BoxGeometry(boxSize, boxSize, boxSize);
    const cageEdges = new THREE.EdgesGeometry(cageBox);
    const cageLine = new THREE.LineSegments(
      cageEdges,
      new THREE.LineBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.28 })
    );
    scene.add(cageLine);
    cageRef.current = cageLine;

    // 11. Animation Loop
    let clock = new THREE.Clock();
    let animationFrameId: number;

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const t = clock.getElapsedTime();

      // Controls update (auto-rotate)
      controls.update();

      // Animate top waves
      for (let i = 0; i < wavePosAttr.count; i++) {
        const u = wavePosAttr.getX(i);
        const w = wavePosAttr.getZ(i);
        const yVal =
          Math.sin(u * 0.9 + t * 2.2) * 0.16 +
          Math.cos(w * 0.75 + t * 1.8) * 0.14 +
          Math.sin((u + w) * 0.5 + t * 3.0) * 0.08;
        wavePosAttr.setY(i, yVal);
      }
      wavePosAttr.needsUpdate = true;
      waveGeom.computeVertexNormals();

      // Animate Argo Float with realistic heave, pitch, and roll
      const heave = Math.sin(t * 2.2) * 0.16 + Math.cos(t * 1.8) * 0.12;
      const pitch = Math.sin(t * 1.9) * 0.08;
      const roll = Math.cos(t * 2.1) * 0.06;
      floatGroup.position.y = halfBox + heave;
      floatGroup.rotation.x = pitch;
      floatGroup.rotation.z = roll;

      // Blinking satellite beacon LED
      ledMat.color.setHex((Math.sin(t * 5.5) > 0.3) ? 0x22c55e : 0x042f14);

      // Swaying marine kelp flora
      for (let k = 0; k < kelpClusters.length; k++) {
        const cluster = kelpClusters[k];
        cluster.rotation.z = Math.sin(t * 1.4 + k) * 0.08;
        cluster.rotation.x = Math.cos(t * 1.2 + k * 0.7) * 0.06;
      }

      renderer.render(scene, camera);
    };

    animate();

    // Resize handler
    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
      renderer.dispose();
      if (renderer.domElement.parentNode) {
        renderer.domElement.parentNode.removeChild(renderer.domElement);
      }
    };
  }, []);

  // Update auto-rotate
  useEffect(() => {
    if (controlsRef.current) {
      controlsRef.current.autoRotate = autoRotate;
    }
  }, [autoRotate]);

  // Update cage visibility
  useEffect(() => {
    if (cageRef.current) {
      cageRef.current.visible = showCage;
    }
  }, [showCage]);

  // Reset view
  const handleResetView = () => {
    if (cameraRef.current && controlsRef.current) {
      cameraRef.current.position.set(15.5, 9.2, 17.5);
      controlsRef.current.target.set(0, 0, 0);
      controlsRef.current.update();
    }
  };

  return (
    <div className="relative w-full h-[660px] rounded-xl overflow-hidden border border-zinc-800 bg-[#060913] shadow-2xl flex flex-col font-sans select-none">
      {/* 1. TOP HEADER HUD */}
      <div className="absolute top-0 left-0 right-0 z-10 flex flex-wrap items-center justify-between gap-3 p-4 bg-gradient-to-b from-[#060913]/95 via-[#060913]/70 to-transparent pointer-events-none">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono tracking-widest text-cyan-400 uppercase">
              OceanEmbed Architecture
            </span>
            <span className="rounded border border-cyan-500/40 bg-cyan-950/40 px-1.5 py-0.2 text-[9px] font-mono text-cyan-300">
              Photorealistic 3D
            </span>
          </div>
          <h2 className="text-lg font-bold text-zinc-100 tracking-tight flex items-center gap-2">
            3D Subsurface Temperature Reconstruction
          </h2>
          <p className="text-xs text-zinc-400 font-mono">
            Location: <span className="text-cyan-300 font-medium">{regionName}</span> ({coordinates})
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 pointer-events-auto">
          <button
            onClick={() => setAutoRotate(!autoRotate)}
            className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-all ${
              autoRotate
                ? 'border-cyan-500/50 bg-cyan-950/50 text-cyan-200 shadow-[0_0_12px_rgba(6,182,212,0.25)]'
                : 'border-zinc-800 bg-zinc-900/80 text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <RotateCw className={`h-3.5 w-3.5 ${autoRotate ? 'animate-spin' : ''}`} />
            Auto-Rotate
          </button>

          <button
            onClick={() => setShowCage(!showCage)}
            className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-all ${
              showCage
                ? 'border-cyan-500/50 bg-cyan-950/50 text-cyan-200'
                : 'border-zinc-800 bg-zinc-900/80 text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Layers className="h-3.5 w-3.5" />
            Grid Cage
          </button>

          <button
            onClick={handleResetView}
            className="flex items-center gap-1.5 rounded-lg border border-zinc-800 bg-zinc-900/80 px-3 py-1.5 text-xs font-medium text-zinc-300 hover:bg-zinc-800 hover:text-zinc-100 transition-all"
          >
            <Maximize2 className="h-3.5 w-3.5" />
            Reset View
          </button>
        </div>
      </div>

      {/* 2. LEFT SIDEBAR: DEPTH LAYERS & REAL TIME VALUES */}
      <div className="absolute top-20 left-4 z-10 flex flex-col gap-2 pointer-events-none max-w-[260px]">
        {/* Layer 1: Surface Mixed Layer */}
        <div className="rounded-lg border-l-2 border-orange-500 bg-[#090d1a]/85 p-2.5 backdrop-blur-md shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold tracking-wider text-orange-400 uppercase">
              Surface Mixed Layer
            </span>
            <span className="font-mono text-xs font-bold text-orange-300">{temp0m}°C</span>
          </div>
          <span className="text-[9px] text-zinc-400">0 - {mld ?? 45}m (Direct SST Coupling)</span>
        </div>

        {/* Layer 2: Thermocline Zone */}
        <div className="rounded-lg border-l-2 border-amber-400 bg-[#090d1a]/85 p-2.5 backdrop-blur-md shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold tracking-wider text-amber-300 uppercase">
              Thermocline Zone
            </span>
            <span className="font-mono text-xs font-bold text-amber-200">{temp500m}°C</span>
          </div>
          <span className="text-[9px] text-zinc-400">
            {mld ?? 45} - {thermoclineDepth ?? 160}m (SLA Isotherm Heave & Eddies)
          </span>
        </div>

        {/* Layer 3: Deep Ocean Water */}
        <div className="rounded-lg border-l-2 border-cyan-400 bg-[#090d1a]/85 p-2.5 backdrop-blur-md shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold tracking-wider text-cyan-300 uppercase">
              Deep Ocean Water
            </span>
            <span className="font-mono text-xs font-bold text-cyan-200">{temp1000m}°C</span>
          </div>
          <span className="text-[9px] text-zinc-400">700 - 1000m (Basin Baroclinic Modes)</span>
        </div>

        {/* Layer 4: Abyssal Water */}
        <div className="rounded-lg border-l-2 border-indigo-500 bg-[#090d1a]/85 p-2.5 backdrop-blur-md shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold tracking-wider text-indigo-300 uppercase">
              Abyssal Water
            </span>
            <span className="font-mono text-xs font-bold text-indigo-200">{temp1500m}°C</span>
          </div>
          <span className="text-[9px] text-zinc-400">&gt; 1500m (Dense Cold Bottom Water)</span>
        </div>
      </div>

      {/* 3. RIGHT SIDEBAR: VERTICAL THERMAL COLORBAR SCALE */}
      <div className="absolute top-20 right-4 z-10 flex items-center gap-2 rounded-lg border border-zinc-800/80 bg-[#090d1a]/85 p-3 backdrop-blur-md shadow-lg pointer-events-none">
        <div className="flex flex-col justify-between items-center h-48 py-1">
          <span className="font-mono text-[10px] text-orange-400 font-bold">{temp0m}°C</span>
          <span className="font-mono text-[9px] text-amber-300">18°C</span>
          <span className="font-mono text-[9px] text-emerald-300">14°C</span>
          <span className="font-mono text-[9px] text-cyan-300">{temp500m}°C</span>
          <span className="font-mono text-[9px] text-blue-400">{temp1000m}°C</span>
          <span className="font-mono text-[10px] text-indigo-400 font-bold">{temp1500m}°C</span>
        </div>
        <div className="h-48 w-3 rounded-full bg-gradient-to-b from-[#f97316] via-[#eab308] via-[#22c55e] via-[#06b6d4] to-[#1e3a8a] shadow-inner border border-zinc-700/50" />
      </div>

      {/* 4. BOTTOM FOOTER HUD */}
      <div className="absolute bottom-3 left-4 right-4 z-10 flex items-center justify-between text-xs text-zinc-400 pointer-events-none">
        <div className="flex items-center gap-3">
          <span className="rounded bg-zinc-900/90 border border-zinc-800 px-2 py-1 font-mono text-[10px] text-zinc-300 backdrop-blur-sm">
            Left Click: Orbit • Scroll: Zoom • Right Click: Pan
          </span>
          <span className="text-[10px] text-zinc-500 hidden sm:inline">
            TEOS-10 Subsurface Thermal Stratification
          </span>
        </div>

        <div className="flex items-center gap-2 bg-[#090d1a]/80 px-2.5 py-1 rounded border border-zinc-800/80 backdrop-blur-sm">
          <Waves className="h-3 w-3 text-cyan-400" />
          <span className="text-[10px] font-mono text-cyan-300">
            Argo Float Scale ~2m • Sounding Depth 1500m
          </span>
        </div>
      </div>

      {/* Three.js Canvas Container */}
      <div ref={mountRef} className="w-full h-full flex-1 cursor-grab active:cursor-grabbing" />
    </div>
  );
};

export default ThreeDOceanModel;
