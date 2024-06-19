import random
import graphviz
import copy

class DominoTile:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"[{self.left}|{self.right}]"

class Player:
    def __init__(self, name):
        self.name = name
        self.tiles = []

    def draw_tile(self, tile):
        self.tiles.append(tile)

    def play_tile(self, tile, board):
        self.tiles.remove(tile)
        if tile.left == board[-1].right:
            board.append(tile)
        elif tile.right == board[-1].right:
            tile.left, tile.right = tile.right, tile.left
            board.append(tile)
        elif tile.left == board[0].left:
            tile.left, tile.right = tile.right, tile.left
            board.insert(0, tile)
        elif tile.right == board[0].left:
            board.insert(0, tile)
        else:
            raise ValueError("Tile cannot be played")

    def has_playable_tile(self, board):
        left_end = board[0].left
        right_end = board[-1].right
        return any(tile.left in (left_end, right_end) or tile.right in (left_end, right_end) for tile in self.tiles)

class AIPlayer(Player):
    def choose_tile(self, board, available_tiles):
        best_tile = None
        best_score = float('-inf')
        tree = graphviz.Digraph()
        tree.node("Start", f"Board: {board}\nAI Tiles: {self.tiles}")

        print(f"\n{self.name} is thinking...")

        for tile in self.get_playable_tiles(board):
            new_board = self.simulate_play(board, tile)
            new_tiles = self.tiles[:]
            new_tiles.remove(tile)
            score = self.expectiminimax(new_board, new_tiles, available_tiles, depth=3, is_maximizing=False, tree=tree, move=f"Start->{tile}")
            tree.node(f"Start->{tile}", f"{tile}\nScore: {score}")
            tree.edge("Start", f"Start->{tile}")
            print(f"Evaluated move {tile} with score {score}")
            if score > best_score:
                best_score = score
                best_tile = tile

        print(f"AI chose tile {best_tile} with score {best_score}")
        tree.node("Best Move", f"Best Move: {best_tile}\nScore: {best_score}")
        tree.edge(f"Start->{best_tile}", "Best Move")
        tree.render('ai_decision_tree', format='png', view=True)
        return best_tile

    def expectiminimax(self, board, ai_tiles, available_tiles, depth, is_maximizing, tree, move):
        if depth == 0 or not ai_tiles:
            return self.evaluate(board, ai_tiles)

        if is_maximizing:
            best_score = float('-inf')
            for tile in self.get_playable_tiles(board, ai_tiles):
                new_board = self.simulate_play(board, tile)
                new_tiles = ai_tiles[:]
                new_tiles.remove(tile)
                score = self.expectiminimax(new_board, new_tiles, available_tiles, depth - 1, False, tree, move + f"->{tile}")
                tree.node(move + f"->{tile}", f"{tile}\nScore: {score}")
                tree.edge(move, move + f"->{tile}")
                best_score = max(best_score, score)
            return best_score
        else:
            # Opponent's turn with hidden tiles
            best_score = float('inf')
            for tile in available_tiles:
                new_opponent_tiles = [tile]
                new_available_tiles = available_tiles[:]
                new_available_tiles.remove(tile)
                score = 0
                playable = False
                for opp_tile in new_opponent_tiles:
                    if any(tile.left in (board[0].left, board[-1].right) or tile.right in (board[0].left, board[-1].right) for tile in new_opponent_tiles):
                        playable = True
                        new_board = self.simulate_play(board, opp_tile)
                        new_opponent_tiles.remove(opp_tile)
                        score = self.expectiminimax(new_board, ai_tiles, new_available_tiles, depth - 1, True, tree, move + f"->Draw {tile}")
                if not playable:
                    score = self.expectiminimax(board, ai_tiles, new_available_tiles, depth - 1, True, tree, move + f"->Draw {tile}")
                best_score = min(best_score, score)
            return best_score

    def get_playable_tiles(self, board, tiles=None):
        if tiles is None:
            tiles = self.tiles
        left_end = board[0].left
        right_end = board[-1].right
        return [tile for tile in tiles if tile.left in (left_end, right_end) or tile.right in (left_end, right_end)]

    def simulate_play(self, board, tile):
        new_board = board[:]
        if tile.left == board[-1].right:
            new_board.append(tile)
        elif tile.right == board[-1].right:
            tile.left, tile.right = tile.right, tile.left
            new_board.append(tile)
        elif tile.left == board[0].left:
            tile.left, tile.right = tile.right, tile.left
            new_board.insert(0, tile)
        elif tile.right == board[0].left:
            new_board.insert(0, tile)
        return new_board

    def evaluate(self, board, tiles):
        score = -len(tiles)
        score += sum(1 for tile in tiles if tile.left == board[0].left or tile.right == board[0].left or \
                                            tile.left == board[-1].right or tile.right == board[-1].right)
        score += 5 * any(tile.left == board[-1].right or tile.right == board[-1].right for tile in tiles)
        score += 5 * any(tile.left == board[0].left or tile.right == board[0].left for tile in tiles)
        high_value_tiles = [tile for tile in tiles if tile.left + tile.right >= 10]
        score -= len(high_value_tiles) * 2
        return score

class HumanPlayer(Player):
    def choose_tile(self, board):
        while True:
            try:
                print(f"Your tiles: {self.tiles}")
                tile_index = int(input("Choose a tile index to play: "))
                tile = self.tiles[tile_index]
                if tile.left == board[0].left or tile.right == board[0].left or \
                tile.left == board[-1].right or tile.right == board[-1].right:
                    return tile
                else:
                    print("Tile cannot be played. Choose another tile.")
            except (IndexError, ValueError):
                print("Invalid input. Choose a valid tile index.")

def create_domino_set():
    tiles = [DominoTile(i, j) for i in range(1, 7) for j in range(i, 7)]
    random.shuffle(tiles)
    return tiles

def distribute_tiles(tiles):
    players = [HumanPlayer("Human"), AIPlayer("AI")]
    for _ in range(7):
        for player in players:
            player.draw_tile(tiles.pop())
    return players

def main():
    tiles = create_domino_set()
    players = distribute_tiles(tiles)
    board = [tiles.pop()]

    current_player_index = 0
    while True:
        current_player = players[current_player_index]
        print(f"\nBoard: {board}")
        print(f"{current_player.name}'s turn")
        
        if current_player.has_playable_tile(board):
            if isinstance(current_player, HumanPlayer):
                tile = current_player.choose_tile(board)
            else:
                print(f"AI's tiles: {current_player.tiles}")  # Display AI's tiles
                tile = current_player.choose_tile(board, tiles)
                print(f"AI plays {tile}")
            current_player.play_tile(tile, board)
        else:
            if tiles:
                print(f"{current_player.name} has no playable tiles. Drawing a tile.")
                current_player.draw_tile(tiles.pop())
            else:
                print(f"{current_player.name} has no playable tiles and no tiles left to draw. Skipping turn.")

        if not current_player.tiles:
            print(f"{current_player.name} wins!")
            break

        if not any(player.has_playable_tile(board) for player in players) and not tiles:
            print("No more playable tiles and no tiles left to draw. The game ends in a draw!")
            break

        current_player_index = (current_player_index + 1) % 2

if __name__ == "__main__":
    main()
