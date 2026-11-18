import numpy as np
from PIL import Image, ImageFilter
import math

def create_ocean_surface_texture(filename="sample_3d_ocean_model/water_surface.png"):
    W, H = 1024, 1024
    
    # 1. Base vibrant oceanic cyan gradient
    x = np.linspace(-1, 1, W)
    y = np.linspace(-1, 1, H)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)

    # Core water color
    c_center = np.array([56, 189, 248], dtype=np.float32)  # #38bdf8
    c_edge = np.array([2, 132, 199], dtype=np.float32)     # #0284c7
    c_deep = np.array([12, 74, 110], dtype=np.float32)     # #0c4a6e

    # Base radial wash
    t = np.clip(R / 1.2, 0, 1)[:, :, np.newaxis]
    rgb = (1 - t) * c_center + t * c_edge

    # 2. Delicate wave ripple mesh
    theta = np.linspace(0, 12 * np.pi, W)
    phi = np.linspace(0, 12 * np.pi, H)
    TH, PH = np.meshgrid(theta, phi)

    wave1 = np.sin(TH * 1.0 + PH * 0.8) * 0.15
    wave2 = np.cos(TH * 1.5 - PH * 1.2) * 0.12
    wave3 = np.sin((TH + PH) * 2.0) * 0.08
    ripples = wave1 + wave2 + wave3

    # Specular glints
    glints = np.clip(ripples, 0, 1) ** 3
    glint_color = np.array([240, 253, 255], dtype=np.float32)

    rgb += (glint_color - rgb) * (glints[:, :, np.newaxis] * 0.45)
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)

    img = Image.fromarray(rgb, mode="RGB")
    img = img.filter(ImageFilter.GaussianBlur(radius=1.0))
    img.save(filename, quality=95)
    print(f"Generated realistic water surface: {filename}")

if __name__ == "__main__":
    create_ocean_surface_texture()
