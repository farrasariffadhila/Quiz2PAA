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
RED = (255, 0, 0)
GREEN = (0, 255, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Adventure")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", FONT_SIZE)

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

def flash_screen(color=YELLOW, flashes=3, delay=100):
    original_screen = screen.copy()
    for _ in range(flashes):
        screen.fill(color)
        pygame.display.flip()
        pygame.time.delay(delay)
        screen.blit(original_screen, (0,0))
        pygame.display.flip()
        pygame.time.delay(delay)

def draw_popup_card(lines, width=400, height=120, bgcolor=(240, 240, 240), border_color=BLACK):
    x = (WIDTH - width) // 2
    y = (HEIGHT - height) // 2
    rect = pygame.Rect(x, y, width, height)
    popup_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    popup_surface.fill((*bgcolor, 230))
    screen.blit(popup_surface, (x,y))
    pygame.draw.rect(screen, border_color, rect, 2)
    for i, line in enumerate(lines):
        text = font.render(line, True, BLACK)
        text_rect = text.get_rect(center=(WIDTH // 2, y + 25 + i * 25))
        screen.blit(text, text_rect)

def draw_maze(maze_data, player_obj, goal_pos, trap_list, reveal_traps=False):
    screen.blit(bg_game, (0, 0))
    info_area_surface = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
    info_area_surface.fill((255, 255, 255, 180))
    screen.blit(info_area_surface, (0,0))
    for r in range(ROWS):
        for c in range(COLS):
            x, y = c * TILE_SIZE, r * TILE_SIZE + 80
            pos = (r, c)
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            if maze_data[r][c] == mz.WALL:
                screen.blit(wall_img, rect)
            else:
                if pos == goal_pos:
                    screen.blit(goal_img, rect)
                if reveal_traps and pos in trap_list:
                    screen.blit(trap_img, rect)
                if pos == player_obj.get_position():
                    screen.blit(player_img, rect)
    info = f"Level {current_level} | Arrows: Move | H: Hint | Q: Quit"
    screen.blit(font.render(info, True, BLACK), (10, 10))
    if hint_text:
        screen.blit(font.render(hint_text, True, BLACK), (10, 35))

def move_player(maze_data, player_obj, dr, dc):
    global hint_text
    r, c = player_obj.get_position()
    nr, nc = r + dr, c + dc
    if 0 <= nr < ROWS and 0 <= nc < COLS and maze_data[nr][nc] != mz.WALL:
        player_obj.set_position(nr, nc)
        hint_text = ""

def show_hint(maze_data, trap_list, player_obj, goal_pos):
    global hint_text
    import time
    pos = player_obj.get_position()
    algorithms = ["BFS", "Dijkstra", "DFS"]
    paths = {}
    times = {}
    for name in algorithms:
        path_finding_func = getattr(mz, f"{name.lower()}_pathfinding")
        start_time = time.perf_counter()
        path = path_finding_func(maze_data, pos, goal_pos, trap_list, ROWS, COLS)
        elapsed = (time.perf_counter() - start_time) * 1000  # ms
        if path:
            paths[name] = path
        times[name] = elapsed
    if not paths:
        hint_text = "Hint: No path found (traps might block)."
        return
    best_overall = sorted(paths.items(), key=lambda x: len(x[1]))
    chosen_algo_name = None
    chosen_path = None
    for name in ["BFS", "Dijkstra"]:
        if name in dict(best_overall):
            chosen_algo_name = name
            chosen_path = dict(best_overall)[name]
            break
    if not chosen_algo_name:
        chosen_algo_name, chosen_path = best_overall[0]
    if chosen_path:
        direction = get_direction_str(pos, chosen_path[0])
        hint_text = f"Hint ({chosen_algo_name}): move {direction} | "
        hint_text += " | ".join([f"{algo}: {times[algo]:.2f}ms" for algo in algorithms])
    else:
        hint_text = "Hint: No path found."

def play_level(level):
    global hint_text, current_level
    current_level = level
    maze = mz.generate_maze(ROWS, COLS)
    player = pl.Player(1, 1)
    goal = mz.place_goal(maze, player.get_position(), ROWS, COLS)
    traps = mz.place_traps_safe(maze, set_trap_count(level), player.get_position(), goal, ROWS, COLS)
    win = False
    dead = False
    running_level = True
    while running_level:
        draw_maze(maze, player, goal, traps, reveal_traps=(win or dead))
        if win:
            draw_popup_card([
                "You win!",
                "Press N for next level,",
                "R to replay,",
                "M for menu."
            ], height=140)
        elif dead:
            draw_popup_card([
                "You died!",
                "Press R to Restart Level,",
                "M for Main Menu."
            ], height=120)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if win:
                    if event.key == pygame.K_r:
                        return "replay"
                    elif event.key == pygame.K_m:
                        return "menu"
                    elif event.key == pygame.K_n:
                        return "next"
                elif dead:
                    if event.key == pygame.K_r:
                        return "replay"
                    elif event.key == pygame.K_m:
                        return "menu"
                else:
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
        if not win and not dead:
            if player.get_position() in traps:
                flash_screen(RED)
                dead = True
                hint_text = ""
            if player.get_position() == goal:
                flash_screen(GREEN)
                win = True
                hint_text = ""
        clock.tick(10)

def show_level_menu():
    global current_level
    selected = current_level - 1
    selecting = True
    while selecting:
        screen.blit(bg_img, (0, 0))
        card_width, card_height = 500, 370
        card_x = (WIDTH - card_width) // 2
        card_y = (HEIGHT - card_height) // 2
        card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        card_surface.fill((255, 255, 255, 200))
        screen.blit(card_surface, (card_x, card_y))
        title_text = font.render("Select Level 1-5 (arrow keys + Enter) | Q to Quit", True, BLACK)
        title_rect = title_text.get_rect(center=(WIDTH // 2, card_y + 40))
        screen.blit(title_text, title_rect)
        for i in range(1, max_level + 1):
            y_pos = card_y + 80 + (i-1) * 50
            level_text = f"Level {i}"
            text_surf = font.render(level_text, True, BLACK)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, y_pos))
            if selected == i - 1:
                box_rect = pygame.Rect(text_rect.x - 12, text_rect.y - 8,
                                       text_rect.width + 24, text_rect.height + 16)
                pygame.draw.rect(screen, YELLOW, box_rect, border_radius=8)
            screen.blit(text_surf, text_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % max_level
                elif event.key == pygame.K_UP:
                    selected = (selected - 1 + max_level) % max_level
                elif event.key == pygame.K_RETURN:
                    current_level = selected + 1
                    selecting = False
                    return

def main():
    global current_level
    while True:
        show_level_menu()
        running_game = True
        while running_game:
            outcome = play_level(current_level)
            if outcome == "next":
                current_level += 1
                if current_level > max_level:
                    print("Congratulations! You've completed all levels!")
                    current_level = 1
                    running_game = False
            elif outcome == "replay":
                continue
            elif outcome == "menu":
                running_game = False
            else:
                print(f"Unknown outcome: {outcome}, returning to menu.")
                running_game = False

if __name__ == '__main__':
    main()