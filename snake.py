import pygame
import math
from settings import CELL_SIZE, PLAYER_COLOR, PLAYER_TAIL

class Snake:
    def __init__(self, x, y, color, tail_color, controls=None, is_ai=False):
        # Position is grid-based
        self.body = [(x, y), (x - CELL_SIZE, y), (x - 2 * CELL_SIZE, y)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.color = color
        self.tail_color = tail_color
        self.controls = controls
        self.is_ai = is_ai
        self.grow = False
        self.alive = True
        self.score = 0
        self.move_counter = 0

    def handle_input(self, keys):
        if not self.controls:
            return
        
        if keys[self.controls["UP"]] and self.direction != (0, 1):
            self.next_direction = (0, -1)
        elif keys[self.controls["DOWN"]] and self.direction != (0, -1):
            self.next_direction = (0, 1)
        elif keys[self.controls["LEFT"]] and self.direction != (1, 0):
            self.next_direction = (-1, 0)
        elif keys[self.controls["RIGHT"]] and self.direction != (-1, 0):
            self.next_direction = (1, 0)

    def move(self):
        if not self.alive:
            return

        self.direction = self.next_direction
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        
        new_head = (head_x + dx * CELL_SIZE, head_y + dy * CELL_SIZE)
        
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
            self.score += 1

    def check_collision(self, width, height, obstacles, other_snake=None):
        head = self.body[0]
        
        # Wall collision
        if head[0] < 0 or head[0] >= width or head[1] < 0 or head[1] >= height:
            self.alive = False
            return True
            
        # Self collision
        if head in self.body[1:]:
            self.alive = False
            return True
            
        # Obstacle collision
        if head in obstacles:
            self.alive = False
            return True

        # Other snake collision
        if other_snake and head in other_snake.body:
            self.alive = False
            return True
            
        return False

    def draw(self, screen, current_time):
        for i, segment in enumerate(self.body):
            # Gradient color from head to tail
            ratio = i / len(self.body)
            r = int(self.color[0] * (1 - ratio) + self.tail_color[0] * ratio)
            g = int(self.color[1] * (1 - ratio) + self.tail_color[1] * ratio)
            b = int(self.color[2] * (1 - ratio) + self.tail_color[2] * ratio)
            
            # Breathing effect for segments
            size_offset = math.sin(current_time * 0.01 + i * 0.5) * 2
            rect_size = CELL_SIZE - 2 + size_offset
            
            rect = pygame.Rect(
                segment[0] + (CELL_SIZE - rect_size) // 2,
                segment[1] + (CELL_SIZE - rect_size) // 2,
                rect_size,
                rect_size
            )
            
            pygame.draw.rect(screen, (r, g, b), rect, border_radius=int(CELL_SIZE//4))
            
            # Draw eyes on the head
            if i == 0:
                eye_color = (255, 255, 255)
                eye_size = 4
                # Position eyes based on direction
                dx, dy = self.direction
                if dx == 1: # Right
                    e1 = (segment[0] + CELL_SIZE - 8, segment[1] + 6)
                    e2 = (segment[0] + CELL_SIZE - 8, segment[1] + CELL_SIZE - 10)
                elif dx == -1: # Left
                    e1 = (segment[0] + 4, segment[1] + 6)
                    e2 = (segment[0] + 4, segment[1] + CELL_SIZE - 10)
                elif dy == -1: # Up
                    e1 = (segment[0] + 6, segment[1] + 4)
                    e2 = (segment[0] + CELL_SIZE - 10, segment[1] + 4)
                else: # Down
                    e1 = (segment[0] + 6, segment[1] + CELL_SIZE - 8)
                    e2 = (segment[0] + CELL_SIZE - 10, segment[1] + CELL_SIZE - 8)
                
                pygame.draw.circle(screen, eye_color, e1, eye_size)
                pygame.draw.circle(screen, eye_color, e2, eye_size)