import random
from settings import WIDTH, HEIGHT, CELL_SIZE, MAX_OBSTACLES

def generate_obstacles(count=None):
    if count is None:
        count = MAX_OBSTACLES
        
    obstacles = set()
    attempts = 0
    while len(obstacles) < count and attempts < 100:
        x = random.randrange(CELL_SIZE, WIDTH - CELL_SIZE, CELL_SIZE)
        y = random.randrange(CELL_SIZE, HEIGHT - CELL_SIZE, CELL_SIZE)
        
        # Avoid middle area for spawn safety
        if abs(x - WIDTH//2) < 4 * CELL_SIZE and abs(y - HEIGHT//2) < 4 * CELL_SIZE:
            attempts += 1
            continue
            
        obstacles.add((x, y))
        attempts += 1
    return list(obstacles)