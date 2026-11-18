import base64
import numpy as np
from PIL import Image, ImageFilter
import math

# 1. Generate optimized 1024x1024 Thermocline Texture
def generate_thermocline():
    W, H = 1024, 1024
    stops = [
        (0.00, np.array([245, 102, 25])),   # Surface 24C Warm Orange
        (0.15, np.array([252, 150, 38])),   # 22C
        (0.28, np.array([255, 208, 72])),   # 18C Upper Thermocline Gold
        (0.40, np.array([246, 185, 52])),   # 15C
        (0.52, np.array([35, 188, 178])),   # 12C Cyan
        (0.66, np.array([12, 128, 202])),   # 8C
        (0.80, np.array([18, 52, 138])),    # 5C Deep Navy
        (1.00, np.array([5, 8, 28]))        # 2C Abyssal Midnight
    ]

    y_coords = np.linspace(0, 1, H)
    base_rgb = np.zeros((H, 3), dtype=np.float32)
    for i in range(len(stops) - 1):
        y0, c0 = stops[i]
        y1, c1 = stops[i+1]
        mask = (y_coords >= y0) & (y_coords <= y1)
        if not np.any(mask):
            continue
        t = (y_coords[mask] - y0) / (y1 - y0)
        t = t[:, np.newaxis]
        base_rgb[mask] = (1 - t) * c0 + t * c1

    x = np.linspace(0, 2.4 * np.pi, W)
    y = np.linspace(0, 1, H)
    X, Y = np.meshgrid(x, y)

    envelope = np.exp(-((Y - 0.38) ** 2) / (2 * 0.14 ** 2))
    swell1 = np.sin(X * 1.0 + 0.4) * 0.08
    swell2 = np.cos(X * 2.2 - 0.6) * 0.04
    swell3 = np.sin(X * 3.8 + Y * 2.0) * 0.02
    vortex1 = np.sin(X * 3.2 + np.cos(Y * 8.0) * 0.8) * 0.035
    total_displacement = (swell1 + swell2 + swell3 + vortex1) * envelope

    displaced_Y = np.clip(Y + total_displacement, 0.0, 1.0)
    displaced_indices = (displaced_Y * (H - 1)).astype(np.int32)
    texture_rgb = base_rgb[displaced_indices, :]

    # Isotherm glowing lines
    filament_phase = displaced_Y * 20.0
    filaments = (np.sin(filament_phase * 2 * np.pi) ** 6) * envelope * 0.4
    highlight_gold = np.array([255, 248, 210], dtype=np.float32)
    for c in range(3):
        texture_rgb[:, :, c] += (highlight_gold[c] - texture_rgb[:, :, c]) * filaments

    texture_rgb = np.clip(texture_rgb, 0, 255).astype(np.uint8)
    img = Image.fromarray(texture_rgb, mode="RGB")
    img = img.filter(ImageFilter.GaussianBlur(radius=1.2))
    img.save("sample_3d_ocean_model/cross_section_texture.png", quality=90)

    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode('ascii')

# 2. Generate Water Surface Texture
def generate_water_surface():
    W, H = 512, 512
    x = np.linspace(-1, 1, W)
    y = np.linspace(-1, 1, H)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)

    c_center = np.array([56, 189, 248], dtype=np.float32)
    c_edge = np.array([2, 132, 199], dtype=np.float32)
    t = np.clip(R / 1.2, 0, 1)[:, :, np.newaxis]
    rgb = (1 - t) * c_center + t * c_edge

    theta = np.linspace(0, 8 * np.pi, W)
    phi = np.linspace(0, 8 * np.pi, H)
    TH, PH = np.meshgrid(theta, phi)
    ripples = np.sin(TH * 1.0 + PH * 0.8) * 0.15 + np.cos(TH * 1.5 - PH * 1.2) * 0.12
    glints = np.clip(ripples, 0, 1) ** 3
    glint_color = np.array([240, 253, 255], dtype=np.float32)
    rgb += (glint_color - rgb) * (glints[:, :, np.newaxis] * 0.45)
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)

    img = Image.fromarray(rgb, mode="RGB")
    img = img.filter(ImageFilter.GaussianBlur(radius=1.0))
    img.save("sample_3d_ocean_model/water_surface.png", quality=90)

    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode('ascii')

print("Encoding textures to Base64...")
b64_thermocline = generate_thermocline()
b64_water = generate_water_surface()
print(f"Thermocline b64 length: {len(b64_thermocline)}")
print(f"Water b64 length: {len(b64_water)}")

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>OceanEmbed - 3D Subsurface Temperature Reconstruction</title>
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
    }}
    body {{
      background-color: #030712;
      color: #e2e8f0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      overflow: hidden;
      width: 100vw;
      height: 100vh;
    }}
    #canvas-container {{
      width: 100%;
      height: 100%;
      position: absolute;
      top: 0;
      left: 0;
      z-index: 1;
    }}
    .bg-grid {{
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
    }}
    .hud-layer {{
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
    }}
    .header-bar {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }}
    .brand-title {{
      font-size: 10px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: #38bdf8;
      font-weight: 700;
      margin-bottom: 2px;
      text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
    }}
    .main-heading {{
      font-size: 19px;
      font-weight: 800;
      color: #ffffff;
      letter-spacing: 0.5px;
      display: flex;
      align-items: center;
      gap: 12px;
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.8);
    }}
    .badge {{
      font-size: 10px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      background: rgba(14, 165, 233, 0.15);
      border: 1px solid rgba(56, 189, 248, 0.4);
      color: #38bdf8;
      letter-spacing: 1px;
    }}
    .controls-panel {{
      display: flex;
      gap: 10px;
      pointer-events: auto;
    }}
    .ctrl-btn {{
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
    }}
    .ctrl-btn:hover {{
      background: rgba(30, 41, 59, 0.95);
      border-color: #38bdf8;
      color: #ffffff;
      box-shadow: 0 0 12px rgba(56, 189, 248, 0.3);
    }}
    .ctrl-btn.active {{
      background: rgba(14, 165, 233, 0.25);
      border-color: #38bdf8;
      color: #38bdf8;
      box-shadow: 0 0 14px rgba(56, 189, 248, 0.4);
    }}
    .strata-callouts {{
      position: absolute;
      top: 130px;
      left: 32px;
      display: flex;
      flex-direction: column;
      gap: 30px;
      pointer-events: none;
    }}
    .strata-item {{
      display: flex;
      flex-direction: column;
      gap: 2px;
      border-left: 2px solid #64748b;
      padding-left: 12px;
      position: relative;
    }}
    .strata-name {{
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 1px;
      text-transform: uppercase;
      text-shadow: 0 1px 4px rgba(0,0,0,0.8);
    }}
    .strata-range {{
      font-size: 9px;
      color: #94a3b8;
      font-family: monospace;
      letter-spacing: 0.5px;
    }}
    .colorbar-panel {{
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
    }}
    .colorbar-gradient {{
      width: 14px;
      height: 280px;
      border-radius: 7px;
      background: linear-gradient(to bottom, 
        #ea580c 0%, 
        #f59e0b 18%, 
        #fbbf24 32%, 
        #34d399 48%, 
        #06b6d4 64%, 
        #2563eb 82%, 
        #1e1b4b 100%);
      box-shadow: 0 0 16px rgba(245, 158, 11, 0.35);
    }}
    .colorbar-ticks {{
      height: 280px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      font-size: 11px;
      font-family: monospace;
      font-weight: 700;
      color: #cbd5e1;
    }}
    .colorbar-ticks span {{
      position: relative;
    }}
    .colorbar-ticks span::before {{
      content: "—";
      position: absolute;
      left: -14px;
      color: #64748b;
    }}
    .footer-bar {{
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }}
    .footer-title-block {{
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}
    .footer-subtitle {{
      font-size: 10px;
      color: #38bdf8;
      letter-spacing: 2px;
      text-transform: uppercase;
      font-weight: 700;
    }}
    .footer-title {{
      font-size: 17px;
      font-weight: 800;
      color: #ffffff;
      letter-spacing: 1.2px;
      text-shadow: 0 2px 8px rgba(0,0,0,0.8);
    }}
    .horizontal-legend {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-top: 6px;
      font-size: 10px;
      color: #94a3b8;
      font-family: monospace;
      font-weight: 600;
    }}
    .legend-bar-mini {{
      width: 90px;
      height: 6px;
      border-radius: 3px;
      background: linear-gradient(to right, #ea580c, #fbbf24, #34d399, #06b6d4, #1e1b4b);
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
    }}
    .scale-compass-block {{
      display: flex;
      align-items: flex-end;
      gap: 24px;
    }}
    .scale-widget {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 3px;
    }}
    .scale-label {{
      font-size: 8px;
      color: #64748b;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      font-weight: 600;
    }}
    .scale-bar {{
      width: 100px;
      height: 3px;
      background: #475569;
      position: relative;
    }}
    .scale-bar::before, .scale-bar::after {{
      content: "";
      position: absolute;
      top: -3px;
      width: 2px;
      height: 8px;
      background: #475569;
    }}
    .scale-bar::before {{ left: 0; }}
    .scale-bar::after {{ right: 0; }}
    .scale-ticks {{
      width: 100px;
      display: flex;
      justify-content: space-between;
      font-size: 8px;
      color: #64748b;
      font-family: monospace;
    }}
    .compass-rose {{
      display: flex;
      flex-direction: column;
      align-items: center;
      font-family: monospace;
      font-size: 10px;
      font-weight: 800;
      color: #38bdf8;
      gap: 2px;
    }}
    .compass-needle {{
      width: 2px;
      height: 18px;
      background: linear-gradient(to bottom, #38bdf8 50%, #475569 50%);
      box-shadow: 0 0 8px rgba(56, 189, 248, 0.5);
    }}
    .interaction-hint {{
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
    }}
  </style>

  <!-- Three.js + OrbitControls + Post-processing Bloom Suite -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/EffectComposer.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/RenderPass.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/ShaderPass.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/shaders/CopyShader.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/shaders/LuminosityHighPassShader.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/UnrealBloomPass.js"></script>
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
          <span class="badge">PHOTOREALISTIC V2</span>
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
    const B64_THERMOCLINE = "data:image/png;base64,{b64_thermocline}";
    const B64_WATER = "data:image/png;base64,{b64_water}";

    const container = document.getElementById('canvas-container');
    const scene = new THREE.Scene();

    const camera = new THREE.PerspectiveCamera(36, window.innerWidth / window.innerHeight, 0.1, 150);
    // Standard isometric camera angle
    camera.position.set(22, 16, 22);

    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true, powerPreference: "high-performance" }});
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    renderer.shadowMap.enabled = true;
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2 - 0.04;
    controls.minDistance = 12;
    controls.maxDistance = 50;
    controls.target.set(0, 0, 0);

    // UnrealBloomPass
    let composer = null;
    try {{
      const renderScene = new THREE.RenderPass(scene, camera);
      const bloomPass = new THREE.UnrealBloomPass(
        new THREE.Vector2(window.innerWidth, window.innerHeight),
        0.95, // strength
        0.4,  // radius
        0.65  // threshold
      );
      composer = new THREE.EffectComposer(renderer);
      composer.addPass(renderScene);
      composer.addPass(bloomPass);
    }} catch (e) {{
      console.warn("Bloom pass init:", e);
    }}

    // Cinematic Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 1.4);
    scene.add(ambientLight);

    const sunLight = new THREE.DirectionalLight(0xffffff, 2.4);
    sunLight.position.set(20, 30, 20);
    scene.add(sunLight);

    const cyanRimLight = new THREE.DirectionalLight(0x38bdf8, 2.0);
    cyanRimLight.position.set(-20, 15, -20);
    scene.add(cyanRimLight);

    // Load textures synchronously from inline base64
    const textureLoader = new THREE.TextureLoader();
    const crossSectionTex = textureLoader.load(B64_THERMOCLINE);
    crossSectionTex.generateMipmaps = true;

    const waterSurfaceTex = textureLoader.load(B64_WATER);
    waterSurfaceTex.wrapS = THREE.RepeatWrapping;
    waterSurfaceTex.wrapT = THREE.RepeatWrapping;
    waterSurfaceTex.repeat.set(2, 2);

    const oceanGroup = new THREE.Group();
    scene.add(oceanGroup);

    const BLOCK_W = 12.0;
    const BLOCK_H = 12.0;
    const BLOCK_D = 12.0;

    // Cutaway Cube
    // Front (+Z) and Right (+X) are vivid Thermocline Strata
    const cutawayMat = new THREE.MeshStandardMaterial({{
      map: crossSectionTex,
      roughness: 0.15,
      metalness: 0.05
    }});

    const deepSideMat = new THREE.MeshStandardMaterial({{
      color: 0x06182c,
      roughness: 0.35,
      metalness: 0.2
    }});

    const topWaterMat = new THREE.MeshStandardMaterial({{
      map: waterSurfaceTex,
      color: 0x38bdf8,
      roughness: 0.05,
      metalness: 0.1,
      transparent: true,
      opacity: 0.88
    }});

    // Three.js Box Materials: [+X, -X, +Y, -Y, +Z, -Z]
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

    // Top Surface Wave Ripple mesh
    const waveSurfaceGeom = new THREE.PlaneGeometry(BLOCK_W, BLOCK_D, 40, 40);
    waveSurfaceGeom.rotateX(-Math.PI / 2);
    const wavePos = waveSurfaceGeom.attributes.position;
    const waveOrigY = new Float32Array(wavePos.count);
    for (let i = 0; i < wavePos.count; i++) {{
      waveOrigY[i] = wavePos.getY(i);
    }}
    const waveMesh = new THREE.Mesh(waveSurfaceGeom, new THREE.MeshPhongMaterial({{
      color: 0x38bdf8,
      specular: 0xffffff,
      shininess: 120,
      transparent: true,
      opacity: 0.45,
      side: THREE.DoubleSide
    }}));
    waveMesh.position.set(0, BLOCK_H / 2 + 0.02, 0);
    oceanGroup.add(waveMesh);

    // Grid on top surface
    const surfaceGrid = new THREE.GridHelper(BLOCK_W, 16, 0x38bdf8, 0x0284c7);
    surfaceGrid.position.set(0, BLOCK_H / 2 + 0.04, 0);
    surfaceGrid.material.opacity = 0.28;
    surfaceGrid.material.transparent = true;
    oceanGroup.add(surfaceGrid);

    // Scientific Isometric Wireframe Cage
    const cageEdges = new THREE.EdgesGeometry(oceanCubeGeom);
    const cageMat = new THREE.LineBasicMaterial({{ color: 0x38bdf8, transparent: true, opacity: 0.4 }});
    const cageLine = new THREE.LineSegments(cageEdges, cageMat);
    oceanGroup.add(cageLine);

    // 3D ARGO FLOAT & NEON DEPTH RINGS (Positioned on the front corner edge so it stands out vividly!)
    const argoGroup = new THREE.Group();
    // Centered prominently at the cutaway corner
    argoGroup.position.set(2.2, 0, 2.2);
    oceanGroup.add(argoGroup);

    // Yellow Hull
    const hullMesh = new THREE.Mesh(
      new THREE.CylinderGeometry(0.28, 0.28, 3.8, 32),
      new THREE.MeshStandardMaterial({{
        color: 0xfacc15,
        roughness: 0.15,
        metalness: 0.35,
        emissive: 0xca8a04,
        emissiveIntensity: 0.35
      }})
    );
    hullMesh.position.y = 1.4;
    argoGroup.add(hullMesh);

    // Top CTD Sensor Head & Needle Antenna
    const ctdMesh = new THREE.Mesh(
      new THREE.CylinderGeometry(0.22, 0.28, 0.5, 24),
      new THREE.MeshStandardMaterial({{ color: 0x1e293b, metalness: 0.8, roughness: 0.2 }})
    );
    ctdMesh.position.y = 3.55;
    argoGroup.add(ctdMesh);

    const antMesh = new THREE.Mesh(
      new THREE.CylinderGeometry(0.02, 0.02, 1.8, 12),
      new THREE.MeshStandardMaterial({{ color: 0xffffff, metalness: 0.9, roughness: 0.1 }})
    );
    antMesh.position.y = 4.6;
    argoGroup.add(antMesh);

    // Base collar
    const collarMesh = new THREE.Mesh(
      new THREE.CylinderGeometry(0.3, 0.24, 0.5, 24),
      new THREE.MeshStandardMaterial({{ color: 0x1e293b, metalness: 0.8, roughness: 0.2 }})
    );
    collarMesh.position.y = -0.6;
    argoGroup.add(collarMesh);

    // Vertical holographic cable
    const cableMesh = new THREE.Mesh(
      new THREE.CylinderGeometry(0.015, 0.015, BLOCK_H - 1.0, 12),
      new THREE.MeshBasicMaterial({{ color: 0x67e8f9, transparent: true, opacity: 0.75 }})
    );
    cableMesh.position.y = -0.6;
    argoGroup.add(cableMesh);

    // 4 Brilliant Neon Glowing Depth Rings
    const depthLevels = [
      {{ depth: '0m', y: 3.8, radius: 2.0, color: 0xffffff }},
      {{ depth: '500m', y: 1.3, radius: 2.3, color: 0x67e8f9 }},
      {{ depth: '1000m', y: -1.3, radius: 2.6, color: 0x38bdf8 }},
      {{ depth: '1500m', y: -3.8, radius: 2.9, color: 0x0284c7 }}
    ];

    const depthRings = [];

    function makeTextSprite(message, colorStr) {{
      const canvas = document.createElement('canvas');
      canvas.width = 256;
      canvas.height = 128;
      const ctx = canvas.getContext('2d');
      ctx.font = 'Bold 42px monospace';
      ctx.fillStyle = colorStr || '#ffffff';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(message, 128, 64);
      const texture = new THREE.CanvasTexture(canvas);
      const spriteMat = new THREE.SpriteMaterial({{ map: texture, transparent: true, depthWrite: false }});
      const sprite = new THREE.Sprite(spriteMat);
      sprite.scale.set(1.6, 0.8, 1.0);
      return sprite;
    }}

    depthLevels.forEach(lvl => {{
      const ringGeom = new THREE.TorusGeometry(lvl.radius, 0.05, 16, 64);
      ringGeom.rotateX(Math.PI / 2);
      const ringMat = new THREE.MeshBasicMaterial({{
        color: lvl.color,
        transparent: true,
        opacity: 0.98
      }});
      const ringMesh = new THREE.Mesh(ringGeom, ringMat);
      ringMesh.position.y = lvl.y;
      argoGroup.add(ringMesh);

      const glowDisc = new THREE.Mesh(
        new THREE.CircleGeometry(lvl.radius, 32),
        new THREE.MeshBasicMaterial({{ color: lvl.color, transparent: true, opacity: 0.09, side: THREE.DoubleSide, depthWrite: false }})
      );
      glowDisc.rotateX(-Math.PI / 2);
      glowDisc.position.y = lvl.y;
      argoGroup.add(glowDisc);

      const label = makeTextSprite(lvl.depth, '#ffffff');
      label.position.set(0, lvl.y + 0.35, lvl.radius + 0.1);
      argoGroup.add(label);

      depthRings.push({{ mesh: ringMesh, phase: lvl.y }});
    }});

    // Argo Float Callout Label
    const floatLabel = makeTextSprite('ARGO FLOAT (PROFILING)', '#facc15');
    floatLabel.scale.set(3.4, 1.7, 1.0);
    floatLabel.position.set(2.8, 1.6, 1.2);
    argoGroup.add(floatLabel);

    const calloutLine = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0.3, 1.6, 0),
        new THREE.Vector3(1.8, 1.6, 0)
      ]),
      new THREE.LineBasicMaterial({{ color: 0xfacc15, transparent: true, opacity: 0.9 }})
    );
    argoGroup.add(calloutLine);

    // Contoured Seabed
    const seabedGeom = new THREE.PlaneGeometry(BLOCK_W + 1.2, BLOCK_D + 1.2, 54, 54);
    seabedGeom.rotateX(-Math.PI / 2);
    const seabedPos = seabedGeom.attributes.position;
    for (let i = 0; i < seabedPos.count; i++) {{
      const u = seabedPos.getX(i);
      const v = seabedPos.getZ(i);
      const ridge = Math.sin(u * 0.9) * Math.cos(v * 0.9) * 0.55;
      const micro = Math.sin(u * 2.5 + v * 2.2) * 0.2;
      seabedPos.setY(i, ridge + micro - 0.2);
    }}
    seabedGeom.computeVertexNormals();

    const seabedMesh = new THREE.Mesh(
      seabedGeom,
      new THREE.MeshStandardMaterial({{
        color: 0x0f172a,
        roughness: 0.85,
        metalness: 0.2,
        flatShading: true
      }})
    );
    seabedMesh.position.set(0, -BLOCK_H / 2 - 0.25, 0);
    oceanGroup.add(seabedMesh);

    const seabedLabel = makeTextSprite('BATHYMETRIC SEABED', '#94a3b8');
    seabedLabel.scale.set(3.2, 1.6, 1.0);
    seabedLabel.position.set(3.2, -BLOCK_H / 2 - 0.8, 4.0);
    oceanGroup.add(seabedLabel);

    // Satellite Scan Cone
    const scanCone = new THREE.Mesh(
      new THREE.ConeGeometry(BLOCK_W * 0.7, 9.0, 4, 1, true),
      new THREE.MeshBasicMaterial({{ color: 0x38bdf8, transparent: true, opacity: 0.08, wireframe: true }})
    );
    scanCone.rotateX(Math.PI);
    scanCone.position.set(0, BLOCK_H / 2 + 4.5, 0);
    oceanGroup.add(scanCone);

    // Animation Loop
    let isAutoRotating = true;
    let isWireframeVisible = true;
    const clock = new THREE.Clock();

    function animate() {{
      requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();

      if (isAutoRotating) {{
        oceanGroup.rotation.y += 0.0035;
      }}

      for (let i = 0; i < wavePos.count; i++) {{
        const u = wavePos.getX(i);
        const w = wavePos.getZ(i);
        const wave = Math.sin(u * 0.8 + elapsed * 1.8) * 0.06 + Math.cos(w * 0.9 + elapsed * 1.5) * 0.05;
        wavePos.setY(i, waveOrigY[i] + wave);
      }}
      waveSurfaceGeom.computeVertexNormals();
      waveSurfaceGeom.attributes.position.needsUpdate = true;

      depthRings.forEach(r => {{
        const pulse = 1.0 + Math.sin(elapsed * 2.5 + r.phase) * 0.035;
        r.mesh.scale.set(pulse, 1, pulse);
      }});

      scanCone.rotation.y = elapsed * 0.2;

      controls.update();

      if (composer) {{
        composer.render();
      }} else {{
        renderer.render(scene, camera);
      }}
    }}
    animate();

    const btnRotate = document.getElementById('btn-rotate');
    btnRotate.addEventListener('click', () => {{
      isAutoRotating = !isAutoRotating;
      btnRotate.classList.toggle('active', isAutoRotating);
    }});

    const btnWireframe = document.getElementById('btn-wireframe');
    btnWireframe.addEventListener('click', () => {{
      isWireframeVisible = !isWireframeVisible;
      btnWireframe.classList.toggle('active', isWireframeVisible);
      cageLine.visible = isWireframeVisible;
      surfaceGrid.visible = isWireframeVisible;
    }});

    const btnReset = document.getElementById('btn-reset');
    btnReset.addEventListener('click', () => {{
      camera.position.set(22, 16, 22);
      controls.target.set(0, 0, 0);
      oceanGroup.rotation.y = 0;
    }});

    window.addEventListener('resize', () => {{
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
      if (composer) composer.setSize(window.innerWidth, window.innerHeight);
    }});
  </script>
</body>
</html>
"""

with open("sample_3d_ocean_model/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Standalone index.html with inline base64 textures successfully written!")
