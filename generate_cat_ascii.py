import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SOURCE_IMG = "d:/Projects/mtritran/cat_input.jpg"
OUTPUT_GIF = "d:/Projects/mtritran/cat_christmas.gif"
FONT_PATH = "C:/Windows/Fonts/consola.ttf"

# Target grid size (balanced for readability and profile fit)
COLS = 82
ROWS = 56
CHAR_W = 7
CHAR_H = 13
PADDING_TOP = 26
PADDING_BOTTOM = 26
PADDING_SIDE = 12

CANVAS_W = COLS * CHAR_W + PADDING_SIDE * 2
CANVAS_H = ROWS * CHAR_H + PADDING_TOP + PADDING_BOTTOM

# ASCII ramp from dark to bright
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

# Pre-generate snowfall particles (seamless looping)
NUM_SNOW = 110
np.random.seed(42)
snow_x = np.random.uniform(0, COLS, NUM_SNOW)
snow_y_start = np.random.uniform(0, ROWS, NUM_SNOW)
snow_speed = np.random.uniform(1.0, 2.5, NUM_SNOW)
snow_drift = np.random.uniform(0.5, 2.0, NUM_SNOW)
snow_phase = np.random.uniform(0, 2 * math.pi, NUM_SNOW)
snow_type = np.random.choice(["*", "+", ".", "o"], NUM_SNOW, p=[0.25, 0.35, 0.3, 0.1])

# Street lamp approximate coordinate in grid (top-left)
LAMP_X = int(COLS * 0.18)
LAMP_Y = int(ROWS * 0.16)

# Cat eyes approximate coordinates in grid
EYE1_X, EYE1_Y = int(COLS * 0.52), int(ROWS * 0.62)
EYE2_X, EYE2_Y = int(COLS * 0.72), int(ROWS * 0.62)

N_FRAMES = 36
frames = []

print(f"Generating {N_FRAMES} frames of Festive ASCII Cat...")

for f in range(N_FRAMES):
    t = (f / N_FRAMES) * 2 * math.pi
    
    # Create canvas
    frame_img = Image.new("RGB", (CANVAS_W, CANVAS_H), (10, 12, 16))
    draw = ImageDraw.Draw(frame_img)
    
    # 1. Lamp pulsating light multiplier
    lamp_pulse = 1.0 + 0.35 * math.sin(t * 2)
    
    # 2. Render ASCII character grid
    for r in range(ROWS):
        for c in range(COLS):
            r_val, g_val, b_val = rgb_data[r, c]
            
            # Apply warm glow if near the street lamp
            dist_lamp = math.hypot(c - LAMP_X, r - LAMP_Y)
            if dist_lamp < 18:
                glow_factor = max(0.0, 1.0 - dist_lamp / 18) * lamp_pulse
                r_val = min(255.0, r_val + glow_factor * 70)
                g_val = min(255.0, g_val + glow_factor * 50)
                b_val = max(0.0, b_val - glow_factor * 20)
            
            # Calculate luminance
            lum = 0.299 * r_val + 0.587 * g_val + 0.114 * b_val
            ramp_idx = int((lum / 255.0) * (len(RAMP) - 1))
            ch = RAMP[ramp_idx]
            
            # Subtly boost saturation for vivid terminal look
            max_c = max(r_val, g_val, b_val)
            if max_c > 0:
                sat_boost = 1.15
                r_val = min(255.0, r_val * sat_boost)
                g_val = min(255.0, g_val * sat_boost)
                b_val = min(255.0, b_val * sat_boost)
            
            x_pos = PADDING_SIDE + c * CHAR_W
            y_pos = PADDING_TOP + r * CHAR_H
            
            if ch != ' ':
                draw.text((x_pos, y_pos), ch, font=font, fill=(int(r_val), int(g_val), int(b_val)))
    
    # 3. Render falling snow particles
    for i in range(NUM_SNOW):
        cur_y = (snow_y_start[i] + (f / N_FRAMES) * snow_speed[i] * ROWS) % ROWS
        drift = math.sin(t + snow_phase[i]) * snow_drift[i]
        cur_x = (snow_x[i] + drift) % COLS
        
        c_int = int(cur_x)
        r_int = int(cur_y)
        
        sx = PADDING_SIDE + c_int * CHAR_W
        sy = PADDING_TOP + r_int * CHAR_H
        
        ch_snow = snow_type[i]
        # Snow color with slight blueish-white glow
        snow_col = (255, 255, 255) if ch_snow in ["*", "o"] else (210, 235, 255)
        draw.text((sx, sy), ch_snow, font=font_bold, fill=snow_col)
    
    # 4. Subtle twinkle on the cat eyes
    eye_twinkle = (math.sin(t * 3) + 1) * 0.5
    if eye_twinkle > 0.6:
        glint_ch = "+" if eye_twinkle > 0.85 else "."
        draw.text((PADDING_SIDE + EYE1_X * CHAR_W, PADDING_TOP + EYE1_Y * CHAR_H), glint_ch, font=font_bold, fill=(255, 255, 200))
        draw.text((PADDING_SIDE + EYE2_X * CHAR_W, PADDING_TOP + EYE2_Y * CHAR_H), glint_ch, font=font_bold, fill=(255, 255, 200))
    
    # 5. Header HUD Bar
    header_text = "cat_christmas.py • ❄️  Winter Park • @mtritran"
    draw.text((PADDING_SIDE, 6), header_text, font=font, fill=(100, 140, 180))
    
    # 6. Festive Footer Text
    footer_text = "🐾  M E R R Y   C H R I S T M A S   🎄"
    # Center footer text
    text_w = len(footer_text) * CHAR_W
    foot_x = max(PADDING_SIDE, (CANVAS_W - text_w) // 2)
    # Color pulse
    gold_val = int(210 + 45 * math.sin(t * 2))
    draw.text((foot_x, CANVAS_H - 20), footer_text, font=font_bold, fill=(255, gold_val, 100))
    
    # Quantize to 256 colors for clean GIF encoding
    frame_q = frame_img.convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
    frames.append(frame_q)
    print(f"Frame {f+1}/{N_FRAMES} ready", end="\r")

print(f"\nSaving animated GIF to {OUTPUT_GIF}...")
frames[0].save(
    OUTPUT_GIF,
    save_all=True,
    append_images=frames[1:],
    duration=75,
    loop=0,
    optimize=True
)

file_size_mb = os.path.getsize(OUTPUT_GIF) / (1024 * 1024)
print(f"Done! File size: {file_size_mb:.2f} MB")
