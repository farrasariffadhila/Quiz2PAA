import random
from collections import deque
import heapq

ROWS, COLS = 11, 21
WALL = '#'
PATH = ' '
GOAL = 'E'


def _get_random_unvisited_neighbor(r, c, visited, r_max, c_max):
    neighbors = []
    directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
    random.shuffle(directions)
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if (0 <= nr < r_max and 0 <= nc < c_max and (nr, nc) not in visited):
            neighbors.append((nr, nc, r + dr//2, c + dc//2))
    if neighbors:
        return random.choice(neighbors)
    return None


def generate_maze(r_max, c_max):
    maze = [[WALL for _ in range(c_max)] for _ in range(r_max)]
    start = (1, 1)
    maze[start[0]][start[1]] = PATH
    stack = [start]
    visited = {start}
    while stack:
        current_r, current_c = stack[-1]
        neighbor = _get_random_unvisited_neighbor(current_r, current_c, visited, r_max, c_max)
        if neighbor:
            next_r, next_c, wall_r, wall_c = neighbor
            maze[next_r][next_c] = PATH
            maze[wall_r][wall_c] = PATH
            visited.add((next_r, next_c))
            stack.append((next_r, next_c))
        else:
            stack.pop()
    extra_connections = max(2, (r_max * c_max) // 20)
    attempts = 0
    while extra_connections > 0 and attempts < 1000:
        r = random.randint(1, r_max - 2)
        c = random.randint(1, c_max - 2)
        if maze[r][c] == WALL:
            if maze[r-1][c] == PATH and maze[r+1][c] == PATH and maze[r][c-1] == WALL and maze[r][c+1] == WALL:
                maze[r][c] = PATH
                extra_connections -= 1
            elif maze[r][c-1] == PATH and maze[r][c+1] == PATH and maze[r-1][c] == WALL and maze[r+1][c] == WALL:
                maze[r][c] = PATH
                extra_connections -= 1
        attempts += 1
    goal_pos = place_goal(maze, start, r_max, c_max)
    path = bfs_pathfinding(maze, start, goal_pos, set(), r_max, c_max)
    if path and len(path) > 2:
        return maze
    return generate_maze(r_max, c_max)


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
        if 0 <= nr < r_max and 0 <= nc < c_max and maze_layout[nr][nc] != WALL and (nr, nc) not in existing_obstacles:
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
            if 0 <= nr < r_max and 0 <= nc < c_max and maze_layout[nr][nc] != WALL and (nr, nc) not in traps_to_avoid and (nr, nc) not in visited:
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