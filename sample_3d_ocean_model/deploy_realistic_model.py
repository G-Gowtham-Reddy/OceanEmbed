import os

html_code = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>OceanEmbed - 3D Subsurface Temperature Reconstruction</title>
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
    }
    body {
      background-color: #030712;
      color: #e2e8f0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      overflow: hidden;
      width: 100vw;
      height: 100vh;
    }
    #canvas-container {
      width: 100%;
      height: 100%;
      position: absolute;
      top: 0;
      left: 0;
      z-index: 1;
    }

    /* Ambient Background Grid */
    .bg-grid {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-image: 
        radial-gradient(circle at 50% 38%, rgba(14, 165, 233, 0.16) 0%, rgba(3, 7, 18, 0.98) 75%),
        linear-gradient(to right, rgba(30, 58, 95, 0.14) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(30, 58, 95, 0.14) 1px, transparent 1px);
      background-size: 100% 100%, 44px 44px, 44px 44px;
      pointer-events: none;
      z-index: 2;
    }

    /* HUD Overlay UI */
    .hud-layer {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 10;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 24px 32px;
    }

    /* Top Header */
    .header-bar {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }
    .brand-title {
      font-size: 10px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: #38bdf8;
      font-weight: 700;
      margin-bottom: 2px;
      text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
    }
    .main-heading {
      font-size: 19px;
      font-weight: 800;
      color: #ffffff;
      letter-spacing: 0.5px;
      display: flex;
      align-items: center;
      gap: 12px;
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.8);
    }
    .badge {
      font-size: 10px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      background: rgba(14, 165, 233, 0.15);
      border: 1px solid rgba(56, 189, 248, 0.4);
      color: #38bdf8;
      letter-spacing: 1px;
    }

    /* Control Buttons */
    .controls-panel {
      display: flex;
      gap: 10px;
      pointer-events: auto;
    }
    .ctrl-btn {
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid rgba(51, 65, 85, 0.8);
      color: #cbd5e1;
      padding: 8px 14px;
      font-size: 11px;
      font-weight: 600;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s ease;
      backdrop-filter: blur(8px);
      letter-spacing: 0.5px;
    }
    .ctrl-btn:hover {
      background: rgba(30, 41, 59, 0.95);
      border-color: #38bdf8;
      color: #ffffff;
      box-shadow: 0 0 12px rgba(56, 189, 248, 0.3);
    }
    .ctrl-btn.active {
      background: rgba(14, 165, 233, 0.25);
      border-color: #38bdf8;
      color: #38bdf8;
      box-shadow: 0 0 14px rgba(56, 189, 248, 0.4);
    }

    /* Left Side: Strata Brackets */
    .strata-callouts {
      position: absolute;
      top: 130px;
      left: 32px;
      display: flex;
      flex-direction: column;
      gap: 30px;
      pointer-events: none;
    }
    .strata-item {
      display: flex;
      flex-direction: column;
      gap: 2px;
      border-left: 2px solid #64748b;
      padding-left: 12px;
      position: relative;
    }
    .strata-name {
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 1px;
      text-transform: uppercase;
      text-shadow: 0 1px 4px rgba(0,0,0,0.8);
    }
    .strata-range {
      font-size: 9px;
      color: #94a3b8;
      font-family: monospace;
      letter-spacing: 0.5px;
    }

    /* Right Side: Temperature Colorbar */
    .colorbar-panel {
      position: absolute;
      top: 120px;
      right: 32px;
      display: flex;
      align-items: center;
      gap: 12px;
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid rgba(51, 65, 85, 0.6);
      padding: 14px 16px;
      border-radius: 8px;
      backdrop-filter: blur(10px);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    }
    .colorbar-gradient {
      width: 14px;
      height: 280px;
      border-radius: 7px;
      background: linear-gradient(to bottom, 
        #ea580c 0%, 
        #f59e0b 18%, 
        #fbbf24 32%, 
        #10b981 48%, 
        #06b6d4 64%, 
        #1d4ed8 82%, 
        #020617 100%);
      box-shadow: 0 0 16px rgba(245, 158, 11, 0.35);
    }
    .colorbar-ticks {
      height: 280px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      font-size: 11px;
      font-family: monospace;
      font-weight: 700;
      color: #cbd5e1;
    }
    .colorbar-ticks span {
      position: relative;
    }
    .colorbar-ticks span::before {
      content: "—";
      position: absolute;
      left: -14px;
      color: #64748b;
    }

    /* Bottom Footer Bar */
    .footer-bar {
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }
    .footer-title-block {
      display: flex;
      flex-direction: column;
      gap: 3px;
    }
    .footer-subtitle {
      font-size: 10px;
      color: #38bdf8;
      letter-spacing: 2px;
      text-transform: uppercase;
      font-weight: 700;
    }
    .footer-title {
      font-size: 17px;
      font-weight: 800;
      color: #ffffff;
      letter-spacing: 1.2px;
      text-shadow: 0 2px 8px rgba(0,0,0,0.8);
    }
    .horizontal-legend {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-top: 6px;
      font-size: 10px;
      color: #94a3b8;
      font-family: monospace;
      font-weight: 600;
    }
    .legend-bar-mini {
      width: 90px;
      height: 6px;
      border-radius: 3px;
      background: linear-gradient(to right, #ea580c, #fbbf24, #10b981, #06b6d4, #020617);
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
    }

    /* Scale & Compass */
    .scale-compass-block {
      display: flex;
      align-items: flex-end;
      gap: 24px;
    }
    .scale-widget {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 3px;
    }
    .scale-label {
      font-size: 8px;
      color: #64748b;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      font-weight: 600;
    }
    .scale-bar {
      width: 100px;
      height: 3px;
      background: #475569;
      position: relative;
    }
    .scale-bar::before, .scale-bar::after {
      content: "";
      position: absolute;
      top: -3px;
      width: 2px;
      height: 8px;
      background: #475569;
    }
    .scale-bar::before { left: 0; }
    .scale-bar::after { right: 0; }
    .scale-ticks {
      width: 100px;
      display: flex;
      justify-content: space-between;
      font-size: 8px;
      color: #64748b;
      font-family: monospace;
    }
    .compass-rose {
      display: flex;
      flex-direction: column;
      align-items: center;
      font-family: monospace;
      font-size: 10px;
      font-weight: 800;
      color: #38bdf8;
      gap: 2px;
    }
    .compass-needle {
      width: 2px;
      height: 18px;
      background: linear-gradient(to bottom, #38bdf8 50%, #475569 50%);
      box-shadow: 0 0 8px rgba(56, 189, 248, 0.5);
    }

    /* Floating Tooltip Hint */
    .interaction-hint {
      position: absolute;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      font-size: 11px;
      color: #94a3b8;
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(51, 65, 85, 0.8);
      padding: 5px 16px;
      border-radius: 20px;
      pointer-events: none;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.6);
      letter-spacing: 0.5px;
    }
  </style>

  <!-- Three.js + OrbitControls -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>

  <div class="bg-grid"></div>
  <div id="canvas-container"></div>

  <div class="hud-layer">
    <div class="header-bar">
      <div>
        <div class="brand-title">OceanEmbed Architecture</div>
        <div class="main-heading">
          3D Subsurface Temperature Reconstruction
          <span class="badge">PHOTOREALISTIC 3D</span>
        </div>
      </div>

      <div class="controls-panel">
        <button id="btn-rotate" class="ctrl-btn active">Auto-Rotate</button>
        <button id="btn-wireframe" class="ctrl-btn">Grid Cage</button>
        <button id="btn-reset" class="ctrl-btn">Reset View</button>
      </div>
    </div>

    <div class="strata-callouts">
      <div class="strata-item" style="border-left-color: #f97316;">
        <span class="strata-name" style="color: #fb923c;">Surface Mixed Layer</span>
        <span class="strata-range">0 – 150m (Direct SST Coupling)</span>
      </div>
      <div class="strata-item" style="border-left-color: #eab308;">
        <span class="strata-name" style="color: #facc15;">Thermocline Zone</span>
        <span class="strata-range">150 – 700m (SLA Isotherm Heave & Eddies)</span>
      </div>
      <div class="strata-item" style="border-left-color: #06b6d4;">
        <span class="strata-name" style="color: #38bdf8;">Deep Ocean Water</span>
        <span class="strata-range">700 – 1500m (Basin Baroclinic Modes)</span>
      </div>
      <div class="strata-item" style="border-left-color: #6366f1;">
        <span class="strata-name" style="color: #818cf8;">Abyssal Water</span>
        <span class="strata-range">&gt; 1500m (Dense Cold Bottom Water)</span>
      </div>
    </div>

    <div class="colorbar-panel">
      <div class="colorbar-gradient"></div>
      <div class="colorbar-ticks">
        <span>24°C</span>
        <span>18°C</span>
        <span>14°C</span>
        <span>8°C</span>
        <span>5°C</span>
        <span>3°C</span>
      </div>
    </div>

    <div class="footer-bar">
      <div class="footer-title-block">
        <div class="footer-subtitle">Subsurface Thermal Inversion & Turbulence Model</div>
        <div class="footer-title">SUB-SURFACE TEMPERATURE RECONSTRUCTION</div>
        <div class="horizontal-legend">
          <span>24°C Warm</span>
          <div class="legend-bar-mini"></div>
          <span>2°C Cold</span>
        </div>
      </div>

      <div class="scale-compass-block">
        <div class="scale-widget">
          <span class="scale-label">Scale (km)</span>
          <div class="scale-bar"></div>
          <div class="scale-ticks">
            <span>0</span>
            <span>500</span>
            <span>2000</span>
          </div>
        </div>
        <div class="compass-rose">
          <span>N</span>
          <div class="compass-needle"></div>
        </div>
      </div>
    </div>
  </div>

  <div class="interaction-hint">
    Left Click + Drag to Orbit • Scroll to Zoom • Right Click to Pan
  </div>

  <script>
    // =========================================================================
    // 1. HIGH-CONTRAST THERMOCLINE TEXTURE GENERATOR
    // =========================================================================
    function createThermoclineCanvasTexture() {
      const canvas = document.createElement('canvas');
      canvas.width = 1024;
      canvas.height = 1024;
      const ctx = canvas.getContext('2d');

      const grad = ctx.createLinearGradient(0, 0, 0, 1024);
      grad.addColorStop(0.00, '#ea580c'); // 24C surface warm orange
      grad.addColorStop(0.12, '#f97316'); // 22C
      grad.addColorStop(0.22, '#f59e0b'); // 20C
      grad.addColorStop(0.34, '#fbbf24'); // 18C Gold core
      grad.addColorStop(0.46, '#10b981'); // 14C Emerald transition
      grad.addColorStop(0.58, '#0284c7'); // 10C Marine blue
      grad.addColorStop(0.72, '#1e3a8a'); // 6C Deep Navy
      grad.addColorStop(0.86, '#0f172a'); // 4C Lower Deep
      grad.addColorStop(1.00, '#020617'); // 2C Abyssal midnight black
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 1024, 1024);

      ctx.save();
      const numLines = 54;
      for (let i = 0; i < numLines; i++) {
        const normY = i / numLines;
        const y = normY * 1024;
        const env = Math.sin(normY * Math.PI);

        ctx.beginPath();
        for (let x = 0; x <= 1024; x += 12) {
          const swell = Math.sin(x * 0.005 + i * 0.22) * (env * 60);
          const vortex = Math.sin(x * 0.012 - i * 0.3) * (env * 28);
          const eddy = Math.cos(x * 0.024 + i * 0.15) * (env * 14);
          const curY = y + swell + vortex + eddy;
          if (x === 0) ctx.moveTo(x, curY); else ctx.lineTo(x, curY);
        }

        if (normY < 0.22) {
          ctx.strokeStyle = `rgba(255, 237, 213, ${0.45 + env * 0.4})`;
          ctx.lineWidth = 2.0;
        } else if (normY < 0.48) {
          ctx.strokeStyle = `rgba(254, 240, 138, ${0.6 + env * 0.4})`;
          ctx.lineWidth = 2.4;
        } else if (normY < 0.65) {
          ctx.strokeStyle = `rgba(167, 243, 208, ${0.45 + env * 0.35})`;
          ctx.lineWidth = 2.0;
        } else if (normY < 0.82) {
          ctx.strokeStyle = `rgba(125, 211, 252, ${0.35 + env * 0.3})`;
          ctx.lineWidth = 1.8;
        } else {
          ctx.strokeStyle = `rgba(96, 165, 250, 0.2)`;
          ctx.lineWidth = 1.4;
        }
        ctx.stroke();
      }
      ctx.restore();

      const tex = new THREE.CanvasTexture(canvas);
      tex.wrapS = THREE.ClampToEdgeWrapping;
      tex.wrapT = THREE.ClampToEdgeWrapping;
      return tex;
    }

    function createWaterSurfaceCanvasTexture() {
      const canvas = document.createElement('canvas');
      canvas.width = 512;
      canvas.height = 512;
      const ctx = canvas.getContext('2d');

      const grad = ctx.createRadialGradient(256, 256, 20, 256, 256, 256);
      grad.addColorStop(0, '#38bdf8');
      grad.addColorStop(0.6, '#0284c7');
      grad.addColorStop(1, '#075985');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 512, 512);

      ctx.save();
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.45)';
      ctx.lineWidth = 2.0;
      for (let i = 0; i < 20; i++) {
        ctx.beginPath();
        for (let x = 0; x <= 512; x += 16) {
          const y = (i * 26) + Math.sin(x * 0.04 + i) * 12;
          if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.stroke();
      }
      ctx.restore();

      const tex = new THREE.CanvasTexture(canvas);
      tex.wrapS = THREE.RepeatWrapping;
      tex.wrapT = THREE.RepeatWrapping;
      tex.repeat.set(2, 2);
      return tex;
    }

    // =========================================================================
    // 2. SCENE SETUP & CINEMATIC RENDERER
    // =========================================================================
    const container = document.getElementById('canvas-container');
    const scene = new THREE.Scene();

    const camera = new THREE.PerspectiveCamera(36, window.innerWidth / window.innerHeight, 0.1, 150);
    camera.position.set(20, 15, 20);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2 - 0.04;
    controls.minDistance = 12;
    controls.maxDistance = 50;
    controls.target.set(0, -0.4, 0);

    // Studio Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    scene.add(ambientLight);

    const sunLight = new THREE.DirectionalLight(0xffffff, 1.4);
    sunLight.position.set(16, 26, 16);
    scene.add(sunLight);

    const rimLight = new THREE.DirectionalLight(0x38bdf8, 1.0);
    rimLight.position.set(-18, 14, -18);
    scene.add(rimLight);

    // =========================================================================
    // 3. 3D OCEAN BLOCK (ISOMETRIC CUTAWAY)
    // =========================================================================
    const oceanGroup = new THREE.Group();
    scene.add(oceanGroup);

    const BLOCK_W = 12.0;
    const BLOCK_H = 12.0;
    const BLOCK_D = 12.0;

    const thermoclineTex = createThermoclineCanvasTexture();
    const waterTex = createWaterSurfaceCanvasTexture();

    const cutawayMat = new THREE.MeshStandardMaterial({
      map: thermoclineTex,
      roughness: 0.35,
      metalness: 0.05
    });

    const deepSideMat = new THREE.MeshStandardMaterial({
      color: 0x020617,
      roughness: 0.5,
      metalness: 0.1
    });

    const topWaterMat = new THREE.MeshStandardMaterial({
      map: waterTex,
      color: 0x38bdf8,
      roughness: 0.1,
      metalness: 0.1,
      transparent: true,
      opacity: 0.92
    });

    const cubeMaterials = [
      cutawayMat,   // +X (Right cutaway face)
      deepSideMat,  // -X
      topWaterMat,  // +Y (Top Water surface)
      deepSideMat,  // -Y
      cutawayMat,   // +Z (Front cutaway face)
      deepSideMat   // -Z
    ];

    const oceanCubeGeom = new THREE.BoxGeometry(BLOCK_W, BLOCK_H, BLOCK_D);
    const oceanCube = new THREE.Mesh(oceanCubeGeom, cubeMaterials);
    oceanGroup.add(oceanCube);

    // Top surface animated wave ripples
    const waveSurfaceGeom = new THREE.PlaneGeometry(BLOCK_W, BLOCK_D, 40, 40);
    waveSurfaceGeom.rotateX(-Math.PI / 2);
    const wavePos = waveSurfaceGeom.attributes.position;
    const waveOrigY = new Float32Array(wavePos.count);
    for (let i = 0; i < wavePos.count; i++) {
      waveOrigY[i] = wavePos.getY(i);
    }
    const waveMesh = new THREE.Mesh(waveSurfaceGeom, new THREE.MeshPhongMaterial({
      color: 0x38bdf8,
      specular: 0xffffff,
      shininess: 120,
      transparent: true,
      opacity: 0.45,
      side: THREE.DoubleSide
    }));
    waveMesh.position.set(0, BLOCK_H / 2 + 0.02, 0);
    oceanGroup.add(waveMesh);

    // Surface grid helper
    const surfaceGrid = new THREE.GridHelper(BLOCK_W, 16, 0x38bdf8, 0x0284c7);
    surfaceGrid.position.set(0, BLOCK_H / 2 + 0.04, 0);
    surfaceGrid.material.opacity = 0.25;
    surfaceGrid.material.transparent = true;
    oceanGroup.add(surfaceGrid);

    // Wireframe Cage
    const cageEdges = new THREE.EdgesGeometry(oceanCubeGeom);
    const cageMat = new THREE.LineBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.35 });
    const cageLine = new THREE.LineSegments(cageEdges, cageMat);
    oceanGroup.add(cageLine);

    // =========================================================================
    // 4. 3D ARGO PROFILING FLOAT & NEON DEPTH RINGS (POSITIONED FOR MAXIMUM VISIBILITY)
    // =========================================================================
    const argoGroup = new THREE.Group();
    const ARGO_X = 6.05;
    const ARGO_Z = 6.05;
    argoGroup.renderOrder = 10;
    oceanGroup.add(argoGroup);

    // Bright Argo Hull (Yellow)
    const hullMesh = new THREE.Mesh(
      new THREE.CylinderGeometry(0.34, 0.34, 4.2, 32),
      new THREE.MeshStandardMaterial({
        color: 0xfacc15,
        roughness: 0.2,
        metalness: 0.4,
        emissive: 0xca8a04,
        emissiveIntensity: 0.55
      })
    );
    hullMesh.position.set(ARGO_X, 1.4, ARGO_Z);
    argoGroup.add(hullMesh);

    // CTD Sensor Head & Antenna Needle
    const ctdMesh = new THREE.Mesh(
      new THREE.CylinderGeometry(0.24, 0.34, 0.55, 24),
      new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.8, roughness: 0.2 })
    );
    ctdMesh.position.set(ARGO_X, 3.75, ARGO_Z);
    argoGroup.add(ctdMesh);

    const antMesh = new THREE.Mesh(
      new THREE.CylinderGeometry(0.025, 0.025, 1.8, 12),
      new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0.9, roughness: 0.1 })
    );
    antMesh.position.set(ARGO_X, 4.9, ARGO_Z);
    argoGroup.add(antMesh);

    // Base collar
    const collarMesh = new THREE.Mesh(
      new THREE.CylinderGeometry(0.36, 0.28, 0.5, 24),
      new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.8, roughness: 0.2 })
    );
    collarMesh.position.set(ARGO_X, -0.7, ARGO_Z);
    argoGroup.add(collarMesh);

    // Vertical holographic cable
    const cableMesh = new THREE.Mesh(
      new THREE.CylinderGeometry(0.02, 0.02, BLOCK_H - 0.8, 12),
      new THREE.MeshBasicMaterial({ color: 0x67e8f9, transparent: true, opacity: 0.85 })
    );
    cableMesh.position.set(ARGO_X, -0.6, ARGO_Z);
    argoGroup.add(cableMesh);

    // Helper for 3D Text Sprites
    function makeTextSprite(message, colorStr) {
      const canvas = document.createElement('canvas');
      canvas.width = 512;
      canvas.height = 128;
      const ctx = canvas.getContext('2d');
      ctx.font = 'Bold 46px monospace';
      ctx.fillStyle = colorStr || '#ffffff';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(message, 256, 64);
      const tex = new THREE.CanvasTexture(canvas);
      const spriteMat = new THREE.SpriteMaterial({ map: tex, transparent: true, depthWrite: false });
      const sprite = new THREE.Sprite(spriteMat);
      sprite.scale.set(2.8, 0.7, 1.0);
      return sprite;
    }

    // 4 Brilliant Neon Glowing Depth Rings: 0m, 500m, 1000m, 1500m
    const depthLevels = [
      { depth: '0m', y: 3.8, radius: 2.2, color: 0xffffff },
      { depth: '500m', y: 1.3, radius: 2.5, color: 0x67e8f9 },
      { depth: '1000m', y: -1.3, radius: 2.8, color: 0x38bdf8 },
      { depth: '1500m', y: -3.8, radius: 3.1, color: 0x0284c7 }
    ];

    const depthRings = [];

    depthLevels.forEach(lvl => {
      const ringGeom = new THREE.TorusGeometry(lvl.radius, 0.07, 16, 64);
      ringGeom.rotateX(Math.PI / 2);
      const ringMat = new THREE.MeshBasicMaterial({
        color: lvl.color,
        transparent: true,
        opacity: 0.98
      });
      const ringMesh = new THREE.Mesh(ringGeom, ringMat);
      ringMesh.position.set(ARGO_X, lvl.y, ARGO_Z);
      argoGroup.add(ringMesh);

      // Inner soft glow disc
      const glowDisc = new THREE.Mesh(
        new THREE.CircleGeometry(lvl.radius, 32),
        new THREE.MeshBasicMaterial({ color: lvl.color, transparent: true, opacity: 0.08, side: THREE.DoubleSide, depthWrite: false })
      );
      glowDisc.rotateX(-Math.PI / 2);
      glowDisc.position.set(ARGO_X, lvl.y, ARGO_Z);
      argoGroup.add(glowDisc);

      // Depth Label
      const label = makeTextSprite(lvl.depth, '#ffffff');
      label.scale.set(1.4, 0.7, 1.0);
      label.position.set(ARGO_X, lvl.y + 0.35, ARGO_Z + lvl.radius + 0.2);
      argoGroup.add(label);

      depthRings.push({ mesh: ringMesh, phase: lvl.y });
    });

    // Argo Callout Label
    const floatLabel = makeTextSprite('ARGO FLOAT (PROFILING)', '#facc15');
    floatLabel.scale.set(3.6, 0.9, 1.0);
    floatLabel.position.set(ARGO_X + 2.4, 1.6, ARGO_Z);
    argoGroup.add(floatLabel);

    const calloutLine = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(ARGO_X + 0.35, 1.6, ARGO_Z),
        new THREE.Vector3(ARGO_X + 1.2, 1.6, ARGO_Z)
      ]),
      new THREE.LineBasicMaterial({ color: 0xfacc15, transparent: true, opacity: 0.9 })
    );
    argoGroup.add(calloutLine);

    // =========================================================================
    // 5. CONTOURED BATHYMETRIC SEABED
    // =========================================================================
    const seabedGeom = new THREE.PlaneGeometry(BLOCK_W + 1.2, BLOCK_D + 1.2, 54, 54);
    seabedGeom.rotateX(-Math.PI / 2);
    const seabedPos = seabedGeom.attributes.position;
    for (let i = 0; i < seabedPos.count; i++) {
      const u = seabedPos.getX(i);
      const v = seabedPos.getZ(i);
      const ridge = Math.sin(u * 0.9) * Math.cos(v * 0.9) * 0.55;
      const micro = Math.sin(u * 2.5 + v * 2.2) * 0.2;
      seabedPos.setY(i, ridge + micro - 0.2);
    }
    seabedGeom.computeVertexNormals();

    const seabedMesh = new THREE.Mesh(
      seabedGeom,
      new THREE.MeshStandardMaterial({
        color: 0x0f172a,
        roughness: 0.85,
        metalness: 0.2,
        flatShading: true
      })
    );
    seabedMesh.position.set(0, -BLOCK_H / 2 - 0.25, 0);
    oceanGroup.add(seabedMesh);

    const seabedLabel = makeTextSprite('BATHYMETRIC SEABED', '#94a3b8');
    seabedLabel.scale.set(3.2, 0.8, 1.0);
    seabedLabel.position.set(3.2, -BLOCK_H / 2 - 0.8, 4.0);
    oceanGroup.add(seabedLabel);

    // Overhead Radar Scan Cone
    const scanCone = new THREE.Mesh(
      new THREE.ConeGeometry(BLOCK_W * 0.7, 9.0, 4, 1, true),
      new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.08, wireframe: true })
    );
    scanCone.rotateX(Math.PI);
    scanCone.position.set(0, BLOCK_H / 2 + 4.5, 0);
    oceanGroup.add(scanCone);

    // =========================================================================
    // 6. ANIMATION LOOP
    // =========================================================================
    let isAutoRotating = true;
    let isWireframeVisible = true;
    const clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();

      if (isAutoRotating) {
        oceanGroup.rotation.y += 0.0035;
      }

      for (let i = 0; i < wavePos.count; i++) {
        const u = wavePos.getX(i);
        const w = wavePos.getZ(i);
        const wave = Math.sin(u * 0.8 + elapsed * 1.8) * 0.06 + Math.cos(w * 0.9 + elapsed * 1.5) * 0.05;
        wavePos.setY(i, waveOrigY[i] + wave);
      }
      waveSurfaceGeom.computeVertexNormals();
      waveSurfaceGeom.attributes.position.needsUpdate = true;

      depthRings.forEach(r => {
        const pulse = 1.0 + Math.sin(elapsed * 2.5 + r.phase) * 0.035;
        r.mesh.scale.set(pulse, 1, pulse);
      });

      scanCone.rotation.y = elapsed * 0.2;

      controls.update();
      renderer.render(scene, camera);
    }
    animate();

    const btnRotate = document.getElementById('btn-rotate');
    btnRotate.addEventListener('click', () => {
      isAutoRotating = !isAutoRotating;
      btnRotate.classList.toggle('active', isAutoRotating);
    });

    const btnWireframe = document.getElementById('btn-wireframe');
    btnWireframe.addEventListener('click', () => {
      isWireframeVisible = !isWireframeVisible;
      btnWireframe.classList.toggle('active', isWireframeVisible);
      cageLine.visible = isWireframeVisible;
      surfaceGrid.visible = isWireframeVisible;
    });

    const btnReset = document.getElementById('btn-reset');
    btnReset.addEventListener('click', () => {
      camera.position.set(20, 15, 20);
      controls.target.set(0, -0.4, 0);
      oceanGroup.rotation.y = 0;
    });

    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });
  </script>
</body>
</html>
"""

with open("sample_3d_ocean_model/index.html", "w", encoding="utf-8") as f:
    f.write(html_code)
print("Complete photorealistic index.html written successfully!")
