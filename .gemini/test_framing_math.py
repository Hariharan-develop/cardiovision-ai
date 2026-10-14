import math

W = 1250.0
H = 840.0
fov = 40.0 # degrees

left_panel_w = 320.0 + 16.0 # 336
right_panel_w = 340.0 + 16.0 # 356

avail_w = W - left_panel_w - right_panel_w # 558
avail_h = H - 72.0 - 45.0 # 723

fov_rad = math.radians(fov)
tan_v = math.tan(fov_rad / 2.0)
tan_h = tan_v * (W / H)

frac_w = avail_w / W
frac_h = avail_h / H

eff_tan_v = tan_v * frac_h
eff_tan_h = tan_h * frac_w

radius = 2.1
padding = 1.25 # 25% margin

dist_v = (radius * padding) / eff_tan_v
dist_h = (radius * padding) / eff_tan_h
dist = max(dist_v, dist_h)

print(f"Viewport: {W}x{H}, Available: {avail_w}x{avail_h}")
print(f"dist_v: {dist_v:.2f}, dist_h: {dist_h:.2f} -> fittedDistance: {dist:.2f}")

# Screen size of heart
full_scene_w = 2.0 * dist * tan_h
px_per_unit = W / full_scene_w
heart_px_w = 4.2 * px_per_unit
heart_px_h = 4.2 * px_per_unit

print(f"Heart on screen: {heart_px_w:.1f}px wide, {heart_px_h:.1f}px high")
print(f"Margin inside available width ({avail_w}px): {(avail_w - heart_px_w)/2.0:.1f}px each side")
print(f"Margin inside available height ({avail_h}px): {(avail_h - heart_px_h)/2.0:.1f}px top/bottom")
