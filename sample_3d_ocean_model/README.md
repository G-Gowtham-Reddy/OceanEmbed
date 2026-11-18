# OceanEmbed 3D Subsurface Temperature Reconstruction — Sample Model

This folder contains a standalone, interactive 3D visual reconstruction sample based on the reference design. It runs independently in any modern web browser without requiring backend servers or build steps.

---

## 🚀 How to Open and View

1. **Direct Browser Launch**:
   - Double-click `index.html` inside this folder, or
   - Right-click `index.html` -> **Open with** -> **Google Chrome** / **Microsoft Edge** / **Firefox**, or
   - Enter `file:///c:/Users/HP/OneDrive/Desktop(1)/Project395/sample_3d_ocean_model/index.html` in your browser address bar.

---

## 🎨 Model Features & Controls

| Feature | Description |
| :--- | :--- |
| **3D Isometric Ocean Block** | Transparent water volume showing internal thermal stratification. |
| **Thermocline Strata** | Fluid-dynamic turbulence contours matching Kelvin-Helmholtz billows from the reference pic. |
| **Translucent Water Surface** | Live sinusoidal wave ripple vertex animation on the surface mesh. |
| **Argo Profiling Float** | Detailed 3D Argo float with sensor head, antenna, and 4 depth rings (0m, 500m, 1000m, 1500m). |
| **Contoured Bathymetry** | Contoured seabed topography base plane with 3D depth gradients. |
| **HUD Scientific Overlay** | Temperature gradient colorbar ($24^\circ\text{C}$ to $2^\circ\text{C}$), layer brackets, scale bar, compass rose. |

### Interactive Actions
- **Mouse Left Drag / Touch**: Orbit & rotate the 3D block in 360 degrees.
- **Mouse Wheel / Pinch**: Zoom in and out.
- **Mouse Right Drag**: Pan the camera.
- **Top Buttons**:
  - `Auto-Rotate`: Toggle smooth 360° rotational inspection.
  - `Explode Strata`: Spatially separate the 4 vertical depth layers to inspect inner structures.
  - `Grid Cage`: Toggle the scientific isometric bounding wireframe.
  - `Reset View`: Return camera to default isometric angle.
