from copy import deepcopy

WHITE = "white"
BLACK = "black"

FILES = "abcdefgh"


def parse(square):
    return 8 - int(square[1]), FILES.index(square[0])


def to_sq(pos):
    return FILES[pos[1]] + str(8 - pos[0])


class BasePiece:
    def __init__(self, side):
        self.side = side
        self.was_moved = False

    def is_enemy(self, other):
        return other and other.side != self.side


class Pawn(BasePiece):
    def moves(self, board, pos, attack=False):
        res = []
        x, y = pos
        step = -1 if self.side == WHITE else 1

        if not attack:
            if board.at(x + step, y) is None:
                res.append((x + step, y))
                if not self.was_moved and board.at(x + 2 * step, y) is None:
                    res.append((x + 2 * step, y))

        for dy in (-1, 1):
            nx, ny = x + step, y + dy
            if 0 <= ny < 8:
                if attack or self.is_enemy(board.at(nx, ny)):
                    res.append((nx, ny))

        return res

    def __repr__(self):
        return "♙" if self.side == WHITE else "♟"


class Rook(BasePiece):
    def moves(self, board, pos, attack=False):
        return board.ray_moves(pos, self.side, [(1,0),(-1,0),(0,1),(0,-1)])
    def __repr__(self):
        return "♖" if self.side == WHITE else "♜"


class Bishop(BasePiece):
    def moves(self, board, pos, attack=False):
        return board.ray_moves(pos, self.side, [(1,1),(-1,-1),(1,-1),(-1,1)])
    def __repr__(self):
        return "♗" if self.side == WHITE else "♝"


class Queen(BasePiece):
    def moves(self, board, pos, attack=False):
        return board.ray_moves(pos, self.side,
                              [(1,0),(-1,0),(0,1),(0,-1),
                               (1,1),(-1,-1),(1,-1),(-1,1)])
    def __repr__(self):
        return "♕" if self.side == WHITE else "♛"


class Knight(BasePiece):
    def moves(self, board, pos, attack=False):
        res = []
        x, y = pos
        for dx, dy in [(2,1),(2,-1),(-2,1),(-2,-1),
                       (1,2),(1,-2),(-1,2),(-1,-2)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                t = board.at(nx, ny)
                if t is None or self.is_enemy(t):
                    res.append((nx, ny))
        return res

    def __repr__(self):
        return "♘" if self.side == WHITE else "♞"


class King(BasePiece):
    def moves(self, board, pos, attack=False):
        res = []
        x, y = pos

        for dx in (-1,0,1):
            for dy in (-1,0,1):
                if dx == dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    t = board.at(nx, ny)
                    if t is None or self.is_enemy(t):
                        res.append((nx, ny))

        if attack:
            return res

        if not self.was_moved and not board.in_check(self.side):
            row = x

            rook = board.at(row, 7)
            if isinstance(rook, Rook) and not rook.was_moved:
                if all(board.at(row, c) is None for c in (5,6)):
                    res.append((row,6))

            rook = board.at(row, 0)
            if isinstance(rook, Rook) and not rook.was_moved:
                if all(board.at(row, c) is None for c in (1,2,3)):
                    res.append((row,2))

        return res

    def __repr__(self):
        return "♔" if self.side == WHITE else "♚"


class ChessBoard:
    def __init__(self):
        self.grid = [[None]*8 for _ in range(8)]
        self.history = []
        self.init_board()

    def init_board(self):
        for i in range(8):
            self.grid[6][i] = Pawn(WHITE)
            self.grid[1][i] = Pawn(BLACK)

        self.grid[7] = [Rook(WHITE),Knight(WHITE),Bishop(WHITE),Queen(WHITE),
                        King(WHITE),Bishop(WHITE),Knight(WHITE),Rook(WHITE)]
        self.grid[0] = [Rook(BLACK),Knight(BLACK),Bishop(BLACK),Queen(BLACK),
                        King(BLACK),Bishop(BLACK),Knight(BLACK),Rook(BLACK)]

    def at(self, x, y):
      return self.grid[x][y] if 0 <= x < 8 and 0 <= y < 8 else None

    def ray_moves(self, pos, side, dirs):
        res = []
        x, y = pos
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                t = self.at(nx, ny)
                if t is None:
                    res.append((nx, ny))
                elif t.side != side:
                    res.append((nx, ny))
                    break
                else:
                    break
                nx += dx
                ny += dy
        return res

    def find_king(self, side):
        for i in range(8):
            for j in range(8):
                p = self.grid[i][j]
                if isinstance(p, King) and p.side == side:
                    return (i,j)

    def in_check(self, side):
        king_pos = self.find_king(side)
        for i in range(8):
            for j in range(8):
                p = self.grid[i][j]
                if p and p.side != side:
                    if king_pos in p.moves(self, (i,j), True):
                        return True
        return False

    def apply_move(self, start, end):
        piece = self.at(*start)
        self.history.append(deepcopy(self.grid))

        if isinstance(piece, King) and abs(end[1]-start[1]) == 2:
            if end[1] == 6:
                rook = self.at(start[0], 7)
                self.grid[start[0]][5] = rook
                self.grid[start[0]][7] = None
                rook.was_moved = True
            else:
                rook = self.at(start[0], 0)
                self.grid[start[0]][3] = rook
                self.grid[start[0]][0] = None
                rook.was_moved = True

        self.grid[end[0]][end[1]] = piece
        self.grid[start[0]][start[1]] = None
        piece.was_moved = True

        if isinstance(piece, Pawn):
            if (piece.side == WHITE and end[0] == 0) or \
               (piece.side == BLACK and end[0] == 7):
                self.grid[end[0]][end[1]] = Queen(piece.side)

    def rollback(self):
        if self.history:
            self.grid = self.history.pop()

    def draw(self):
        print("  a b c d e f g h")
        for i, row in enumerate(self.grid):
            print(8-i, " ".join(str(p) if p else "." for p in row))
        print()


class ChessGame:
    def __init__(self):
        self.board = ChessBoard()
        self.turn = WHITE

    def valid_moves(self, pos):
        piece = self.board.at(*pos)
        if not piece or piece.side != self.turn:
            return []

        res = []
        for m in piece.moves(self.board, pos):
            copy = deepcopy(self.board)
            copy.apply_move(pos, m)
            if not copy.in_check(self.turn):
                res.append(m)
        return res

    def any_moves(self):
        for i in range(8):
            for j in range(8):
                if self.valid_moves((i,j)):
                    return True
        return False

    def run(self):
        while True:
            self.board.draw()

            if self.board.in_check(self.turn):
                print("ШАХ!")

            if not self.any_moves():
                print("МАТ!" if self.board.in_check(self.turn) else "ПАТ!")
                break

            print(f"Ход: {'Белые' if self.turn == WHITE else 'Чёрные'}")
            cmd = input("Введите ход (e2 e4) или 'откат': ")

            if cmd == "откат":
                self.board.rollback()
                self.turn = BLACK if self.turn == WHITE else WHITE
                continue

            try:
                s, e = cmd.split()
                start = parse(s)
                end = parse(e)
            except:
                print("Ошибка ввода")
                continue

            moves = self.valid_moves(start)
            print("Возможные ходы:", [to_sq(m) for m in moves])

            if end in moves:
                self.board.apply_move(start, end)
                self.turn = BLACK if self.turn == WHITE else WHITE
            else:
                print("Недопустимый ход")

if __name__ == "__main__":
    ChessGame().run()
