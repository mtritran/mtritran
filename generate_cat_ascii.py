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

LAMP_X, LAMP_Y = int(COLS * 0.18), int(ROWS * 0.16)
EYE1_X, EYE1_Y = int(COLS * 0.52), int(ROWS * 0.62)
EYE2_X, EYE2_Y = int(COLS * 0.72), int(ROWS * 0.62)

# -------------------------------------------------------------
# Pure Snowfall Animation:
# 36 frames @ 80ms = ~2.88 seconds seamless infinite loop
# All pixels fully drawn from frame 0 (no progressive drawing)
# -------------------------------------------------------------
TOTAL_FRAMES = 36

# Setup seamless snowfall particles
NUM_SNOW = 125
np.random.seed(42)
snow_x = np.random.uniform(0, COLS, NUM_SNOW)
snow_y_start = np.random.uniform(0, ROWS, NUM_SNOW)
# snow_cycles: each snowflake completes 1, 2, or 3 full vertical screen traversals for perfect loop
snow_cycles = np.random.choice([1, 2, 3], NUM_SNOW, p=[0.45, 0.40, 0.15])
snow_drift = np.random.uniform(0.6, 2.0, NUM_SNOW)
snow_phase = np.random.uniform(0, 2 * math.pi, NUM_SNOW)
snow_type = np.random.choice(["*", "+", ".", "o"], NUM_SNOW, p=[0.25, 0.35, 0.30, 0.10])

frames = []
print(f"Generating {TOTAL_FRAMES} frames of pure snowfall ASCII Cat...")

for f in range(TOTAL_FRAMES):
    # progress in [0, 1)
    prog = f / float(TOTAL_FRAMES)
    cycle_t = prog * 2 * math.pi
    
    # Base dark canvas
    frame_img = Image.new("RGB", (CANVAS_W, CANVAS_H), (10, 12, 16))
    draw = ImageDraw.Draw(frame_img)
    
    # Lamp breathing glow (smooth sine wave)
    lamp_pulse = 1.0 + 0.32 * math.sin(cycle_t * 2)
    
    # 1. Render complete ASCII character grid
    for r in range(ROWS):
        for c in range(COLS):
            r_val, g_val, b_val = rgb_data[r, c]
            
            # Lamp radial glow
            dist_lamp = math.hypot(c - LAMP_X, r - LAMP_Y)
            if dist_lamp < 18:
                glow_factor = max(0.0, 1.0 - dist_lamp / 18) * lamp_pulse
                r_val = min(255.0, r_val + glow_factor * 70)
                g_val = min(255.0, g_val + glow_factor * 50)
                b_val = max(0.0, b_val - glow_factor * 20)
            
            lum = 0.299 * r_val + 0.587 * g_val + 0.114 * b_val
            ramp_idx = int((lum / 255.0) * (len(RAMP) - 1))
            ch = RAMP[ramp_idx]
            
            sat_boost = 1.15
            char_col = (
                int(min(255, r_val * sat_boost)),
                int(min(255, g_val * sat_boost)),
                int(min(255, b_val * sat_boost))
            )
            
            x_pos = PADDING_SIDE + c * CHAR_W
            y_pos = PADDING_TOP + r * CHAR_H
            
            if ch != ' ':
                draw.text((x_pos, y_pos), ch, font=font, fill=char_col)
    
    # 2. Render seamless falling snow
    for i in range(NUM_SNOW):
        # Guaranteed seamless loop: (start + prog * cycles * ROWS) % ROWS
        cur_y = (snow_y_start[i] + prog * snow_cycles[i] * ROWS) % ROWS
        drift = math.sin(cycle_t + snow_phase[i]) * snow_drift[i]
        cur_x = (snow_x[i] + drift) % COLS
        
        c_int = int(cur_x)
        r_int = int(cur_y)
        
        sx = PADDING_SIDE + c_int * CHAR_W
        sy = PADDING_TOP + r_int * CHAR_H
        ch_snow = snow_type[i]
        snow_col = (255, 255, 255) if ch_snow in ["*", "o"] else (210, 235, 255)
        draw.text((sx, sy), ch_snow, font=font_bold, fill=snow_col)
    
    # 3. Eye twinkle (subtle periodic glimmer)
    twinkle = (math.sin(cycle_t * 4) + 1) * 0.5
    if twinkle > 0.65:
        glint_ch = "+" if twinkle > 0.88 else "."
        draw.text((PADDING_SIDE + EYE1_X * CHAR_W, PADDING_TOP + EYE1_Y * CHAR_H), glint_ch, font=font_bold, fill=(255, 255, 200))
        draw.text((PADDING_SIDE + EYE2_X * CHAR_W, PADDING_TOP + EYE2_Y * CHAR_H), glint_ch, font=font_bold, fill=(255, 255, 200))
    
    # 4. Header HUD Bar
    header_text = "cat_christmas.py • ❄️  Winter Park • @mtritran"
    draw.text((PADDING_SIDE, 6), header_text, font=font, fill=(100, 140, 180))
    
    # 5. Footer festive text
    footer_text = "🐾  M E R R Y   C H R I S T M A S   🎄"
    text_w = len(footer_text) * CHAR_W
    foot_x = max(PADDING_SIDE, (CANVAS_W - text_w) // 2)
    gold_val = int(210 + 45 * math.sin(cycle_t * 2))
    draw.text((foot_x, CANVAS_H - 20), footer_text, font=font_bold, fill=(255, gold_val, 100))
    
    # Quantize palette
    frame_q = frame_img.convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
    frames.append(frame_q)
    print(f"Frame {f+1}/{TOTAL_FRAMES} ready", end="\r")

print(f"\nEncoding GIF to {OUTPUT_GIF} (seamless 80ms loop)...")
frames[0].save(
    OUTPUT_GIF,
    save_all=True,
    append_images=frames[1:],
    duration=80,
    loop=0,
    optimize=True
)

size_mb = os.path.getsize(OUTPUT_GIF) / (1024 * 1024)
print(f"Done! File size: {size_mb:.2f} MB")
