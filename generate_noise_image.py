
from PIL import Image 
from perlin_noise import PerlinNoise 


WIDTH = 800  
HEIGHT = 600 


NOISE_SCALE = 100.0


OCTAVES = 6


X_OFFSET = 0.0
Y_OFFSET = 0.0


COLORS = {
    "deep_water":   (0, 0, 100),       #
    "shallow_water":(0, 100, 200),     
    "sand":         (210, 180, 140),   
    "grass":        (50, 150, 50),     
    "forest":       (30, 100, 30),     
    "mountain":     (120, 120, 120),   
    "snow":         (220, 220, 220)    
}

def generate_landscape():
    """
    Generates a procedural landscape image using Perlin noise from the 'perlin-noise' library.
    """
    print("Generating landscape...")

    
    perlin_noise_generator = PerlinNoise(octaves=OCTAVES)

    
    img = Image.new('RGB', (WIDTH, HEIGHT))
    
    pixels = img.load()

    
    min_noise_val = float('inf')
    max_noise_val = float('-inf')

    
    noise_values_grid = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for y in range(HEIGHT):
        for x in range(WIDTH):
            
            noise_value = perlin_noise_generator([
                (x + X_OFFSET) / NOISE_SCALE,
                (y + Y_OFFSET) / NOISE_SCALE
            ])
            noise_values_grid[y][x] = noise_value

            if noise_value < min_noise_val:
                min_noise_val = noise_value
            if noise_value > max_noise_val:
                max_noise_val = noise_value

    
    if max_noise_val == min_noise_val:
        range_val = 1.0 
    else:
        range_val = max_noise_val - min_noise_val


    
    for y in range(HEIGHT):
        for x in range(WIDTH):
            
            normalized_noise = (noise_values_grid[y][x] - min_noise_val) / range_val

            
            color = (0, 0, 0) 

            if normalized_noise < 0.3:
                color = COLORS["deep_water"]
            elif normalized_noise < 0.4:
                color = COLORS["shallow_water"]
            elif normalized_noise < 0.5:
                color = COLORS["sand"]
            elif normalized_noise < 0.65:
                color = COLORS["grass"]
            elif normalized_noise < 0.8:
                color = COLORS["forest"]
            elif normalized_noise < 0.9:
                color = COLORS["mountain"]
            else:
                color = COLORS["snow"]

            
            pixels[x, y] = color

    
    output_filename = "landscape.png"
    img.save(output_filename)
    print(f"Landscape saved as {output_filename}")


if __name__ == "__main__":
    generate_landscape()
