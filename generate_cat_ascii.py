import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SOURCE_IMG = "d:/Projects/mtritran/cat_input.jpg"
OUTPUT_GIF = "d:/Projects/mtritran/cat_christmas.gif"
FONT_PATH = "C:/Windows/Fonts/consola.ttf"

# Grid configuration
COLS = 82
ROWS = 56
CHAR_W = 7
CHAR_H = 13
PADDING_TOP = 26
PADDING_BOTTOM = 26
PADDING_SIDE = 12

CANVAS_W = COLS * CHAR_W + PADDING_SIDE * 2
CANVAS_H = ROWS * CHAR_H + PADDING_TOP + PADDING_BOTTOM

RAMP = " .':;!+*xoe$#@&B"

# Load source image
base_img = Image.open(SOURCE_IMG).convert("RGB")
img_small = base_img.resize((COLS, ROWS), Image.Resampling.LANCZOS)
rgb_data = np.array(img_small, dtype=np.float32)

# Load font
try:
    font = ImageFont.truetype(FONT_PATH, 11)
    font_bold = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 11)
except Exception:
    font = ImageFont.load_default()
    font_bold = font

# Compute appearance timeline for each pixel (0.0 to 0.75 of total time)
np.random.seed(42)
t_appear = np.zeros((ROWS, COLS), dtype=np.float32)

LAMP_X, LAMP_Y = int(COLS * 0.18), int(ROWS * 0.16)
EYE1_X, EYE1_Y = int(COLS * 0.52), int(ROWS * 0.62)
EYE2_X, EYE2_Y = int(COLS * 0.72), int(ROWS * 0.62)

for r in range(ROWS):
    for c in range(COLS):
        # 1. Lamp
        d_lamp = math.hypot(c - LAMP_X, r - LAMP_Y)
        is_lamp = d_lamp < 9
        
        # 2. Cat face & body
        is_cat = (26 <= r <= 50) and (34 <= c <= 70)
        
        # 3. Santa Hat
        is_hat = (14 <= r <= 28) and (36 <= c <= 78)
        
        # 4. Tangerine
        is_tangerine = (42 <= r <= 54) and (18 <= c <= 36)
        
        # 5. Cola
        is_cola = (38 <= r <= 55) and (68 <= c <= 81)
        
        jitter = np.random.uniform(-0.03, 0.03)
        
        if is_lamp:
            t_appear[r, c] = 0.20 + 0.10 * (d_lamp / 9.0) + jitter
        elif is_hat:
            t_appear[r, c] = 0.55 + 0.12 * ((r - 14) / 14.0) + jitter
        elif is_tangerine:
            t_appear[r, c] = 0.48 + np.random.uniform(0.0, 0.08)
        elif is_cola:
            t_appear[r, c] = 0.50 + np.random.uniform(0.0, 0.08)
        elif is_cat:
            # Cat materializes from bottom up towards face
            t_appear[r, c] = 0.30 + 0.22 * (1.0 - (r - 26) / 24.0) + jitter
        else:
            # Background trees and snow ground
            wave = (r / float(ROWS)) * 0.6 + (c / float(COLS)) * 0.4
            t_appear[r, c] = 0.02 + 0.26 * wave + jitter

# Normalize t_appear so all pixels finish drawing by progress = 0.70
t_min, t_max = t_appear.min(), t_appear.max()
t_appear = 0.02 + (t_appear - t_min) / (t_max - t_min) * 0.68

# Falling snow setup
NUM_SNOW = 110
snow_x = np.random.uniform(0, COLS, NUM_SNOW)
snow_y_start = np.random.uniform(0, ROWS, NUM_SNOW)
snow_speed = np.random.uniform(1.2, 2.8, NUM_SNOW)
snow_drift = np.random.uniform(0.5, 2.0, NUM_SNOW)
snow_phase = np.random.uniform(0, 2 * math.pi, NUM_SNOW)
snow_type = np.random.choice(["*", "+", ".", "o"], NUM_SNOW, p=[0.25, 0.35, 0.3, 0.1])

N_FRAMES = 48
frames = []

print(f"Rendering {N_FRAMES} progressive drawing frames...")

for f in range(N_FRAMES):
    # progress goes from 0.0 to 1.0
    prog = f / float(N_FRAMES)
    
    # Canvas
    frame_img = Image.new("RGB", (CANVAS_W, CANVAS_H), (10, 12, 16))
    draw = ImageDraw.Draw(frame_img)
    
    # Lamp pulse
    lamp_pulse = 1.0 + 0.35 * math.sin(prog * 4 * math.pi)
    
    # Render ASCII Grid
    for r in range(ROWS):
        for c in range(COLS):
            t_app = t_appear[r, c]
            
            # Pixel not yet drawn
            if prog < t_app:
                continue
            
            r_val, g_val, b_val = rgb_data[r, c]
            
            # Apply warm glow if near the street lamp
            dist_lamp = math.hypot(c - LAMP_X, r - LAMP_Y)
            if dist_lamp < 18 and prog >= 0.25:
                glow_factor = max(0.0, 1.0 - dist_lamp / 18) * lamp_pulse
                r_val = min(255.0, r_val + glow_factor * 70)
                g_val = min(255.0, g_val + glow_factor * 50)
                b_val = max(0.0, b_val - glow_factor * 20)
            
            # Calculate luminance
            lum = 0.299 * r_val + 0.587 * g_val + 0.114 * b_val
            ramp_idx = int((lum / 255.0) * (len(RAMP) - 1))
            ch = RAMP[ramp_idx]
            
            time_since = prog - t_app
            
            # FLASH EFFECT on newly born pixels (glittering burst)
            if time_since < 0.05:
                # Bright sparkling white / cyan flash
                spark_progress = time_since / 0.05
                ch = "*" if (r + c) % 2 == 0 else "+"
                flash_r = int(min(255, r_val + (1.0 - spark_progress) * 200))
                flash_g = int(min(255, g_val + (1.0 - spark_progress) * 220))
                flash_b = int(min(255, b_val + (1.0 - spark_progress) * 255))
                char_col = (flash_r, flash_g, flash_b)
                cur_font = font_bold
            else:
                # Real settled ASCII pixel
                sat_boost = 1.15
                char_col = (
                    int(min(255, r_val * sat_boost)),
                    int(min(255, g_val * sat_boost)),
                    int(min(255, b_val * sat_boost))
                )
                cur_font = font
            
            x_pos = PADDING_SIDE + c * CHAR_W
            y_pos = PADDING_TOP + r * CHAR_H
            
            if ch != ' ':
                draw.text((x_pos, y_pos), ch, font=cur_font, fill=char_col)
    
    # Snow begins softly during reveal and fully flows once drawn
    snow_intensity = min(1.0, prog / 0.4)
    active_snow = int(NUM_SNOW * snow_intensity)
    
    for i in range(active_snow):
        cur_y = (snow_y_start[i] + prog * snow_speed[i] * ROWS * 1.5) % ROWS
        drift = math.sin(prog * 4 * math.pi + snow_phase[i]) * snow_drift[i]
        cur_x = (snow_x[i] + drift) % COLS
        
        c_int = int(cur_x)
        r_int = int(cur_y)
        
        # Only show snow if the pixel underneath or nearby has already begun appearing
        if prog >= t_appear[r_int, c_int] * 0.8:
            sx = PADDING_SIDE + c_int * CHAR_W
            sy = PADDING_TOP + r_int * CHAR_H
            ch_snow = snow_type[i]
            snow_col = (255, 255, 255) if ch_snow in ["*", "o"] else (210, 235, 255)
            draw.text((sx, sy), ch_snow, font=font_bold, fill=snow_col)
    
    # Cat eye twinkle once cat is drawn (after prog > 0.55)
    if prog > 0.55:
        twinkle = (math.sin(prog * 6 * math.pi) + 1) * 0.5
        if twinkle > 0.6:
            glint_ch = "+" if twinkle > 0.85 else "."
            draw.text((PADDING_SIDE + EYE1_X * CHAR_W, PADDING_TOP + EYE1_Y * CHAR_H), glint_ch, font=font_bold, fill=(255, 255, 200))
            draw.text((PADDING_SIDE + EYE2_X * CHAR_W, PADDING_TOP + EYE2_Y * CHAR_H), glint_ch, font=font_bold, fill=(255, 255, 200))
    
    # Header HUD Bar
    header_text = "cat_christmas.py • ❄️  Winter Park • @mtritran"
    # Header types out during the first 25% of animation
    header_chars = min(len(header_text), int(len(header_text) * (prog / 0.25)))
    if header_chars > 0:
        draw.text((PADDING_SIDE, 6), header_text[:header_chars], font=font, fill=(100, 140, 180))
    
    # Footer festive text types out once cat is assembled (prog > 0.70)
    footer_full = "🐾  M E R R Y   C H R I S T M A S   🎄"
    if prog >= 0.70:
        type_progress = (prog - 0.70) / 0.20
        shown_len = min(len(footer_full), int(len(footer_full) * type_progress))
        text_w = len(footer_full) * CHAR_W
        foot_x = max(PADDING_SIDE, (CANVAS_W - text_w) // 2)
        gold_val = int(210 + 45 * math.sin(prog * 4 * math.pi))
        draw.text((foot_x, CANVAS_H - 20), footer_full[:shown_len], font=font_bold, fill=(255, gold_val, 100))
    
    # Convert to adaptive palette
    frame_q = frame_img.convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
    frames.append(frame_q)
    print(f"Frame {f+1}/{N_FRAMES} ready", end="\r")

print(f"\nEncoding progressive GIF to {OUTPUT_GIF}...")

# Frame durations: 85ms during drawing, slightly longer pause at the end (1200ms) to admire the finished artwork!
durations = [85] * (N_FRAMES - 1) + [1400]

frames[0].save(
    OUTPUT_GIF,
    save_all=True,
    append_images=frames[1:],
    duration=durations,
    loop=0,
    optimize=True
)

size_mb = os.path.getsize(OUTPUT_GIF) / (1024 * 1024)
print(f"Successfully generated! File size: {size_mb:.2f} MB")
