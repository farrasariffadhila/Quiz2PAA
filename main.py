import random
import os
from collections import deque

# Ukuran labirin
ROWS, COLS = 11, 21  # Ukuran kecil agar lebih nyaman di terminal

# Simbol
WALL = '#'
PATH = ' '
PLAYER = 'P'
GOAL = 'G'
TRAP = 'T'
UNKNOWN = ' '

# Clear terminal
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Generate labirin dengan DFS
def generate_maze():
    maze = [[WALL for _ in range(COLS)] for _ in range(ROWS)]

    def carve(x, y):
        dirs = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 1 <= nx < ROWS-1 and 1 <= ny < COLS-1 and maze[nx][ny] == WALL:
                maze[nx][ny] = PATH
                maze[x + dx//2][y + dy//2] = PATH
                carve(nx, ny)

    maze[1][1] = PATH
    carve(1, 1)
    return maze

# Tempatkan goal secara acak
def place_goal(maze):
    while True:
        r, c = random.randint(1, ROWS-2), random.randint(1, COLS-2)
        if maze[r][c] == PATH:
            maze[r][c] = GOAL
            return r, c

# Tempatkan jebakan secara aman (masih ada jalan ke goal)
def place_traps_safe(maze, count, start, goal):
    while True:
        traps = set()
        candidates = [(r, c) for r in range(1, ROWS-1) for c in range(1, COLS-1)
                      if maze[r][c] == PATH and (r, c) != start and (r, c) != goal]
        traps = set(random.sample(candidates, count))
        if bfs(maze, traps, start, goal):
            return traps

# Print labirin
def print_maze(maze, player, traps, reveal=False):
    for r in range(ROWS):
        line = ''
        for c in range(COLS):
            if (r, c) == player:
                line += PLAYER
            elif maze[r][c] == GOAL:
                line += GOAL
            elif (r, c) in traps and reveal:
                line += TRAP
            elif (r, c) in traps:
                line += UNKNOWN
            else:
                line += maze[r][c]
        print(line)

# BFS untuk hint
def bfs(maze, traps, start, goal):
    queue = deque([(start, [])])
    visited = set()
    while queue:
        (r, c), path = queue.popleft()
        if (r, c) in visited or (r, c) in traps:
            continue
        visited.add((r, c))
        if (r, c) == goal:
            return path
        for dr, dc, move in [(-1,0,'up'), (1,0,'down'), (0,-1,'left'), (0,1,'right')]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] != WALL:
                queue.append(((nr, nc), path + [move]))
    return None

# Game utama
def main():
    maze = generate_maze()
    start = (1, 1)
    goal = place_goal(maze)
    traps = place_traps_safe(maze, 3, start, goal)
    player = start
    has_second_chance = True  # kesempatan hidup sekali

    while True:
        clear()
        print_maze(maze, player, traps)
        print(f"\nSecond Chance: {'AVAILABLE' if has_second_chance else 'USED'}")
        print("Controls: w/a/s/d to move, 'hint' for BFS suggestion, 'quit' to exit")
        cmd = input("Your move: ").strip().lower()

        if cmd == 'quit':
            print("Thanks for playing!")
            break
        elif cmd == 'hint':
            path = bfs(maze, traps, player, goal)
            if path:
                print(f"HINT: Move {path[0]}")
            else:
                print("No safe path found!")
            input("Press Enter...")
            continue

        move_map = {'w': (-1, 0), 's': (1, 0), 'a': (0, -1), 'd': (0, 1)}
        if cmd in move_map:
            dr, dc = move_map[cmd]
            nr, nc = player[0] + dr, player[1] + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] != WALL:
                player = (nr, nc)

            if player in traps:
                clear()
                if has_second_chance:
                    has_second_chance = False
                    traps.remove(player)
                    print_maze(maze, player, traps, reveal=True)
                    print("\n⚠️ You stepped on a TRAP... but you survived thanks to your second chance!")
                    input("Press Enter to continue...")
                else:
                    print_maze(maze, player, traps, reveal=True)
                    print("\n💥 You stepped on a TRAP! Game Over!")
                    break
            elif maze[player[0]][player[1]] == GOAL:
                clear()
                print_maze(maze, player, traps, reveal=True)
                print("\n🎉 Congratulations! You reached the GOAL!")
                break
        else:
            print("Invalid input!")
            input("Press Enter...")

if __name__ == '__main__':
    main()
