# game.py
import os

# Import from other modules
import maze as mz
import player as pl

# Clear terminal
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Print labirin (Print maze state)
def print_maze_state(maze_layout, player_obj, current_traps, reveal_traps=False):
    player_pos = player_obj.get_position()
    for r in range(mz.ROWS):
        line = ''
        for c in range(mz.COLS):
            if (r, c) == player_pos:
                line += pl.PLAYER_SYMBOL
            elif maze_layout[r][c] == mz.GOAL: # Goal is always visible
                line += mz.GOAL
            elif (r, c) in current_traps:
                if reveal_traps:
                    line += mz.TRAP
                else:
                    # If not revealing, show as UNKNOWN (or PATH if UNKNOWN is ' ')
                    # This makes traps indistinguishable from paths unless stepped on or revealed.
                    line += mz.UNKNOWN if mz.UNKNOWN != ' ' else mz.PATH
            else:
                line += maze_layout[r][c]
        print(line)

# Game utama (Main game logic)
def main():
    # Setup maze
    maze_data = mz.generate_maze()
    
    # Player start position (typically fixed after maze generation, e.g., (1,1))
    player_start_pos = (1, 1)
    if maze_data[player_start_pos[0]][player_start_pos[1]] == mz.WALL:
        # Fallback if (1,1) somehow became a wall (should not happen with current gen_maze)
        # Find first path cell
        for r_idx in range(1, mz.ROWS -1):
            for c_idx in range(1, mz.COLS -1):
                if maze_data[r_idx][c_idx] == mz.PATH:
                    player_start_pos = (r_idx, c_idx)
                    break
            if maze_data[player_start_pos[0]][player_start_pos[1]] == mz.PATH:
                break
    maze_data[player_start_pos[0]][player_start_pos[1]] = mz.PATH # Ensure start is path, not goal/trap


    goal_pos = mz.place_goal(maze_data)
    
    num_traps_to_place = 3
    traps_set = mz.place_traps_safe(maze_data, num_traps_to_place, player_start_pos, goal_pos)

    # Setup player
    game_player = pl.Player(player_start_pos[0], player_start_pos[1])

    game_over_message = ""

    while True:
        clear()
        # Reveal traps if game is over (won or lost on trap without second chance)
        reveal_all_traps = bool(game_over_message) 
        print_maze_state(maze_data, game_player, traps_set, reveal_traps=reveal_all_traps)
        
        if game_over_message:
            print(game_over_message)
            break

        print(f"\nSecond Chance: {'AVAILABLE' if game_player.has_second_chance_available() else 'USED'}")
        print("Controls: w (up) / a (left) / s (down) / d (right) to move")
        print("          'hint' for BFS suggestion, 'quit' to exit")
        cmd = input("Your move: ").strip().lower()

        if cmd == 'quit':
            print("Thanks for playing!")
            break
        elif cmd == 'hint':
            # For hint, traps are obstacles
            hint_path = mz.bfs(maze_data, traps_set, game_player.get_position(), goal_pos)
            if hint_path and len(hint_path) > 0:
                print(f"HINT: Try moving {hint_path[0]}.")
            else:
                print("No safe path found or you are at the goal!")
            input("Press Enter to continue...")
            continue

        move_map = {'w': (-1, 0), 's': (1, 0), 'a': (0, -1), 'd': (0, 1)}
        if cmd in move_map:
            dr, dc = move_map[cmd]
            current_player_pos = game_player.get_position()
            nr, nc = current_player_pos[0] + dr, current_player_pos[1] + dc

            if 0 <= nr < mz.ROWS and 0 <= nc < mz.COLS and maze_data[nr][nc] != mz.WALL:
                game_player.set_position(nr, nc)
                new_player_pos = game_player.get_position()

                # Check for traps
                if new_player_pos in traps_set:
                    clear()
                    if game_player.use_second_chance():
                        traps_set.remove(new_player_pos) # Trap is disarmed/removed
                        print_maze_state(maze_data, game_player, traps_set, reveal_traps=True) # Show revealed trap
                        print("\n⚠️ You stepped on a TRAP... but you survived thanks to your second chance!")
                        print("The trap has been disarmed.")
                        input("Press Enter to continue...")
                    else:
                        # Game Over - stepped on trap, no second chance
                        game_over_message = "\n💥 You stepped on a TRAP! Game Over!"
                        continue # To top of loop to print final state and message

                # Check for goal
                # The goal is marked by its symbol mz.GOAL in maze_data
                if maze_data[new_player_pos[0]][new_player_pos[1]] == mz.GOAL:
                    # Game Won
                    game_over_message = "\n🎉 Congratulations! You reached the GOAL!"
                    continue # To top of loop to print final state and message
            else:
                print("You can't move there (wall or boundary)!")
                input("Press Enter to continue...")
        else:
            print("Invalid input! Use w/a/s/d, 'hint', or 'quit'.")
            input("Press Enter to continue...")

if __name__ == '__main__':
    main()