# maze.py
import random
from collections import deque

# Ukuran labirin (Maze dimensions)
ROWS, COLS = 11, 21

# Simbol (Symbols)
WALL = '#'
PATH = ' '
GOAL = 'G'
TRAP = 'T'
UNKNOWN = ' '  # Symbol for hidden trap, can be same as PATH if not revealed

# Generate labirin dengan DFS (Generate maze with DFS)
def generate_maze():
    maze = [[WALL for _ in range(COLS)] for _ in range(ROWS)]

    def carve(x, y):
        dirs = [(0, 2), (2, 0), (0, -2), (-2, 0)] # (dx, dy) for carving two cells away
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            # Check if the new position (nx, ny) is within bounds and is a wall
            if 1 <= nx < ROWS - 1 and 1 <= ny < COLS - 1 and maze[nx][ny] == WALL:
                maze[nx][ny] = PATH  # Carve path to new cell
                maze[x + dx // 2][y + dy // 2] = PATH  # Carve path in the wall between current and new cell
                carve(nx, ny)

    # Start carving from (1,1)
    maze[1][1] = PATH
    carve(1, 1)
    return maze

# Tempatkan goal secara acak (Place goal randomly)
def place_goal(maze_layout):
    while True:
        r, c = random.randint(1, ROWS - 2), random.randint(1, COLS - 2)
        if maze_layout[r][c] == PATH:
            maze_layout[r][c] = GOAL
            return r, c

# BFS untuk hint dan validasi penempatan jebakan (BFS for hints and trap placement validation)
def bfs(maze_layout, traps_to_avoid, start_pos, goal_pos):
    queue = deque([(start_pos, [])]) # Each item: (current_position, path_taken_so_far)
    visited = set()
    while queue:
        (r, c), path = queue.popleft()

        if (r, c) in visited or (r, c) in traps_to_avoid:
            continue
        visited.add((r, c))

        if (r, c) == goal_pos:
            return path # Return the list of moves

        # Explore neighbors: up, down, left, right
        # Moves are 'up', 'down', 'left', 'right'
        for dr, dc, move_name in [(-1, 0, 'up'), (1, 0, 'down'), (0, -1, 'left'), (0, 1, 'right')]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze_layout[nr][nc] != WALL:
                queue.append(((nr, nc), path + [move_name]))
    return None # No path found

# Tempatkan jebakan secara aman (masih ada jalan ke goal)
# (Place traps safely, ensuring a path to the goal still exists)
def place_traps_safe(maze_layout, trap_count, start_pos, goal_pos):
    placed_traps = set()
    for _ in range(trap_count): # Attempt to place 'trap_count' traps
        # Find all possible locations for traps (must be PATH, not start, not goal, not existing trap)
        candidates = []
        for r in range(1, ROWS - 1):
            for c in range(1, COLS - 1):
                if maze_layout[r][c] == PATH and (r, c) != start_pos and (r, c) != goal_pos and (r,c) not in placed_traps:
                    candidates.append((r,c))
        
        if not candidates: # No more valid spots for traps
            break

        trap_placed_successfully = False
        random.shuffle(candidates) # Shuffle to try different candidates

        for trap_candidate in candidates:
            # Temporarily add the trap candidate to test if a path still exists
            temp_traps = placed_traps.copy()
            temp_traps.add(trap_candidate)
            if bfs(maze_layout, temp_traps, start_pos, goal_pos):
                placed_traps.add(trap_candidate)
                trap_placed_successfully = True
                break # Move to placing the next trap
        
        if not trap_placed_successfully:
            # Could not place this trap without blocking the path, try next iteration or stop if not enough traps
            # For simplicity, we'll just have fewer traps if we can't place all safely
            pass
            
    return placed_traps