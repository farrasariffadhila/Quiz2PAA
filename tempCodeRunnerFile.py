import pygame
import sys
import maze as mz
import player as pl
import random
import time

TILE_SIZE = 60
ROWS, COLS = mz.ROWS, mz.COLS
WIDTH, HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE + 80
FONT_SIZE = 20

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Adventure")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", FONT_SIZE)

# Load images
try:
    player_img = pygame.image.load("assets/player.png")
    wall_img = pygame.image.load("assets/maze.png")
    trap_img = pygame.image.load("assets/trap.png")
    goal_img = pygame.image.load("assets/goal.png")
    bg_img = pygame.image.load("assets/background_menu.jpeg")
    bg_game = pygame.image.load("assets/background_game.jpg")
except Exception as e:
    print("Error loading images:", e)
    pygame.quit()
    sys.exit()

player_img = pygame.transform.scale(player_img, (TILE_SIZE, TILE_SIZE))
wall_img = pygame.transform.scale(wall_img, (TILE_SIZE, TILE_SIZE))
trap_img = pygame.transform.scale(trap_img, (TILE_SIZE, TILE_SIZE))
goal_img = pygame.transform.scale(goal_img, (TILE_SIZE, TILE_SIZE))
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
bg_game = pygame.transform.scale(bg_game, (WIDTH, HEIGHT))


hint_text = ""
current_level = 1
max_level = 5

def set_trap_count(level):
    return min(3 + (level - 1) * 2, 10)

def get_direction_str(curr, nxt):
    dr, dc = nxt[0] - curr[0], nxt[1] - curr[1]
    if dr == -1: return "UP"
    if dr == 1: return "DOWN"
    if dc == -1: return "LEFT"
    if dc == 1: return "RIGHT"
    return "UNKNOWN"

def flash_screen(color=(255, 255, 0), flashes=3, delay=100):
    for _ in range(flashes):
        screen.fill(color)
        pygame.display.flip()
        pygame.time.delay(delay)
        screen.fill(WHITE)
        pygame.display.flip()
        pygame.time.delay(delay)

def draw_popup_card(lines, width=400, height=120, bgcolor=(240, 240, 240), border_color=BLACK):
    x = (WIDTH - width) // 2
    y = (HEIGHT - height) // 2
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, bgcolor, rect)
    pygame.draw.rect(screen, border_color, rect, 2)

    for i, line in enumerate(lines):
        text = font.render(line, True, BLACK)
        text_rect = text.get_rect(center=(WIDTH // 2, y + 25 + i * 25))
        screen.blit(text, text_rect)

def draw_maze(maze, player, goal, traps, reveal_traps=False):
    screen.blit(bg_game, (0, 0))
    for r in range(ROWS):
        for c in range(COLS):
            x, y = c * TILE_SIZE, r * TILE_SIZE + 80
            pos = (r, c)
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

            if maze[r][c] == mz.WALL:
                screen.blit(wall_img, rect)
            else:
                pygame.draw.rect(screen, (255, 255, 255, 180), pygame.Rect(0, 0, WIDTH, 80))
                if pos == goal:
                    screen.blit(goal_img, rect)
                if reveal_traps and pos in traps:
                    screen.blit(trap_img, rect)
                if pos == player.get_position():
                    screen.blit(player_img, rect)

    info = f"Level {current_level} | Arrows: Move | H: Hint | Q: Quit"
    screen.blit(font.render(info, True, BLACK), (10, 10))
    if hint_text:
        screen.blit(font.render(hint_text, True, BLACK), (10, 35))

def move_player(maze, player, dr, dc):
    global hint_text
    r, c = player.get_position()
    nr, nc = r + dr, c + dc
    if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] != mz.WALL:
        player.set_position(nr, nc)
        hint_text = ""

def show_hint(maze, traps, player, goal):
    global hint_text
    pos = player.get_position()
    algorithms = ["BFS", "Dijkstra", "DFS"]
    paths = {}
    for name in algorithms:
        path = getattr(mz, f"{name.lower()}_pathfinding")(maze, pos, goal, traps, ROWS, COLS)
        if path:
            paths[name] = path
    if not paths:
        hint_text = "No path found."
        return
    best = sorted(paths.items(), key=lambda x: len(x[1]))
    for name in ["BFS", "Dijkstra", "DFS"]:
        if name in dict(best):
            best_name = name
            best_path = dict(best)[name]
            break
    direction = get_direction_str(pos, best_path[0])
    hint_text = f"Hint ({best_name}): move {direction}"

def play_level(level):
    global hint_text, current_level
    maze = mz.generate_maze(ROWS, COLS)
    player = pl.Player(1, 1)
    goal = mz.place_goal(maze, player.get_position(), ROWS, COLS)
    traps = mz.place_traps_safe(maze, set_trap_count(level), player.get_position(), goal, ROWS, COLS)
    win = False

    while True:
        draw_maze(maze, player, goal, traps, reveal_traps=win)
        if win:
            draw_popup_card([
                "You win!",
                "Press N for next level,",
                "R to replay,",
                "M for menu."
            ])
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()
                if not win:
                    if event.key == pygame.K_h:
                        show_hint(maze, traps, player, goal)
                    elif event.key == pygame.K_UP:
                        move_player(maze, player, -1, 0)
                    elif event.key == pygame.K_DOWN:
                        move_player(maze, player, 1, 0)
                    elif event.key == pygame.K_LEFT:
                        move_player(maze, player, 0, -1)
                    elif event.key == pygame.K_RIGHT:
                        move_player(maze, player, 0, 1)
                else:
                    if event.key == pygame.K_r:
                        return "replay"
                    elif event.key == pygame.K_m:
                        return "menu"
                    elif event.key == pygame.K_n:
                        return "next"

        if not win:
            if player.get_position() in traps:
                flash_screen((255, 0, 0))
                draw_maze(maze, player, goal, traps, reveal_traps=True)
                pygame.display.flip()
                time.sleep(2)
                return "lose"
            if player.get_position() == goal:
                flash_screen((0, 255, 0))
                win = True
                hint_text = ""
        clock.tick(10)

def show_level_menu():
    global current_level
    selected = 0
    selecting = True
    while selecting:
        screen.blit(bg_img, (0, 0))

        # Gambar card semi-transparan
        card_width, card_height = 500, 370
        card_x = (WIDTH - card_width) // 2
        card_y = (HEIGHT - card_height) // 2
        card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        card_surface.fill((255, 255, 255, 200))  # RGBA: white with alpha
        screen.blit(card_surface, (card_x, card_y))

        # Judul menu
        title_text = font.render("Select Level 1-5 (arrow keys + Enter) | Q to Quit", True, BLACK)
        title_rect = title_text.get_rect(center=(WIDTH // 2, card_y + 40))
        screen.blit(title_text, title_rect)

        # Opsi level
        for i in range(1, 6):
            y = card_y + 80 + i * 50
            level_text = f"Level {i}"
            text_surf = font.render(level_text, True, BLACK)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, y))

            if selected == i - 1:
                box_rect = pygame.Rect(text_rect.x - 12, text_rect.y - 8,
                                       text_rect.width + 24, text_rect.height + 16)
                pygame.draw.rect(screen, YELLOW, box_rect, border_radius=8)

            screen.blit(text_surf, text_rect)

        pygame.display.flip()

        # Event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % 5
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % 5
                elif event.key == pygame.K_RETURN:
                    current_level = selected + 1
                    selecting = False



def main():
    global current_level
    show_level_menu()
    while True:
        outcome = play_level(current_level)
        if outcome == "next":
            current_level += 1
            if current_level > max_level:
                show_level_menu()
        elif outcome == "win":
            pass  
        elif outcome == "lose":
            show_level_menu()
        elif outcome == "replay":
            continue
        elif outcome == "menu":
            show_level_menu()

if __name__ == '__main__':
    main()