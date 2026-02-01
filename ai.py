import random
from collections import deque
from settings import CELL_SIZE, WIDTH, HEIGHT

def ai_move(snake, food, obstacles, other_snake_body=None):
    head = snake.body[0]
    
    # Simple BFS to find the shortest path to food avoiding obstacles and snakes
    def get_path(start, target):
        queue = deque([(start, [])])
        visited = {start}
        
        # Combine all collision points
        all_obstacles = set(obstacles) | set(snake.body[1:])
        if other_snake_body:
            all_obstacles |= set(other_snake_body)
            
        while queue:
            (cx, cy), path = queue.popleft()
            
            if (cx, cy) == target:
                return path
                
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = cx + dx * CELL_SIZE, cy + dy * CELL_SIZE
                
                if (0 <= nx < WIDTH and 0 <= ny < HEIGHT and 
                    (nx, ny) not in all_obstacles and 
                    (nx, ny) not in visited):
                    
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(dx, dy)]))
        return None

    path = get_path(head, food)
    
    if path:
        snake.next_direction = path[0]
    else:
        # If no path to food, try to move to any safe neighbor
        all_obstacles = set(obstacles) | set(snake.body[1:])
        if other_snake_body:
            all_obstacles |= set(other_snake_body)
            
        safe_moves = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = head[0] + dx * CELL_SIZE, head[1] + dy * CELL_SIZE
            if (0 <= nx < WIDTH and 0 <= ny < HEIGHT and (nx, ny) not in all_obstacles):
                safe_moves.append((dx, dy))
        
        if safe_moves:
            snake.next_direction = random.choice(safe_moves)
        else:
            # Game over for AI soon, but try to keep moving
            pass 