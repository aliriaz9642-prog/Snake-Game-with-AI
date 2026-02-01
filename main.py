import pygame
import random
import sys
import math
from settings import *
from snake import Snake
from ai import ai_move
from level import generate_obstacles

# ========== INITIALIZATION ==========
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Artificial Snake")
clock = pygame.time.Clock()

# FONTS
try:
    font_title = pygame.font.SysFont(FONT_BOLD, 80)
    font_menu = pygame.font.SysFont(FONT_MAIN, 40)
    font_hud = pygame.font.SysFont(FONT_MAIN, 24)
except:
    font_title = pygame.font.Font(None, 80)
    font_menu = pygame.font.Font(None, 40)
    font_hud = pygame.font.Font(None, 24)

# ========== GAME STATES ==========
MENU = 0
PLAYING_AI = 1
PLAYING_CLASSIC = 2
GAME_OVER = 3

# ========== UTILS ==========
def draw_text(text, font, color, center):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center)
    screen.blit(surf, rect)

class Button:
    def __init__(self, x, y, w, h, text, color):
        self.rect = pygame.Rect(x - w//2, y - h//2, w, h)
        self.base_rect = self.rect.copy()
        self.text = text
        self.color = color
        self.hovered = False
        self.animation_value = 0 # 0 to 1

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered:
            self.animation_value = min(1, self.animation_value + 0.1)
        else:
            self.animation_value = max(0, self.animation_value - 0.1)
            
        # Grow/Shrink effect
        offset = int(self.animation_value * 10)
        self.rect = self.base_rect.inflate(offset, offset)

    def draw(self, screen):
        # Unique animation: Box corners change
        border_radius = int(10 + self.animation_value * 20) # Changes rectangle to more rounded
        
        # Glow effect
        if self.animation_value > 0:
            glow_rect = self.rect.inflate(8, 8)
            pygame.draw.rect(screen, self.color, glow_rect, border_radius=border_radius, width=2)
            
        pygame.draw.rect(screen, self.color, self.rect, border_radius=border_radius)
        
        text_color = BLACK if self.animation_value > 0.5 else WHITE
        draw_text(self.text, font_menu, text_color, self.rect.center)

# ========== GAME CLASS ==========
class Game:
    def __init__(self):
        self.state = MENU
        self.player = None
        self.ai_snake = None
        self.food = None
        self.obstacles = []
        self.score = 0
        self.game_speed = INITIAL_SPEED
        self.last_move_time = 0
        self.ai_last_move_time = 0
        
        # Menu Buttons
        self.btn_ai = Button(WIDTH//2, HEIGHT//2 - 20, 300, 60, "PLAY WITH AI", UI_ACCENT)
        self.btn_classic = Button(WIDTH//2, HEIGHT//2 + 80, 300, 60, "CLASSIC PLAY", UI_SECONDARY)
        
        self.particles = []
        
        # Load and scale background image for menu
        try:
            self.menu_bg = pygame.image.load("snak-pic.jpg").convert()
            self.menu_bg = pygame.transform.scale(self.menu_bg, (WIDTH, HEIGHT))
            # Create a semi-transparent overlay surface for better text readability
            self.overlay = pygame.Surface((WIDTH, HEIGHT))
            self.overlay.set_alpha(150) # 0-255 opacity
            self.overlay.fill(BG_COLOR)
        except:
            self.menu_bg = None
            self.overlay = None

    def start_game(self, mode):
        self.state = mode
        self.player = Snake(200, HEIGHT//2, PLAYER_COLOR, PLAYER_TAIL, {
            "UP": pygame.K_UP, "DOWN": pygame.K_DOWN, 
            "LEFT": pygame.K_LEFT, "RIGHT": pygame.K_RIGHT
        })
        
        self.obstacles = generate_obstacles(MAX_OBSTACLES)
        
        if mode == PLAYING_AI:
            self.ai_snake = Snake(WIDTH - 200, HEIGHT//2, AI_COLOR, AI_TAIL, is_ai=True)
            self.ai_snake.next_direction = (-1, 0)
        else:
            self.ai_snake = None
            
        self.food = self.spawn_food()
        self.score = 0
        self.ai_score = 0
        self.game_speed = INITIAL_SPEED
        self.last_move_time = pygame.time.get_ticks()
        self.ai_last_move_time = pygame.time.get_ticks()

    def spawn_food(self):
        while True:
            pos = (
                random.randrange(0, WIDTH, CELL_SIZE),
                random.randrange(0, HEIGHT, CELL_SIZE)
            )
            # Don't spawn on obstacles or snakes
            collision_points = set(self.obstacles)
            if self.player: collision_points |= set(self.player.body)
            if self.ai_snake: collision_points |= set(self.ai_snake.body)
            
            if pos not in collision_points:
                return pos

    def add_particles(self, pos, color):
        for _ in range(10):
            self.particles.append({
                "pos": list(pos),
                "vel": [random.uniform(-2, 2), random.uniform(-2, 2)],
                "life": 1.0,
                "color": color
            })

    def update_particles(self):
        for p in self.particles[:]:
            p["pos"][0] += p["vel"][0]
            p["pos"][1] += p["vel"][1]
            p["life"] -= 0.02
            if p["life"] <= 0:
                self.particles.remove(p)

    def draw_particles(self):
        for p in self.particles:
            alpha = int(p["life"] * 255)
            # Create a surf for transparency
            s = pygame.Surface((4, 4))
            s.set_alpha(alpha)
            s.fill(p["color"])
            screen.blit(s, p["pos"])

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == MENU:
                    if self.btn_ai.hovered:
                        self.start_game(PLAYING_AI)
                    elif self.btn_classic.hovered:
                        self.start_game(PLAYING_CLASSIC)
                elif self.state == GAME_OVER:
                    self.state = MENU

            if self.state != MENU:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = MENU

    def update(self):
        current_time = pygame.time.get_ticks()
        
        if self.state == MENU:
            self.btn_ai.update(pygame.mouse.get_pos())
            self.btn_classic.update(pygame.mouse.get_pos())
            
        elif self.state in [PLAYING_AI, PLAYING_CLASSIC]:
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
            
            # Speed scaling logic
            move_delay = 1000 / self.game_speed
            
            # Update Player
            if current_time - self.last_move_time >= move_delay:
                self.player.move()
                self.last_move_time = current_time
                
                # Check player collisions
                if self.player.check_collision(WIDTH, HEIGHT, self.obstacles, self.ai_snake):
                    self.state = GAME_OVER
                
                # Check food
                if self.player.body[0] == self.food:
                    self.player.grow = True
                    self.add_particles(self.food, FOOD_COLOR)
                    self.food = self.spawn_food()
                    self.score += 10
                    # Increase speed
                    self.game_speed = min(MAX_SPEED, self.game_speed + SPEED_INCREMENT)

            # Update AI
            if self.state == PLAYING_AI:
                ai_move_delay = move_delay / AI_SPEED_MULTIPLIER # Slower than player
                if current_time - self.ai_last_move_time >= ai_move_delay:
                    ai_move(self.ai_snake, self.food, self.obstacles, self.player.body)
                    self.ai_snake.move()
                    self.ai_last_move_time = current_time
                    
                    if self.ai_snake.check_collision(WIDTH, HEIGHT, self.obstacles, self.player):
                        # AI died, give player points or just reset AI? User wants a match.
                        # For now, if AI dies, game continues or game over? 
                        # Let's say if AI dies, player wins a bonus and AI respawns.
                        self.add_particles(self.ai_snake.body[0], AI_COLOR)
                        self.ai_snake = Snake(WIDTH - 200, HEIGHT//2, AI_COLOR, AI_TAIL, is_ai=True)
                        self.score += 50
                    
                    if self.ai_snake.body[0] == self.food:
                        self.ai_snake.grow = True
                        self.add_particles(self.food, FOOD_COLOR)
                        self.food = self.spawn_food()
                        self.ai_score += 10

        self.update_particles()

    def draw_grid(self):
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

    def draw(self, current_time):
        screen.fill(BG_COLOR)
        
        if self.state == MENU:
            if self.menu_bg:
                screen.blit(self.menu_bg, (0, 0))
                if self.overlay:
                    screen.blit(self.overlay, (0, 0))
            else:
                screen.fill(BG_COLOR)

            # Animated title
            y_offset = math.sin(current_time * 0.005) * 15
            
            # Shadow/Glow for title text for better visibility over image
            draw_text("Artificial Snake", font_title, (0, 0, 0), (WIDTH//2 + 4, HEIGHT//4 + y_offset + 4))
            draw_text("Artificial Snake", font_title, UI_ACCENT, (WIDTH//2, HEIGHT//4 + y_offset))


            self.btn_ai.draw(screen)
            self.btn_classic.draw(screen)
            
        elif self.state in [PLAYING_AI, PLAYING_CLASSIC]:
            self.draw_grid()
            
            # Obstacles
            for obs in self.obstacles:
                pygame.draw.rect(screen, OBSTACLE_COLOR, (obs[0]+2, obs[1]+2, CELL_SIZE-4, CELL_SIZE-4), border_radius=5)
                # Small glow
                pygame.draw.rect(screen, (50, 50, 50), (obs[0], obs[1], CELL_SIZE, CELL_SIZE), 1, border_radius=5)
            
            # Food with pulsing animation
            pulse = (math.sin(current_time * 0.01) + 1) / 2
            f_size = 10 + pulse * 8
            pygame.draw.circle(screen, FOOD_COLOR, (self.food[0] + CELL_SIZE//2, self.food[1] + CELL_SIZE//2), f_size)
            # Food glow
            pygame.draw.circle(screen, (255, 255, 0), (self.food[0] + CELL_SIZE//2, self.food[1] + CELL_SIZE//2), f_size + 4, 1)
            
            # Snakes
            if self.ai_snake:
                self.ai_snake.draw(screen, current_time)
            self.player.draw(screen, current_time)
            
            # Particles
            self.draw_particles()
            
            # HUD
            if self.state == PLAYING_AI:
                draw_text(f"YOU: {self.score}", font_hud, PLAYER_COLOR, (100, 30))
                draw_text(f"AI: {self.ai_score}", font_hud, AI_COLOR, (WIDTH - 100, 30))
                draw_text("VS AI MODE", font_hud, UI_SECONDARY, (WIDTH//2, 30))
            else:
                draw_text(f"SCORE: {self.score}", font_hud, WHITE, (100, 30))
                draw_text("CLASSIC MODE", font_hud, UI_SECONDARY, (WIDTH//2, 30))
            
            draw_text(f"SPEED: {int(self.game_speed)}", font_hud, WHITE, (WIDTH//2, HEIGHT - 30))
                
        elif self.state == GAME_OVER:
            draw_text("GAME OVER", font_title, UI_SECONDARY, (WIDTH//2, HEIGHT//2 - 80))
            draw_text(f"YOUR SCORE: {self.score}", font_menu, PLAYER_COLOR, (WIDTH//2, HEIGHT//2))
            if self.ai_snake:
                draw_text(f"AI SCORE: {self.ai_score}", font_menu, AI_COLOR, (WIDTH//2, HEIGHT//2 + 50))
            draw_text("CLICK ANYWHERE FOR MENU", font_hud, GRAY, (WIDTH//2, HEIGHT//2 + 120))

        pygame.display.flip()

# ========== MAIN LOOP ==========
game = Game()
while True:
    game.handle_events()
    game.update()
    game.draw(pygame.time.get_ticks())
    clock.tick(FPS)
