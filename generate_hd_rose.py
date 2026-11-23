import os, time
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
pygame.init()
import numpy as np
from PIL import Image

import rose_bouquet as rb

# Remove HUD (credit, timer, stats)
def clean_draw(self, t):
    w, h = self.w, self.h
    char, col, steady, info = rb.frame(t, self.cols, self.rows, self.cw, self.ch)
    grey = pygame.image.frombuffer(self.atlas[char].transpose(0, 2, 1, 3).tobytes(), (w, h), 'P')
    grey.set_palette(rb.GREYS)
    self.art.blit(grey, (0, 0))
    if self.last_t is None or t < self.last_t:
        self.trail.fill((0, 0, 0))
    self.last_t = t
    self.trail.fill((int(rb.TRAIL * 255),) * 3, special_flags=pygame.BLEND_MULT)
    self.trail.blit(self.tinted(col * ~steady[..., None], self.moving), (0, 0), special_flags=pygame.BLEND_MAX)
    self.out.blit(self.trail, (0, 0))
    self.out.blit(self.tinted(col * steady[..., None], self.still), (0, 0), special_flags=pygame.BLEND_MAX)
    if info['message']:
        m = info['message']
        for letter, x, rgb in m['letters']:
            g = self.big.render(letter, True, tuple(int(255 * v) for v in rgb))
            self.out.blit(g, (int(x - g.get_width() / 2), int(m['y'] - g.get_height() / 2)))
    self.glow(self.out)
    return self.out

rb.Renderer.draw = clean_draw
renderer = rb.Renderer(hint=False)

# Compact Crop: remove empty top & bottom padding
crop_box = (0, 70, 791, 830) # 791 x 760
out_w, out_h = 620, int(760 * (620 / 791)) # 620 x 595 (or slightly more compact: 600 x 480)
out_w, out_h = 600, 480

print(f"Rendering compact HD animation at {out_w}x{out_h} (cropped from {crop_box})...")

times = np.linspace(0.5, 16.5, 110)
frames = []

t0 = time.time()
for i, t in enumerate(times):
    renderer.draw(t)
    raw = pygame.image.tostring(renderer.out, 'RGB')
    im = Image.frombytes('RGB', (renderer.w, renderer.h), raw)
    im_cropped = im.crop(crop_box)
    im_resized = im_cropped.resize((out_w, out_h), Image.Resampling.LANCZOS)
    frames.append(im_resized.quantize(colors=128, method=Image.Quantize.FASTOCTREE))
    if (i + 1) % 25 == 0:
        print(f"Rendered {i + 1}/{len(times)} frames...")

t1 = time.time()
print(f"All {len(times)} frames rendered in {t1 - t0:.1f}s. Saving GIF...")

frames[0].save(
    'rose_bouquet.gif',
    save_all=True,
    append_images=frames[1:],
    duration=100,
    loop=0,
    optimize=True
)

file_size = os.path.getsize('rose_bouquet.gif')
print(f"Saved compact rose_bouquet.gif successfully! File size: {file_size / (1024*1024):.2f} MB, Dimensions: {out_w}x{out_h}")
