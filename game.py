import os
import time
import random
import maze as mz
import player as pl

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

MAZE_ROWS = mz.ROWS
MAZE_COLS = mz.COLS

def set_trap_count(level):
    if level == 1: return 3
    if level == 2: return 5
    if level == 3: return 7
    if level == 4: return 9
    if level >= 5: return 10
    return 5

def display_loading_screen():
    clear()
    print("Loading Maze Adventure...")
    art = [
        "  M M M   A A A   ZZZZZ  EEEEE  ", "  MM MM  A     A     Z   E      ",
        "  M M M  AAAAAAA    Z    EEEEE  ", "  M   M  A     A   Z     E      ",
        "  M   M  A     A  ZZZZZ  EEEEE  "
    ]
    for line in art: print(line); time.sleep(0.2)
    print("\n" * 2 + "Get ready!"); time.sleep(2)

def draw_main_menu():
    clear(); print("=== MAZE ADVENTURE ===\n\nSelect Level:")
    levels_display = ["1. Level 1 (Easy)", "2. Level 2 (Medium)", "3. Level 3 (Hard)",
                      "4. Level 4 (Very Hard)", "5. Level 5 (Expert)"]
    for item in levels_display: print(item)
    print("\nQ. Quit Game")
    while True:
        choice = input("Enter your choice (1-5 or Q): ").strip().lower()
        if choice.isdigit() and 1 <= int(choice) <= 5: return int(choice)
        elif choice == 'q': return None
        else: print("Invalid choice.")

def get_direction_str(current_pos, next_pos):
    dr, dc = next_pos[0] - current_pos[0], next_pos[1] - current_pos[1]
    if dr == -1: return "UP"
    if dr == 1: return "DOWN"
    if dc == -1: return "LEFT"
    if dc == 1: return "RIGHT"
    return "an unknown direction"

def print_maze_state(maze_layout, player_obj, goal_pos, current_traps, reveal_traps=False, level=1):
    player_r, player_c = player_obj.get_position()
    clear(); print(f"--- MAZE - Level {level} ---")
    for r in range(MAZE_ROWS):
        line = ''
        for c in range(MAZE_COLS):
            pos = (r, c)
            if pos == (player_r, player_c): line += pl.PLAYER_SYMBOL
            elif pos == goal_pos: line += mz.GOAL
            elif pos in current_traps: line += mz.TRAP if reveal_traps else mz.PATH
            else: line += maze_layout[r][c]
            line += ' '
        print(line)
    print("-" * (MAZE_COLS * 2))
    print("Controls: W (Up), A (Left), S (Down), D (Right)")
    print("          H (Hint), Q (Quit Level)")

def play_level(current_level, game_maze, game_player, goal_position, trap_locations):
    game_over = False
    win = False
    
    while not game_over:
        print_maze_state(game_maze, game_player, goal_position, trap_locations, reveal_traps=win, level=current_level)
        if win:
            print("\n🎉 Congratulations! You reached the GOAL! 🎉")
            time.sleep(1)
            return "win"

        action = input("Your move (W/A/S/D/H/Q): ").strip().lower()

        if action == 'q': return "quit_level"
        
        elif action == 'h':
            print("\nCalculating hint using DFS, BFS, and Dijkstra...")
            player_pos = game_player.get_position()
            
            algo_paths = {} 
            
            path_dfs = mz.dfs_pathfinding(game_maze, player_pos, goal_position, trap_locations, MAZE_ROWS, MAZE_COLS)
            if path_dfs is not None: algo_paths['DFS'] = path_dfs
            
            path_bfs = mz.bfs_pathfinding(game_maze, player_pos, goal_position, trap_locations, MAZE_ROWS, MAZE_COLS)
            if path_bfs is not None: algo_paths['BFS'] = path_bfs
            
            path_dijkstra = mz.dijkstra_pathfinding(game_maze, player_pos, goal_position, trap_locations, MAZE_ROWS, MAZE_COLS)
            if path_dijkstra is not None: algo_paths['Dijkstra'] = path_dijkstra

            if not algo_paths:
                print("No path to the goal found by any algorithm. You might be trapped!")
            else:
                shortest_len = float('inf')
                candidate_algos = [] 

                for name, path in algo_paths.items():
                    p_len = len(path)
                    if p_len < shortest_len:
                        shortest_len = p_len
                        candidate_algos = [(p_len, name, path)]
                    elif p_len == shortest_len:
                        candidate_algos.append((p_len, name, path))
                
                final_best_algo_name = None
                final_best_path = None

                if candidate_algos:
                    algo_preference_order = ['BFS', 'Dijkstra', 'DFS']
                    algo_pref_map = {name: i for i, name in enumerate(algo_preference_order)}
                    
                    candidate_algos.sort(key=lambda x: algo_pref_map.get(x[1], 99))
                    
                    final_best_algo_name = candidate_algos[0][1]
                    final_best_path = candidate_algos[0][2]
                
                if shortest_len == 0 : 
                     print("You are already at the goal!")
                elif final_best_path and len(final_best_path) > 0: 
                    next_step = final_best_path[0]
                    direction = get_direction_str(player_pos, next_step)
                    print(f"HINT (via {final_best_algo_name}, length {shortest_len}): Try moving {direction}.")
                else: 
                    print("No clear hint available or you are trapped.")

            input("Press Enter to continue...")
            continue

        move_map = {'w': (-1, 0), 's': (1, 0), 'a': (0, -1), 'd': (0, 1)}
        if action in move_map:
            dr, dc = move_map[action]
            curr_r, curr_c = game_player.get_position()
            next_r, next_c = curr_r + dr, curr_c + dc

            if 0 <= next_r < MAZE_ROWS and 0 <= next_c < MAZE_COLS and \
               game_maze[next_r][next_c] != mz.WALL:
                game_player.set_position(next_r, next_c)
                player_new_pos = game_player.get_position()

                if player_new_pos == goal_position:
                    win = True; continue
                if player_new_pos in trap_locations:
                    print_maze_state(game_maze, game_player, goal_position, trap_locations, reveal_traps=True, level=current_level)
                    print("\n💥 Oh no! You stepped on a TRAP! Game Over. 💥")
                    time.sleep(1); game_over = True; return "lose"
            else:
                print("You can't move there!"); input("Press Enter to continue...")
        else:
            print("Invalid input."); input("Press Enter to continue...")
    return "error" 

def display_play_again_prompt(won_level):
    prompt = "Play Next Level? (y/n): " if won_level else "Play Again? (y/n): "
    while True:
        choice = input(prompt).strip().lower()
        if choice == 'y': return True
        elif choice == 'n': return False
        else: print("Invalid input.")

def main():
    display_loading_screen()
    current_level = 0; keep_playing = True
    while keep_playing:
        if current_level == 0:
            chosen_level = draw_main_menu()
            if chosen_level is None: keep_playing = False; break
            current_level = chosen_level
        
        num_traps = set_trap_count(current_level)
        print(f"\nGenerating Level {current_level} with {num_traps} traps..."); time.sleep(0.5)
        
        maze_layout = mz.generate_maze(MAZE_ROWS, MAZE_COLS)
        player_obj = pl.Player(1, 1); maze_layout[1][1] = mz.PATH
        goal_coords = mz.place_goal(maze_layout, player_obj.get_position(), MAZE_ROWS, MAZE_COLS)
        traps = mz.place_traps_safe(maze_layout, num_traps, player_obj.get_position(), goal_coords, MAZE_ROWS, MAZE_COLS)
        
        level_outcome = play_level(current_level, maze_layout, player_obj, goal_coords, traps)

        if level_outcome == "win":
            if not display_play_again_prompt(True): keep_playing = False
            else:
                current_level += 1
                if current_level > 5: print("All levels beaten! Resetting."); current_level = 0
        elif level_outcome == "lose":
            if not display_play_again_prompt(False): keep_playing = False
        elif level_outcome == "quit_level":
            print("Returning to Main Menu..."); current_level = 0; time.sleep(1)
        
        if current_level == 0 and keep_playing: print("Loading Main Menu..."); time.sleep(1)

    clear(); print("Thanks for playing Maze Adventure!")

if __name__ == '__main__':
    main()