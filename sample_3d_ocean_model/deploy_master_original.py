import base64

with open("sample_3d_ocean_model/original_reference.jpg", "rb") as f:
    b64_orig = base64.b64encode(f.read()).decode("ascii")

html_code = f"""<!DOCTYPE html>
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
      display: flex;
      align-items: center;
      justify-content: center;
      perspective: 1200px;
    }}

    /* Sci-fi Ambient Backdrop Grid */
    .bg-grid {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-image: 
        radial-gradient(circle at 50% 40%, rgba(14, 165, 233, 0.15) 0%, rgba(3, 7, 18, 0.98) 75%),
        linear-gradient(to right, rgba(30, 58, 95, 0.12) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(30, 58, 95, 0.12) 1px, transparent 1px);
      background-size: 100% 100%, 48px 48px, 48px 48px;
      pointer-events: none;
      z-index: 1;
    }}

    /* 3D Stage & Canvas */
    .stage-container {{
      position: relative;
      width: 100vw;
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 2;
      overflow: hidden;
      cursor: grab;
    }}
    .stage-container:active {{
      cursor: grabbing;
    }}

    .viewport-3d {{
      position: relative;
      transform-style: preserve-3d;
      transition: transform 0.12s cubic-bezier(0.2, 0, 0.2, 1);
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .model-card {{
      position: relative;
      max-width: 90vw;
      max-height: 82vh;
      border-radius: 12px;
      box-shadow: 
        0 25px 60px -15px rgba(0, 0, 0, 0.9),
        0 0 50px rgba(14, 165, 233, 0.25),
        0 0 0 1px rgba(56, 189, 248, 0.3);
      transform-style: preserve-3d;
      transition: box-shadow 0.3s ease;
      background: #020617;
      display: block;
    }}
    .model-card:hover {{
      box-shadow: 
        0 30px 70px -10px rgba(0, 0, 0, 0.95),
        0 0 70px rgba(14, 165, 233, 0.38),
        0 0 0 1px rgba(56, 189, 248, 0.5);
    }}

    .master-render {{
      display: block;
      width: auto;
      height: 78vh;
      max-width: 88vw;
      object-fit: contain;
      border-radius: 12px;
      pointer-events: none;
    }}

    /* Interactive Holographic Light Shimmer on Tilt */
    .light-glare {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      border-radius: 12px;
      pointer-events: none;
      background: linear-gradient(135deg, rgba(255,255,255,0.18) 0%, rgba(56,189,248,0.08) 40%, transparent 65%);
      mix-blend-mode: overlay;
      opacity: 0.8;
      transition: opacity 0.3s ease;
    }}

    /* Pulsing Sonar Ring Overlay */
    .sonar-emitter {{
      position: absolute;
      top: 32%;
      left: 52%;
      width: 4px;
      height: 4px;
      transform: translate(-50%, -50%);
      pointer-events: none;
    }}
    .sonar-wave {{
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%) rotateX(60deg);
      border-radius: 50%;
      border: 2px solid rgba(56, 189, 248, 0.9);
      box-shadow: 0 0 16px rgba(56, 189, 248, 0.8);
      opacity: 0;
      pointer-events: none;
    }}
    .sonar-active {{
      animation: sonarPing 2.4s cubic-bezier(0.1, 0.8, 0.3, 1) infinite;
    }}
    @keyframes sonarPing {{
      0% {{
        width: 10px;
        height: 10px;
        opacity: 0.95;
      }}
      70% {{
        opacity: 0.4;
      }}
      100% {{
        width: 320px;
        height: 320px;
        opacity: 0;
      }}
    }}

    /* Interactive Hotspots on the Model */
    .hotspot {{
      position: absolute;
      border-radius: 50%;
      background: rgba(14, 165, 233, 0.25);
      border: 1px solid rgba(56, 189, 248, 0.9);
      box-shadow: 0 0 12px rgba(56, 189, 248, 0.7);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.25s ease;
      z-index: 20;
    }}
    .hotspot::after {{
      content: "";
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #ffffff;
      box-shadow: 0 0 8px #ffffff;
    }}
    .hotspot:hover {{
      transform: scale(1.35);
      background: rgba(56, 189, 248, 0.6);
      box-shadow: 0 0 20px rgba(56, 189, 248, 1);
    }}

    /* Tooltip popup */
    .telemetry-card {{
      position: absolute;
      background: rgba(15, 23, 42, 0.92);
      border: 1px solid rgba(56, 189, 248, 0.6);
      border-radius: 8px;
      padding: 10px 14px;
      min-width: 220px;
      color: #e2e8f0;
      font-size: 11px;
      box-shadow: 0 12px 30px rgba(0,0,0,0.8), 0 0 20px rgba(14, 165, 233, 0.3);
      backdrop-filter: blur(10px);
      pointer-events: none;
      opacity: 0;
      transform: translateY(10px);
      transition: all 0.25s ease;
      z-index: 30;
    }}
    .telemetry-card.visible {{
      opacity: 1;
      transform: translateY(0);
    }}
    .telemetry-title {{
      font-weight: 800;
      color: #38bdf8;
      letter-spacing: 1px;
      text-transform: uppercase;
      font-size: 11px;
      margin-bottom: 4px;
      border-bottom: 1px solid rgba(51, 65, 85, 0.6);
      padding-bottom: 3px;
    }}
    .telemetry-row {{
      display: flex;
      justify-content: space-between;
      margin: 3px 0;
      font-family: monospace;
      font-size: 10px;
    }}
    .telemetry-val {{
      font-weight: 700;
      color: #facc15;
    }}

    /* Top HUD UI */
    .top-hud {{
      position: absolute;
      top: 24px;
      left: 32px;
      right: 32px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 10;
      pointer-events: none;
    }}
    .brand-block {{
      pointer-events: auto;
    }}
    .brand-sub {{
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 2px;
      color: #38bdf8;
      text-transform: uppercase;
    }}
    .brand-main {{
      font-size: 20px;
      font-weight: 900;
      color: #ffffff;
      letter-spacing: 0.5px;
      display: flex;
      align-items: center;
      gap: 10px;
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.8);
    }}
    .orig-pill {{
      font-size: 10px;
      font-weight: 800;
      padding: 3px 8px;
      border-radius: 4px;
      background: rgba(16, 185, 129, 0.2);
      border: 1px solid rgba(52, 211, 153, 0.5);
      color: #34d399;
      letter-spacing: 1px;
    }}

    /* Controls Bar */
    .ctrl-bar {{
      display: flex;
      gap: 8px;
      pointer-events: auto;
    }}
    .ctrl-btn {{
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(51, 65, 85, 0.8);
      color: #cbd5e1;
      padding: 8px 14px;
      font-size: 11px;
      font-weight: 600;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s ease;
      backdrop-filter: blur(8px);
    }}
    .ctrl-btn:hover {{
      background: rgba(30, 41, 59, 0.95);
      border-color: #38bdf8;
      color: #ffffff;
      box-shadow: 0 0 14px rgba(56, 189, 248, 0.35);
    }}
    .ctrl-btn.active {{
      background: rgba(14, 165, 233, 0.3);
      border-color: #38bdf8;
      color: #38bdf8;
      box-shadow: 0 0 16px rgba(56, 189, 248, 0.5);
    }}

    /* Floating Hint */
    .bottom-hint {{
      position: absolute;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      font-size: 11px;
      color: #94a3b8;
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(51, 65, 85, 0.8);
      padding: 6px 18px;
      border-radius: 20px;
      pointer-events: none;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.6);
      z-index: 10;
      letter-spacing: 0.5px;
    }}
  </style>
</head>
<body>

  <div class="bg-grid"></div>

  <!-- Top HUD Bar -->
  <div class="top-hud">
    <div class="brand-block">
      <div class="brand-sub">OceanEmbed Architecture</div>
      <div class="brand-main">
        3D Subsurface Temperature Reconstruction
        <span class="orig-pill">ORIGINAL MASTER RENDER</span>
      </div>
    </div>

    <div class="ctrl-bar">
      <button id="btn-tilt" class="ctrl-btn active">3D Orbit / Tilt</button>
      <button id="btn-sonar" class="ctrl-btn active">Pulse Sonar</button>
      <button id="btn-zoom-in" class="ctrl-btn">Zoom In (+)</button>
      <button id="btn-zoom-out" class="ctrl-btn">Zoom Out (-)</button>
      <button id="btn-reset" class="ctrl-btn">Reset 3D View</button>
    </div>
  </div>

  <!-- 3D Interactive Stage -->
  <div class="stage-container" id="stage">
    <div class="viewport-3d" id="viewport">
      <div class="model-card" id="card">
        <img src="data:image/jpeg;base64,{b64_orig}" alt="OceanEmbed 3D Reconstruction Master" class="master-render" id="art" />
        <div class="light-glare" id="glare"></div>

        <!-- Sonar Pulse Ring -->
        <div class="sonar-emitter">
          <div class="sonar-wave sonar-active" id="sonar-ring"></div>
        </div>

        <!-- Interactive Hotspots on Scientific Points -->
        <!-- 1. Argo Profiling Float -->
        <div class="hotspot" style="top: 32%; left: 52%; width: 22px; height: 22px;" 
             data-title="Argo Autonomous Float" 
             data-type="profiler"
             data-depth="0 – 2000m Profiling"
             data-sensor="SBE 41CP CTD"
             data-freq="10-day Cycle"></div>

        <!-- 2. Thermocline Zone (Eddy Turbulence) -->
        <div class="hotspot" style="top: 44%; left: 34%; width: 20px; height: 20px;" 
             data-title="Thermocline Shear Layer" 
             data-type="strata"
             data-depth="150 – 700m"
             data-sensor="Kelvin-Helmholtz Billows"
             data-freq="ΔT = 16°C Drop"></div>

        <!-- 3. Abyssal Cold Water Layer -->
        <div class="hotspot" style="top: 66%; left: 38%; width: 20px; height: 20px;" 
             data-title="Abyssal Deep Water" 
             data-type="strata"
             data-depth="1500 – 2000m"
             data-sensor="Stable Ocean Baseline"
             data-freq="T = 2.4°C | S = 34.8 PSU"></div>

        <!-- 4. Bathymetric Contoured Seabed -->
        <div class="hotspot" style="top: 78%; left: 50%; width: 22px; height: 22px;" 
             data-title="Bathymetric Seabed" 
             data-type="terrain"
             data-depth="~2000m Depth"
             data-sensor="Contoured Topography"
             data-freq="Sediment Boundary"></div>

        <!-- Floating Telemetry Card -->
        <div class="telemetry-card" id="telemetry">
          <div class="telemetry-title" id="tel-title">Telemetry Sensor</div>
          <div class="telemetry-row"><span>Layer / Metric:</span><span class="telemetry-val" id="tel-depth">0 – 2000m</span></div>
          <div class="telemetry-row"><span>Sensor / Dynamics:</span><span class="telemetry-val" id="tel-sensor">CTD Head</span></div>
          <div class="telemetry-row"><span>Observation:</span><span class="telemetry-val" id="tel-freq">Active Profile</span></div>
        </div>
      </div>
    </div>
  </div>

  <div class="bottom-hint">
    Click & Drag to Tilt in 3D • Scroll to Zoom • Hover over Float & Layers for Telemetry
  </div>

  <script>
    const stage = document.getElementById('stage');
    const viewport = document.getElementById('viewport');
    const card = document.getElementById('card');
    const glare = document.getElementById('glare');
    const sonarRing = document.getElementById('sonar-ring');
    const telemetry = document.getElementById('telemetry');
    const telTitle = document.getElementById('tel-title');
    const telDepth = document.getElementById('tel-depth');
    const telSensor = document.getElementById('tel-sensor');
    const telFreq = document.getElementById('tel-freq');

    let isDragging = false;
    let startX = 0;
    let startY = 0;
    let rotX = 0;
    let rotY = 0;
    let targetRotX = 0;
    let targetRotY = 0;
    let currentScale = 1.0;
    let isAutoTilt = true;
    let autoTiltPhase = 0;

    // Mouse & Touch 3D Tilt Controls
    stage.addEventListener('mousedown', (e) => {{
      isDragging = true;
      isAutoTilt = false;
      document.getElementById('btn-tilt').classList.remove('active');
      startX = e.clientX;
      startY = e.clientY;
    }});

    window.addEventListener('mouseup', () => {{
      isDragging = false;
    }});

    window.addEventListener('mousemove', (e) => {{
      if (isDragging) {{
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        startX = e.clientX;
        startY = e.clientY;

        targetRotY += dx * 0.25;
        targetRotX -= dy * 0.25;

        // Limit tilt angles for realistic 3D isometric perspective
        targetRotX = Math.max(-28, Math.min(28, targetRotX));
        targetRotY = Math.max(-36, Math.min(36, targetRotY));
      }} else if (!isAutoTilt) {{
        // Subtle cursor parallax
        const rect = stage.getBoundingClientRect();
        const normX = (e.clientX - rect.left) / rect.width - 0.5;
        const normY = (e.clientY - rect.top) / rect.height - 0.5;
        targetRotY = normX * 18;
        targetRotX = -normY * 18;
      }}
    }});

    // Scroll Wheel Zoom
    stage.addEventListener('wheel', (e) => {{
      e.preventDefault();
      const delta = e.deltaY > 0 ? -0.08 : 0.08;
      currentScale = Math.max(0.7, Math.min(2.0, currentScale + delta));
      updateTransform();
    }}, {{ passive: false }});

    function updateTransform() {{
      viewport.style.transform = `scale(${{currentScale}}) rotateX(${{rotX}}deg) rotateY(${{rotY}}deg)`;

      // Dynamic Glare Gradient reflection
      const glareX = 50 + (rotY * 1.5);
      const glareY = 50 + (rotX * 1.5);
      glare.style.background = `linear-gradient(${{135 + rotY}}deg, rgba(255,255,255,${{0.22 - Math.abs(rotX)*0.003}}) 0%, rgba(56,189,248,0.1) 40%, transparent 70%)`;
    }}

    // Animation loop for smooth damping & auto-tilt
    function animate() {{
      requestAnimationFrame(animate);

      if (isAutoTilt) {{
        autoTiltPhase += 0.02;
        targetRotX = Math.sin(autoTiltPhase) * 6;
        targetRotY = Math.cos(autoTiltPhase * 0.7) * 9;
      }}

      rotX += (targetRotX - rotX) * 0.1;
      rotY += (targetRotY - rotY) * 0.1;
      updateTransform();
    }}
    animate();

    // Hotspots Telemetry Hover
    const hotspots = document.querySelectorAll('.hotspot');
    hotspots.forEach(spot => {{
      spot.addEventListener('mouseenter', (e) => {{
        telTitle.textContent = spot.dataset.title;
        telDepth.textContent = spot.dataset.depth;
        telSensor.textContent = spot.dataset.sensor;
        telFreq.textContent = spot.dataset.freq;

        const rect = spot.getBoundingClientRect();
        const cardRect = card.getBoundingClientRect();

        telemetry.style.left = `${{rect.left - cardRect.left + 30}}px`;
        telemetry.style.top = `${{rect.top - cardRect.top - 20}}px`;
        telemetry.classList.add('visible');
      }});

      spot.addEventListener('mouseleave', () => {{
        telemetry.classList.remove('visible');
      }});
    }});

    // Controls Buttons
    const btnTilt = document.getElementById('btn-tilt');
    btnTilt.addEventListener('click', () => {{
      isAutoTilt = !isAutoTilt;
      btnTilt.classList.toggle('active', isAutoTilt);
    }});

    const btnSonar = document.getElementById('btn-sonar');
    btnSonar.addEventListener('click', () => {{
      const isSonar = sonarRing.classList.toggle('sonar-active');
      btnSonar.classList.toggle('active', isSonar);
    }});

    document.getElementById('btn-zoom-in').addEventListener('click', () => {{
      currentScale = Math.min(2.0, currentScale + 0.18);
      updateTransform();
    }});

    document.getElementById('btn-zoom-out').addEventListener('click', () => {{
      currentScale = Math.max(0.7, currentScale - 0.18);
      updateTransform();
    }});

    document.getElementById('btn-reset').addEventListener('click', () => {{
      targetRotX = 0;
      targetRotY = 0;
      rotX = 0;
      rotY = 0;
      currentScale = 1.0;
      isAutoTilt = true;
      btnTilt.classList.add('active');
      updateTransform();
    }});
  </script>
</body>
</html>
"""

with open("sample_3d_ocean_model/index.html", "w", encoding="utf-8") as f:
    f.write(html_code)

print("Masterpiece original 3D application written successfully!")
