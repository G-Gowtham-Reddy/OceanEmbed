import numpy as np
from PIL import Image, ImageFilter
import math

def create_ocean_cross_section_texture(filename="sample_3d_ocean_model/cross_section_texture.png"):
    W, H = 2048, 2048
    
    # 1. Base vertical scientific ocean colormap matching reference pic
    stops = [
        (0.00, np.array([238, 98, 24])),    # Surface Mixed Layer warm orange 24C
        (0.16, np.array([245, 142, 32])),   # 22C
        (0.28, np.array([254, 200, 68])),   # 18C - Upper Thermocline core
        (0.40, np.array([242, 180, 50])),   # 15C - Shear layer
        (0.52, np.array([38, 185, 175])),   # 12C - Intermediate cyan
        (0.66, np.array([14, 125, 200])),   # 9C  - Transition
        (0.80, np.array([16, 50, 135])),    # 5C  - Deep water
        (1.00, np.array([5, 8, 26]))        # 2C  - Abyssal bottom
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

    # 2. Broad sweeping horizontal fluid waves + swirling Kelvin-Helmholtz eddies
    # Notice: X has 1.5 to 2.5 wavelengths across the entire width (broad swells, not high frequency!)
    x = np.linspace(0, 2.5 * np.pi, W)
    y = np.linspace(0, 1, H)
    X, Y = np.meshgrid(x, y)

    # Thermocline modulation envelope (maximum disturbance between y=0.22 and 0.58)
    envelope = np.exp(-((Y - 0.38) ** 2) / (2 * 0.14 ** 2))

    # Broad organic swells
    swell1 = np.sin(X * 1.0 + 0.4) * 0.08
    swell2 = np.cos(X * 2.2 - 0.6) * 0.04
    swell3 = np.sin(X * 3.8 + Y * 2.0) * 0.02

    # Rolling vortex eddies (Kelvin-Helmholtz cat's-eye roll-ups)
    vortex1 = np.sin(X * 3.2 + np.cos(Y * 8.0) * 0.8) * 0.035
    vortex2 = np.sin(X * 5.0 - np.sin(Y * 10.0) * 0.6) * 0.02

    total_displacement = (swell1 + swell2 + swell3 + vortex1 + vortex2) * envelope

    # Displaced Y
    displaced_Y = np.clip(Y + total_displacement, 0.0, 1.0)
    displaced_indices = (displaced_Y * (H - 1)).astype(np.int32)

    texture_rgb = base_rgb[displaced_indices, :]

    # 3. Add soft glowing isotherm filaments (wide, smooth, glowing contours)
    filament_phase = displaced_Y * 22.0
    filaments = (np.sin(filament_phase * 2 * np.pi) ** 6) * envelope * 0.35

    highlight_gold = np.array([255, 248, 205], dtype=np.float32)
    for c in range(3):
        texture_rgb[:, :, c] += (highlight_gold[c] - texture_rgb[:, :, c]) * filaments

    # 4. Soft lateral shading (ambient occlusion / depth perspective)
    lateral_shading = 1.0 - 0.15 * (np.sin(np.linspace(0, np.pi, W)) ** 0.5)
    texture_rgb = texture_rgb * lateral_shading[np.newaxis, :, np.newaxis]

    texture_rgb = np.clip(texture_rgb, 0, 255).astype(np.uint8)
    tex_img = Image.fromarray(texture_rgb, mode="RGB")
    tex_img = tex_img.filter(ImageFilter.GaussianBlur(radius=1.5))
    tex_img.save(filename, quality=95)
    print(f"Generated realistic thermocline: {filename}")

if __name__ == "__main__":
    create_ocean_cross_section_texture()
