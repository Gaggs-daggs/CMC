#!/bin/bash
# ============================================================
# Generate PWA icon PNGs from SVG using sips (macOS built-in)
# Run: bash scripts/generate-icons.sh
# ============================================================

ICON_DIR="frontend/web/public/icons"
SVG_SRC="$ICON_DIR/icon.svg"
SIZES=(72 96 128 144 152 192 384 512)

echo "🎨 Generating PWA icons..."

# Check if we have rsvg-convert (from librsvg) or fall back to sips
if command -v rsvg-convert &> /dev/null; then
  for size in "${SIZES[@]}"; do
    rsvg-convert -w "$size" -h "$size" "$SVG_SRC" > "$ICON_DIR/icon-${size}x${size}.png"
    echo "  ✅ icon-${size}x${size}.png"
  done
elif command -v magick &> /dev/null; then
  # ImageMagick 7
  for size in "${SIZES[@]}"; do
    magick "$SVG_SRC" -resize "${size}x${size}" "$ICON_DIR/icon-${size}x${size}.png"
    echo "  ✅ icon-${size}x${size}.png"
  done
elif command -v convert &> /dev/null; then
  # ImageMagick 6
  for size in "${SIZES[@]}"; do
    convert "$SVG_SRC" -resize "${size}x${size}" "$ICON_DIR/icon-${size}x${size}.png"
    echo "  ✅ icon-${size}x${size}.png"
  done
else
  echo "⚠️  No SVG → PNG converter found."
  echo "   Install librsvg: brew install librsvg"
  echo "   Or ImageMagick:  brew install imagemagick"
  echo ""
  echo "📝 Creating placeholder PNGs with sips workaround..."
  
  # Fallback: Create a simple colored square PNG using Python (always available on macOS)
  python3 -c "
import struct, zlib, os

def create_icon(size, path):
    # Simple PNG with gradient-like color (#667eea → #764ba2)
    raw = b''
    for y in range(size):
        raw += b'\\x00'  # filter byte
        for x in range(size):
            # Gradient purple
            r = int(102 + (118-102) * (x+y) / (2*size))
            g = int(126 + (75-126) * (x+y) / (2*size))
            b = int(234 + (162-234) * (x+y) / (2*size))
            a = 255
            # Draw a rounded-corner effect (simple circle mask)
            cx, cy = size/2, size/2
            radius = size * 0.42
            dist = ((x-cx)**2 + (y-cy)**2) ** 0.5
            if dist > radius + size*0.08:
                a = 0
            elif dist > radius:
                a = int(255 * (1 - (dist - radius) / (size*0.08)))
            # Draw cross in center
            cross_w = size * 0.12
            cross_h = size * 0.32
            in_v = abs(x - cx) < cross_w and abs(y - cy) < cross_h
            in_h = abs(y - cy) < cross_w and abs(x - cx) < cross_h
            if (in_v or in_h) and a > 0:
                r, g, b = 0, 212, 170  # teal cross
            raw += struct.pack('BBBB', r, g, b, a)
    
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    
    ihdr = struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)
    png = b'\\x89PNG\\r\\n\\x1a\\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', zlib.compress(raw))
    png += chunk(b'IEND', b'')
    
    with open(path, 'wb') as f:
        f.write(png)
    print(f'  ✅ {os.path.basename(path)}')

sizes = [72, 96, 128, 144, 152, 192, 384, 512]
for s in sizes:
    create_icon(s, f'$ICON_DIR/icon-{s}x{s}.png')
"
fi

echo ""
echo "✅ All icons generated in $ICON_DIR/"
