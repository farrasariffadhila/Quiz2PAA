import random
from collections import deque
import heapq

ROWS, COLS = 11, 21
WALL = '#'
PATH = ' '
GOAL = 'E'
TRAP = 'T'


def generate_maze(r_max, c_max):
    maze = [[WALL for _ in range(c_max)] for _ in range(r_max)]

    def carve(x, y):
        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            wall_x, wall_y = x + dx, y + dy
            next_x, next_y = x + 2 * dx, y + 2 * dy
            if 0 < next_x < r_max - 1 and 0 < next_y < c_max - 1 and maze[next_x][next_y] == WALL:
                maze[wall_x][wall_y] = PATH
                maze[next_x][next_y] = PATH
                carve(next_x, next_y)

    maze[1][1] = PATH
    carve(1, 1)
    return maze


def place_goal(maze_layout, start_pos_tuple, r_max, c_max):
    possible_goal_positions = []
    for r in range(r_max // 2, r_max - 1):
        for c in range(c_max // 2, c_max - 1):
            if maze_layout[r][c] == PATH and (r, c) != start_pos_tuple:
                possible_goal_positions.append((r, c))
    if not possible_goal_positions:
        for r in range(1, r_max - 1):
            for c in range(1, c_max - 1):
                if maze_layout[r][c] == PATH and (r, c) != start_pos_tuple:
                    possible_goal_positions.append((r, c))
    if not possible_goal_positions:
        default_goal_r, default_goal_c = r_max - 2, c_max - 2
        maze_layout[default_goal_r][default_goal_c] = GOAL
        return (default_goal_r, default_goal_c)
    chosen_goal = random.choice(possible_goal_positions)
    maze_layout[chosen_goal[0]][chosen_goal[1]] = GOAL
    return chosen_goal


def _get_valid_neighbors_for_pathfinding(position, maze_layout, existing_obstacles, r_max, c_max):
    row, col = position
    possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    valid_neighbors = []
    for dr, dc in possible_moves:
        nr, nc = row + dr, col + dc
        if 0 <= nr < r_max and 0 <= nc < c_max and \
           maze_layout[nr][nc] != WALL and \
           (nr, nc) not in existing_obstacles:
            valid_neighbors.append((nr, nc))
    return valid_neighbors


def _reconstruct_path_from_came_from(came_from, start_pos, goal_pos):
    path = []
    current = goal_pos
    if current == start_pos:
        return []
    if current not in came_from:
        return None

    while current != start_pos:
        path.append(current)
        if current not in came_from:
             return None 
        current = came_from[current]
    return path[::-1]


def dfs_pathfinding(maze_layout, start_pos, goal_pos, existing_obstacles, r_max, c_max):
    stack = [(start_pos, [start_pos])]
    visited = {start_pos}
    while stack:
        current_p, path_list = stack.pop()
        if current_p == goal_pos:
            return path_list[1:]
        neighbors = _get_valid_neighbors_for_pathfinding(current_p, maze_layout, existing_obstacles, r_max, c_max)
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path_list)
                new_path.append(neighbor)
                stack.append((neighbor, new_path))
    return None


def bfs_pathfinding(maze_layout, start_pos, goal_pos, existing_obstacles, r_max, c_max):
    queue = deque([start_pos])
    visited = {start_pos}
    came_from = {}
    path_found = False
    while queue:
        current_p = queue.popleft()
        if current_p == goal_pos:
            path_found = True
            break
        for neighbor in _get_valid_neighbors_for_pathfinding(current_p, maze_layout, existing_obstacles, r_max, c_max):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current_p
                queue.append(neighbor)
    if path_found:
        return _reconstruct_path_from_came_from(came_from, start_pos, goal_pos)
    return None


def dijkstra_pathfinding(maze_layout, start_pos, goal_pos, existing_obstacles, r_max, c_max):
    pq = [(0, start_pos)]
    distances = {start_pos: 0}
    came_from = {}
    path_found = False
    while pq:
        dist, current_p = heapq.heappop(pq)
        if current_p == goal_pos:
            path_found = True
            break
        if dist > distances.get(current_p, float('inf')):
            continue
        for neighbor in _get_valid_neighbors_for_pathfinding(current_p, maze_layout, existing_obstacles, r_max, c_max):
            new_dist = dist + 1
            if new_dist < distances.get(neighbor, float('inf')):
                distances[neighbor] = new_dist
                came_from[neighbor] = current_p
                heapq.heappush(pq, (new_dist, neighbor))
    if path_found:
        return _reconstruct_path_from_came_from(came_from, start_pos, goal_pos)
    return None


def bfs_for_validation(maze_layout, traps_to_avoid, start_pos, goal_pos, r_max, c_max):
    queue = deque([(start_pos, [])])
    visited = {start_pos}
    while queue:
        (r, c), path = queue.popleft()
        if (r, c) == goal_pos: return path
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < r_max and 0 <= nc < c_max and \
               maze_layout[nr][nc] != WALL and \
               (nr, nc) not in traps_to_avoid and \
               (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append(((nr, nc), path + [(dr,dc)]))
    return None


def place_traps_safe(maze_layout, trap_count, start_pos, goal_pos, r_max, c_max):
    placed_traps = set()
    path_cells = []
    for r in range(r_max):
        for c in range(c_max):
            if maze_layout[r][c] == PATH and (r, c) != start_pos and (r,c) != goal_pos:
                path_cells.append((r,c))
    random.shuffle(path_cells)
    for _ in range(trap_count):
        if not path_cells: break
        trap_candidate_placed = False
        for i in range(len(path_cells) -1, -1, -1):
            trap_candidate = path_cells.pop(i)
            current_potential_traps = placed_traps.copy()
            current_potential_traps.add(trap_candidate)
            if bfs_for_validation(maze_layout, current_potential_traps, start_pos, goal_pos, r_max, c_max):
                placed_traps.add(trap_candidate)
                trap_candidate_placed = True
                break
        if not trap_candidate_placed: pass
    return placed_traps


def heuristic(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
def a_star_search(maze_layout, start_pos, goal_pos, existing_obstacles, r_max, c_max):
    open_set = []; heapq.heappush(open_set, (0, start_pos))
    came_from = {}; g_score = { (r,c): float('inf') for r in range(r_max) for c in range(c_max) }
    g_score[start_pos] = 0; f_score = { (r,c): float('inf') for r in range(r_max) for c in range(c_max) }
    f_score[start_pos] = heuristic(start_pos, goal_pos); open_set_hash = {start_pos}
    while open_set:
        _, current_p = heapq.heappop(open_set); open_set_hash.remove(current_p)
        if current_p == goal_pos: return _reconstruct_path_from_came_from(came_from, start_pos, goal_pos)
        for neighbor_p in _get_valid_neighbors_for_pathfinding(current_p, maze_layout, existing_obstacles, r_max, c_max):
            tentative_g_score = g_score[current_p] + 1
            if tentative_g_score < g_score[neighbor_p]:
                came_from[neighbor_p] = current_p; g_score[neighbor_p] = tentative_g_score
                f_score[neighbor_p] = tentative_g_score + heuristic(neighbor_p, goal_pos)
                if neighbor_p not in open_set_hash:
                    heapq.heappush(open_set, (f_score[neighbor_p], neighbor_p)); open_set_hash.add(neighbor_p)
    return None