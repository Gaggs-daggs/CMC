"""
Generate Atlas AI rounded logo and all PWA icon sizes.
Uses the attached Atlas AI logo image.
"""
import sys
import os
from PIL import Image, ImageDraw

def make_circular(img, size):
    """Make image circular with antialiasing for smooth edges."""
    # Resize to target size with high quality
    img_resized = img.resize((size, size), Image.LANCZOS)
    
    # Create circular mask (use 4x supersampling for smooth edges)
    supersample = size * 4
    mask = Image.new('L', (supersample, supersample), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, supersample - 1, supersample - 1), fill=255)
    mask = mask.resize((size, size), Image.LANCZOS)
    
    # Apply mask
    output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    output.paste(img_resized, (0, 0))
    output.putalpha(mask)
    
    return output


def generate_all_icons(source_path, output_dir):
    """Generate all required icon sizes from source logo."""
    # Open source image
    img = Image.open(source_path).convert('RGBA')
    
    # Crop to center square (the logo part)
    w, h = img.size
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    img_square = img.crop((left, top, left + min_dim, top + min_dim))
    
    # PWA icon sizes
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    os.makedirs(output_dir, exist_ok=True)
    
    for size in sizes:
        circular = make_circular(img_square, size)
        out_path = os.path.join(output_dir, f'icon-{size}x{size}.png')
        circular.save(out_path, 'PNG', optimize=True)
        print(f'  ✅ Generated {out_path} ({size}x{size})')
    
    # Also save full-size rounded logo for use in the app
    logo_full = make_circular(img_square, 512)
    logo_path = os.path.join(output_dir, 'atlas-logo.png')
    logo_full.save(logo_path, 'PNG', optimize=True)
    print(f'  ✅ Generated {logo_path} (512x512 full logo)')
    
    # Generate favicon (32x32 and 16x16)
    favicon_32 = make_circular(img_square, 32)
    favicon_32.save(os.path.join(output_dir, 'favicon-32x32.png'), 'PNG')
    print(f'  ✅ Generated favicon-32x32.png')
    
    favicon_16 = make_circular(img_square, 16)
    favicon_16.save(os.path.join(output_dir, 'favicon-16x16.png'), 'PNG')
    print(f'  ✅ Generated favicon-16x16.png')
    
    # Generate SVG wrapper that references the PNG
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <clipPath id="circle">
      <circle cx="256" cy="256" r="256"/>
    </clipPath>
  </defs>
  <image href="atlas-logo.png" width="512" height="512" clip-path="url(#circle)"/>
</svg>'''
    
    svg_path = os.path.join(output_dir, 'icon.svg')
    with open(svg_path, 'w') as f:
        f.write(svg_content)
    print(f'  ✅ Generated {svg_path}')
    
    print(f'\n🎉 All icons generated successfully!')


if __name__ == '__main__':
    source = sys.argv[1] if len(sys.argv) > 1 else None
    if not source:
        print("Usage: python generate_logo.py <source_image_path>")
        sys.exit(1)
    
    output = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          'frontend', 'web', 'public', 'icons')
    
    print(f'📦 Source: {source}')
    print(f'📁 Output: {output}')
    print()
    
    generate_all_icons(source, output)
