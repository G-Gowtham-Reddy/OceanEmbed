# Generate detailed SVG path for India and surrounding oceans
min_lon, max_lon = 58.0, 98.0
min_lat, max_lat = -4.0, 36.0
width, height = 720, 460

def pt(lon, lat):
    x = ((lon - min_lon) / (max_lon - min_lon)) * width
    y = ((max_lat - lat) / (max_lat - min_lat)) * height
    return f"{round(x, 1)},{round(y, 1)}"

# Geographic coordinates outline of India:
# Starting from Kashmir north crown, down through western border, Gujarat, west coast peninsula, Kanyakumari, east coast, delta, northeast, Himalayas
india_coords = [
    # Kashmir / Ladakh crown
    (74.5, 35.8), (75.5, 35.8), (77.0, 35.2), (78.8, 34.2), (79.2, 33.0),
    # Himachal & Uttarakhand / Nepal border
    (78.5, 31.5), (80.2, 30.0), (81.0, 29.8), (82.5, 28.5), (84.5, 27.5),
    (86.5, 27.0), (88.0, 27.2), (88.8, 27.4),
    # Sikkim & Bhutan border & Northeast
    (89.0, 28.0), (91.5, 27.8), (93.5, 28.2), (95.5, 28.5), (96.5, 28.0),
    (96.8, 27.2), (95.8, 26.5), (94.5, 25.5), (93.2, 24.5), (92.5, 24.0),
    (92.0, 25.2), (90.2, 25.5), (89.5, 26.2),
    # Bangladesh border to West Bengal delta (Sundarbans)
    (88.8, 25.0), (88.5, 23.5), (88.9, 22.2), (88.4, 21.6),
    # Odisha coast (Bay of Bengal)
    (87.5, 21.5), (86.8, 20.6), (85.8, 19.8), (85.0, 19.3),
    # Andhra Pradesh coast (Bay of Bengal)
    (84.0, 18.5), (83.2, 17.7), (82.2, 16.8), (81.5, 16.2), (80.6, 15.8), (80.1, 14.8), (80.2, 13.8),
    # Tamil Nadu / Coromandel coast
    (80.3, 13.0), (79.9, 12.0), (79.8, 11.2), (79.8, 10.5), (79.3, 9.8), (79.3, 9.2),
    (78.5, 8.8), (77.8, 8.2),
    # Kanyakumari (Southernmost Cape)
    (77.5, 8.08),
    # Kerala / Malabar coast (Arabian Sea)
    (77.0, 8.4), (76.6, 8.8), (76.2, 9.6), (76.1, 10.2), (75.8, 11.2), (75.2, 12.0),
    # Karnataka & Goa coast (Arabian Sea)
    (74.8, 12.8), (74.4, 13.8), (74.2, 14.6), (73.8, 15.4),
    # Maharashtra / Konkan coast (Arabian Sea)
    (73.3, 16.5), (73.0, 17.5), (72.8, 18.9), (72.8, 19.5), (72.8, 20.2),
    # Gujarat Gulf of Khambhat & Kathiawar peninsula
    (72.6, 21.2), (72.2, 21.7), (71.5, 21.2), (70.8, 20.8), (69.8, 20.9), (69.0, 22.2),
    # Gulf of Kutch & Rann of Kutch
    (69.0, 22.8), (69.8, 22.9), (70.5, 23.2), (69.2, 23.6), (68.6, 23.8), (68.8, 24.3),
    # Rajasthan & Punjab western border
    (70.2, 25.5), (70.0, 26.8), (70.8, 27.8), (72.2, 29.2), (74.0, 31.0), (74.8, 32.2),
    # J&K western border
    (74.0, 33.2), (73.8, 34.5), (74.5, 35.8)
]

# Sri Lanka coordinates
sri_lanka_coords = [
    (80.1, 9.8), (80.5, 9.2), (81.2, 8.5), (81.8, 7.8), (81.8, 6.8),
    (81.2, 6.0), (80.6, 5.9), (80.0, 6.2), (79.8, 7.2), (79.8, 8.5), (80.1, 9.8)
]

def make_d(coords):
    return "M " + " L ".join(pt(lon, lat) for lon, lat in coords) + " Z"

d_india = make_d(india_coords)
d_sl = make_d(sri_lanka_coords)

print("INDIA PATH:")
print(d_india)
print("\nSRI LANKA PATH:")
print(d_sl)
