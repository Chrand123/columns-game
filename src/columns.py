# Core logic for Columns Game

import random
from collections import namedtuple

# includes empty color (0), and the rest of the colors (1-7)
TOTAL_COLORS = 8
# consists of 3 jewels
FALLER_LENGTH = 3
MIN_MATCH_LENGTH = 3

FROZEN_STATE = 0
FALLING_STATE = 1
LANDED_STATE = 2
MATCHED_STATE = 3

MIN_ROWS = 4
MIN_COLS = 3


Position = namedtuple('Position', 'row col')


class GameRuleError(Exception):
    pass


class GameOver(Exception):
    pass



# ------------ JEWEL CLASS ----------- #

class Jewel:
    def __init__(self, color = 0, state = 0):
        self._color = color
        self._state = state
        

    def __eq__(self, jewel) -> bool:
        return self._color == jewel.color()


    def matches(self, jewel) -> bool:
        return (self._color == jewel.color() and
                self._state == jewel.state())


    def set_color(self, color: int) -> None:
        '''Sets the color of the jewel'''
        self._color = color


    def set_state(self, state: int) -> None:
        '''Sets the state of the jewel:
        frozen = 0,
        falling = 1,
        landed = 2,
        matched = 3'''
        self._state = state
    

    def color(self) -> int:
        '''Returns the color of the jewel, as an int'''
        return self._color


    def state(self) -> int:
        '''Returns the state of the jewel, as an int'''
        return self._state



# ------------ FALLER CLASS ----------- #

class Faller:
    def __init__(self, jewels: list[int] = []):
        self._jewels = []
        if len(jewels) == 0:
            # randomize if did not give jewels list
            for n in range(FALLER_LENGTH):
                random_color = int(random.random() * (TOTAL_COLORS - 1)) + 1
                self._jewels.append(Jewel(random_color, FALLING_STATE))
        else:
            # create faller with specified jewel list
            for i in jewels:
                self._jewels.append(Jewel(i, FALLING_STATE))


    def __eq__(self, faller) -> bool:
        return self._jewels == faller.jewels()


    def rotate(self) -> None:
        rotated_jewels = []
        for i in range(len(self._jewels)):
            rotated_jewels.append(self._jewels[(i - 1) % FALLER_LENGTH])

        self._jewels = rotated_jewels


    def jewels(self) -> list[Jewel]:
        return self._jewels


    def fall(self) -> None:
        for jewel in self._jewels:
            jewel.set_state(FALLING_STATE)


    def land(self) -> None:
        for jewel in self._jewels:
            jewel.set_state(LANDED_STATE)


    def freeze(self) -> None:
        for jewel in self._jewels:
            jewel.set_state(FROZEN_STATE)


    def state(self) -> int:
        return self._jewels[0].state()
    


# ------------ FIELD CLASS ----------- #

class Field:
    def __init__(self, rows: int, cols: int):
        self._cells = []
        # Create empty field with correct size (includes invisible rows)
        for i in range(rows + FALLER_LENGTH - 1):
            row = []
            for j in range(cols):
                row.append(Jewel())
            self._cells.append(row)


    def fill(self, contents: list[list[int]]) -> None:
        '''Fills cells with contents, applies gravity'''
        for i in reversed(range(len(contents))):
            for j in range(len(contents[i])):
                row_from_gravity = i
                row_from_gravity += self.count_empty_spaces_underneath(
                    Position(i, j))
                cell = self._cells[row_from_gravity + FALLER_LENGTH - 1][j]
                cell.set_color(contents[i][j])

    def count_empty_spaces_underneath(self, pos: Position) -> int:
        '''Counts how many empty spaces are underneath a certain position
        Stops counting if it reaches a jewel'''
        count = 0
        for i in range(pos.row + FALLER_LENGTH, self.rows()):
            if self._cells[i][pos.col].color() == 0:
                count += 1
            else:
                return count
        return count


    def rows(self) -> int:
        return len(self._cells)


    def visible_rows(self) -> int:
        return (self.rows() - (FALLER_LENGTH - 1))


    def cols(self) -> int:
        return len(self._cells[0])


    def get_cell(self, pos: Position) -> Jewel:
        return self._cells[pos.row + FALLER_LENGTH - 1][pos.col]


    def set_cell(self, pos: Position, jewel: Jewel) -> None:
        self._cells[pos.row + (FALLER_LENGTH - 1)][pos.col] = jewel


    def set_cells(self, jewel_positions: [(Position, Jewel)]) -> None:
        for position, jewel in jewel_positions:
            self.set_cell(position, jewel)
    

    def cells(self) -> list[list[Jewel]]:
        return self._cells


    def visible_cells(self) -> list[list[Jewel]]:
        return self._cells[(FALLER_LENGTH - 1):]


    def trigger_match(self) -> None:
        for i in range(len(self._cells)):
            for j in range(len(self._cells[i])):
                jewel = self._cells[i][j]
                


    def get_aligned_jewels(self, jewel: Jewel) -> list[Position]:
        while True:
            break


    def jewel_exists(self, jewel: Jewel) -> bool:
        for i in range(len(self._cells)):
            for j in range(len(self._cells[i])):
                if id(self._cells[i][j]) == id(jewel):
                    return True
        return False


    def get_position(self, jewel: Jewel) -> Position:
        for i in range(len(self._cells)):
            for j in range(len(self._cells[i])):
                if id(self._cells[i][j]) == id(jewel):
                    return Position(i, j)
                

    def is_valid_space(self, pos: Position) -> bool:
        return (pos.row >= (-FALLER_LENGTH + 1) and
                pos.row < self.visible_rows() and
                pos.col >= 0 and pos.col < self.cols())


    def is_empty_space(self, pos: Position) -> bool:
        return self._cells[pos.row + FALLER_LENGTH - 1][pos.col] == Jewel(0)


    def apply_gravity(self) -> None:
        '''Fills in holes under cells'''
        for i in reversed(range(len(self._cells))):
            for j in range(len(self._cells[i])):
                jewel = self._cells[i][j]
                pos = Position(i - (FALLER_LENGTH - 1), j)
                row_from_gravity = i
                empty_spaces = self.count_empty_spaces_underneath(pos)
                row_from_gravity += empty_spaces
                if empty_spaces > 0:
                    self._cells[row_from_gravity][j] = jewel
                    self._cells[i][j] = Jewel(0)
        
                
    


# ------------ GAME STATE CLASS ----------- #

class GameState:
    def __init__(self, rows: int, cols: int):
        if (type(rows) == int and type(cols) == int
            and rows >= MIN_ROWS and cols >= MIN_COLS):
            pass
        else:
            raise GameRuleError()

        # Invisible rows included in Field class
        # don't need to worry about it here
        self._field = Field(rows, cols)

        self._faller = Faller()
        self._game_over = False

        # position of the last jewel in the faller
        # is None when faller is not falling
        self._faller_position = None # starts off at 0 (so top jewel is at -2)


    def fill_field(self, contents: list[list[int]]) -> None:
        valid_input = True
        if (type(contents) == list
            and len(contents) == self._field.visible_rows()):
            for row in contents:
                if type(row) == list and len(row) == self._field.cols():
                    for jewel in row:
                        if (type(jewel) == int
                            and jewel >= 0 and jewel < TOTAL_COLORS):
                            pass
                        else:
                            valid_input = False
                            break
                else:
                    valid_input = False
                    break
        else:
            valid_input = False

        if not valid_input:
            raise GameRuleError('Invalid parameters to fill field')
                
        self._field.fill(contents)
        self.search_for_matches()


    def field(self) -> Field:
        return self._field


    def handle_time(self) -> None:
        '''Handles the passage of time (e.g., moving the faller down, etc.)
        1 tick = user input (whether it's a blank line or a command)'''
        if self._faller_position != None:
            self.move_faller_down()
        else:
            self.eliminate_matches()
            self._field.apply_gravity()
            self.search_for_matches()
            if not self.check_if_faller_fits():
                raise GameOver()
            


    def move_faller_down(self) -> None:
        '''Checks if it is a valid move to have the faller move downwards,
        then moves the faller one column downwards for each of its jewels'''
        empty_spaces = self._field.count_empty_spaces_underneath(
            self._faller_position)
        if empty_spaces > 0:
            col = self._faller_position.col
            top_row = self._faller_position.row - (FALLER_LENGTH - 1)
            jewel_index = FALLER_LENGTH - 1
            for row in reversed(range(top_row, top_row + FALLER_LENGTH)):
                jewel = self._faller.jewels()[jewel_index]
                jewel_index -= 1
                
                self._field.set_cell(Position(row + 1, col), jewel)
                if row == top_row:
                    self._field.set_cell(Position(row, col), Jewel(0, 0))
                    
            self._faller_position = Position(self._faller_position.row + 1,
                                             self._faller_position.col)

            # check position again to see if it has landed
            self.check_faller_landing()
        else:
            self._faller.freeze()
            self.search_for_matches()
            if not self.check_if_faller_fits():
                raise GameOver()
            self._faller_position = None


    def check_if_faller_fits(self) -> bool:
        if not self.match_exists():
            return self.invisible_rows_are_empty()
        else:
            return True


    def invisible_rows_are_empty(self) -> bool:
        cells = self._field.cells()
        for i in range(FALLER_LENGTH - 1):
            for j in range(len(cells[i])):
                if cells[i][j].color() != 0:
                    return False
        return True


    def check_faller_landing(self) -> bool:
        '''Lands/Unlands the faller if there is a jewel/space under it
        and returns if it got landed/unlanded'''
        empty_spaces = self._field.count_empty_spaces_underneath(
            self._faller_position)
        if empty_spaces <= 0:
            if self._faller.state() == FALLING_STATE:
                self._faller.land()
            return True
        else:
            if self._faller.state() == LANDED_STATE:
                self._faller.fall()
            return False


    def current_faller(self) -> Faller:
        return self._faller


    def update_faller(self, jewels: list[int] = []) -> None:
        if self._faller_position != None:
            raise GameRuleError('Cannot update a faller already on the field')
            
        self._faller = Faller(jewels)


    def drop_faller(self, col: int) -> None:
        if self._faller_position != None:
            raise GameRuleError('Cannot drop a faller already on the field')

        if col < 1 or col > self._field.cols():
            raise GameRuleError('Invalid Column to Drop Faller')

        if self._field.get_cell(Position(0, col - 1)) != Jewel(0):
            raise GameOver()

        
        index = 0
        for jewel in self._faller.jewels():
            position = Position(index - (FALLER_LENGTH - 1), col - 1)
            self._field.set_cell(position, jewel)
            self._faller_position = position
            index += 1

        self.check_faller_landing()
        

    def rotate_faller(self) -> None:
        self._faller.rotate()
        current_row = self._faller_position.row
        col = self._faller_position.col
        for jewel in reversed(self._faller.jewels()):
            self._field.set_cell(Position(current_row, col), jewel)
            current_row -= 1
    

    def move_faller_column(self, direction: int) -> None:
        '''Moves the faller left or right, depending on the direction'''
        row = self._faller_position.row
        col = self._faller_position.col
        
        # first check:
        for jewel in reversed(self._faller.jewels()):
            position = Position(row, col + direction)
            
            if not (self._field.is_valid_space(position) and
                self._field.is_empty_space(position)):
                # either not valid space to move or there is an
                # existing jewel in that space
                return
            row -= 1

        row = self._faller_position.row
        for jewel in reversed(self._faller.jewels()):
            position = Position(row, col + direction)
            self._field.set_cell(position, jewel)
            self._field.set_cell(Position(row, col), Jewel(0))
            row -= 1

        self._faller_position = Position(self._faller_position.row,
                                         col + direction)

        self.check_faller_landing()



    def get_faller_position(self) -> Position:
        return self._faller_position


    
    def get_all_jewels_of(self, color: int) -> [(Position, Jewel)]:
        jewel_positions = []
        cells = self._field.cells()
        for i in range(len(cells)):
            for j in range(len(cells[i])):
                jewel = cells[i][j]
                if jewel.color() == color:
                    jewel_positions.append(
                        (Position(i, j), jewel)
                    )
        return jewel_positions
    

    def search_for_matches(self) -> None:
        '''Searches for matches of every jewel type and sets the state
        of all the jewels with a match as MATCHED_STATE'''
        for color in range(1, TOTAL_COLORS):
            jewel_positions = self.get_all_jewels_of(color)
            count = 1
            for position, jewel in jewel_positions:
                if count >= len(jewel_positions):
                    break
                start = count

                # horizontal delta
                matches = self.get_matches_for_delta(
                    (0, 1), jewel_positions[start:],
                    (position, jewel)
                    )

                matches = self.get_matches_for_delta(
                    (0, -1), jewel_positions[start:],
                    (position, jewel)
                    )

                # vertical delta
                matches = self.get_matches_for_delta(
                    (1, 0), jewel_positions[start:],
                    (position, jewel)
                    )

                matches = self.get_matches_for_delta(
                    (-1, 0), jewel_positions[start:],
                    (position, jewel)
                    )

                # diagonal delta
                matches = self.get_matches_for_delta(
                    (1, 1), jewel_positions[start:],
                    (position, jewel)
                    )

                matches = self.get_matches_for_delta(
                    (1, -1), jewel_positions[start:],
                    (position, jewel)
                    )

                matches = self.get_matches_for_delta(
                    (-1, 1), jewel_positions[start:],
                    (position, jewel)
                    )

                matches = self.get_matches_for_delta(
                    (-1, -1), jewel_positions[start:],
                    (position, jewel)
                    )
                

                count += 1


    def get_matches_for_delta(
        self, delta: (int, int), pos_jewels: list[(Position, Jewel)],
        current_pos_jewel: (Position, Jewel)) -> None:
        '''Delta Inputs:
        (0, 1) -> horizontal match
        (1, 0) -> vertical match
        (1, 1) -> diagonal match
        '''
        position, jewel = current_pos_jewel
        deltas = [delta]
        aligned_jewels = [jewel]
        previous_pos = position
        for i in range(len(pos_jewels)):
            next_pos, next_jewel = pos_jewels[i]
            delta = self.get_delta_of_positions(previous_pos,
                                                next_pos)
            
            if self.equals_all(deltas, delta):
                deltas.append(delta)
                

            if self.equals_all(deltas, delta):
                aligned_jewels.append(next_jewel)
                previous_pos = next_pos
                
        if len(aligned_jewels) >= MIN_MATCH_LENGTH:
            for jewel in aligned_jewels:
                jewel.set_state(MATCHED_STATE)
                # print(self._field.get_position(jewel))
        


    def get_delta_of_positions(self,
                               pos1: Position,
                               pos2: Position) -> (int, int):
        '''Gets the difference between two positions, returns it as
        a tuple of horizontal and vertical distance'''
        return (pos2.row - pos1.row, pos2.col - pos1.col)


    def is_aligned(self, delta: (int, int)) -> bool:
        '''Determines if it is aligned'''
        x, y = delta
        return (-1 <= x <= 1) and (-1 <= y <= 1)



    def get_equivalent_deltas_from(
        self, deltas_jewels: [((int, int), Jewel)]) -> list[Jewel]:
        start = 1
        all_aligned_jewels = []
        for delta, jewel in deltas_jewels:
            aligned_jewels = []
            for i in range(start, len(deltas_jewels)):
                next_delta, next_jewel = deltas_jewels[i]
                if delta == next_delta:
                    aligned_jewels.append(next_jewel)
            # excludes the first jewel of the match
            if len(aligned_jewels) >= MIN_MATCH_LENGTH - 1:
                all_aligned_jewels.extend(aligned_jewels)
            
            start += 1
        return all_aligned_jewels
    

    def equals_all(self, values: list, val) -> bool:
        for v in values:
            if v != val:
                return False
        return True
    

    def eliminate_matches(self) -> None:
        cells = self._field.cells()
        for i in range(len(cells)):
            for j in range(len(cells[i])):
                if cells[i][j].state() == MATCHED_STATE:
                    cells[i][j] = Jewel(0)


    def match_exists(self) -> bool:
        '''Checks if any of the cells are marked in the matched state'''
        cells = self._field.cells()
        for i in range(len(cells)):
            for j in range(len(cells[i])):
                if cells[i][j].state() == MATCHED_STATE:
                    return True
        return False
    

    def game_over(self) -> bool:
        return self._game_over
