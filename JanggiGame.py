# Author: Cheng-Ying Wu
# Date: 03/11/2021
# Description: A JanggiGame class for playing an abstract board game called Janggi.
from termcolor import colored


class JanggiGame:
    """
    Represents an abstract board game called Janggi for the users to play this game.
    """

    def __init__(self):
        """
        Creates an object with different private data members and initializes all data members.
        """
        # Creates an empty list that is used to store all positions on the board
        self._board_pos = []
        # Creates lists that stores the positions of the palace
        self._palace_red = ["d1", "d2", "d3", "e1", "e2", "e3", "f1", "f2", "f3"]
        self._palace_blue = ["d8", "d9", "d10", "e8", "e9", "e10", "f8", "f9", "f10"]
        self._palace_all = self._palace_red + self._palace_blue
        # Initializes the board
        self._board = self.start_board()
        # Initializes the game state to "UNFINISHED"
        self._game_state = "UNFINISHED"
        # Keeps track of whose turn and initializing it to the starting player "blue"
        self._whose_turn = "blue"
        # Initializes lists that are used to track general's remaining legal moves to the four position besides.
        self._track_blue = ["d8", "d9", "e8", "e10", "f8", "f9"]
        self._track_red = ["d2", "d3", "e1", "e3", "f2", "f3"]
        # Initializes the player objects
        self._blue = Blue()
        self._red = Red()

    def get_board(self):
        """
        Returns the board.
        """
        return self._board

    def get_game_state(self):
        """
        Returns one of these values, depending on the game state: "UNFINISHED" or "RED_WON" or "BLUE_WON".
        """
        return self._game_state

    def get_whose_turn(self):
        """
        Returns the player whose turn.
        """
        return self._whose_turn

    def set_whose_turn(self, player):
        """
        Sets the player whose turn to the next player.
        """
        self._whose_turn = player

    def get_palace_red(self):
        """
        Returns red's palace.
        """
        return self._palace_red

    def get_palace_blue(self):
        """
        Returns blue's palace.
        """
        return self._palace_blue

    def get_palace_all(self):
        """
        Returns all palace's positions.
        """
        return self._palace_all

    def get_board_pos(self):
        """
        Returns the list that is used to store all positions on the board.
        """
        return self._board_pos

    def get_track_blue(self):
        """
        Returns the list that is used to track general's remaining legal moves (blue).
        """
        return self._track_blue

    def get_track_red(self):
        """
        Returns the list that is used to track general's remaining legal moves (red).
        """
        return self._track_red

    def is_in_check(self, player):
        """
        Takes as a parameter either "red" or "blue" and returns True if that player is in check,
        but returns False otherwise.
        """
        # blue player
        if player == "blue":
            if self._blue.get_in_check() is True:
                return True
        # red player
        if player == "red":
            if self._red.get_in_check() is True:
                return True

        return False

    def make_move(self, start_pos, end_pos):
        """
        Takes two parameters (strings) that represent the square to move from and the square to move to.
        Return False:
        If the square being moved from does not contain a piece belonging to the player whose turn it is.
        If the indicated move is not legal.
        If the game has already been won.
        Otherwise it should make the indicated move, remove any captured piece, update the game state if necessary,
        update whose turn it is, and return True.
        """
        # Track tests
        print("Attempting: ", start_pos, "->", end_pos)

        # Calls search_pos to find the piece object on it
        piece = self.search_pos(start_pos)
        # Check whether there is a piece on the starting position
        if piece is None:
            return False

        # Pass a turn
        if start_pos == end_pos:
            # Cannot pass when being in check
            if piece.get_player() == "blue":
                if self._blue.get_in_check() is True:
                    return False
            else:
                if self._red.get_in_check() is True:
                    return False
            # Update whose turn it is
            if self.get_whose_turn() == "red":
                self.set_whose_turn("blue")
            else:
                self.set_whose_turn("red")
            return True

        # If the square being moved from does not contain a piece belonging to the player whose turn it is
        if piece.get_player() != self.get_whose_turn():
            return False
        # Calls move method to check the move is whether valid
        if self.valid_move(piece, end_pos) is False:
            return False
        # Checks the game current status (Cannot move after the game completed)
        if self.get_game_state() == "RED_WON" or self.get_game_state() == "BLUE_WON":
            return False

        # Removes any captured piece
        if self.search_pos(end_pos) is not None:
            # Remove from the player's remaining piece list
            # blue player
            if self.search_pos(end_pos).get_player() == "blue":
                self._blue.remove_piece(self.search_pos(end_pos))
            # red player
            else:
                self._red.remove_piece(self.search_pos(end_pos))
            # Update removed piece object's position to None
            self.search_pos(end_pos).set_position(None)

        # Update the Board
        self.clear_board(piece)

        # Update remain lists (move to the new position)
        if piece.get_player() == "blue":
            self._blue.update_position(piece, end_pos)
        else:
            self._red.update_position(piece, end_pos)

        # Update piece object & Board
        piece.set_position(end_pos)
        self.move_board(piece, end_pos)

        # Track General's position
        if piece.get_role() == "General":
            self.track_general(piece)

        # After the valid move is completed, call the next move method to check whether the general is in check
        if self.next_move(piece) is True:
            # Call checkmate method to check whether it is checkmate
            if self.checkmate(piece) is True:
                return True

        # Checks the in check status
        if piece.get_player() == "blue":
            # Check after moving if the general is still being in check
            # Find red player's pieces
            for role, pos in list(self._red.get_remain_piece().items()):
                piece_obj = self.search_pos(pos)
                # If yes, reverse the move and return False
                if self.next_move(piece_obj) is True:
                    # Restore the remain list:
                    self._blue.update_position(piece, start_pos)
                    # Restore the board and piece object
                    self.clear_board(piece)
                    piece.set_position(start_pos)
                    self.move_board(piece, start_pos)
                    # Restore the removed piece and add back to the lists
                    if self.search_pos(end_pos) is not None:
                        self.search_pos(end_pos).set_position(end_pos)
                        self._red.restore_removed(self.search_pos(end_pos), end_pos)
                    # Track back General's position
                    if piece.get_role() == "General":
                        self.track_general(piece)
                    return False
                # If not, change the status since it is not in check now
                self._blue.set_in_check(False)

        if piece.get_player() == "red":
            # Check after moving if the general is still being in check
            # Find blue player's pieces
            for role, pos in list(self._blue.get_remain_piece().items()):
                piece_obj = self.search_pos(pos)
                # If yes, reverse the move and return False
                if self.next_move(piece_obj) is True:
                    # Restore the remain list:
                    self._red.update_position(piece, start_pos)
                    # Restore the board and piece object
                    self.clear_board(piece)
                    piece.set_position(start_pos)
                    self.move_board(piece, start_pos)
                    # Restore the removed piece and add back to the lists
                    if self.search_pos(end_pos) is not None:
                        self.search_pos(end_pos).set_position(end_pos)
                        self._blue.restore_removed(self.search_pos(end_pos), end_pos)
                    # Track back General's position
                    if piece.get_role() == "General":
                        self.track_general(piece)
                    return False
                # If not, change the status since it is not in check now
                self._red.set_in_check(False)

        # Update whose turn it is
        if self.get_whose_turn() == "red":
            self.set_whose_turn("blue")
        else:
            self.set_whose_turn("red")

        return True

    def search_pos(self, pos):
        """
        Takes a parameter (strings) that represents the square and returns the piece object on it.
        """
        for square in self.get_board():
            if pos == square:
                return self.get_board()[pos]

    def start_board(self):
        """
        Add all positions on the board to the board_pos list.
        To initializes the board, implementing a dictionary, which stores the positions (ex. "b3" and "a10") as keys
        and stores the piece objects on the positions as values.
        """
        column_label = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
        row_label = [str(num) for num in range(1, 11)]
        # Sets red's pieces
        role_red = [Chariot("red", "a1"), Elephant("red", "b1"), Horse("red", "c1"), Guard("red", "d1"),
                    General("red", "e2"), Guard("red", "f1"), Elephant("red", "g1"), Horse("red", "h1"),
                    Chariot("red", "i1"), Cannon("red", "b3"), Cannon("red", "h3"), Soldier("red", "a4"),
                    Soldier("red", "c4"), Soldier("red", "e4"), Soldier("red", "g4"), Soldier("red", "i4")]
        # Sets blue's pieces
        role_blue = [Chariot("blue", "a10"), Elephant("blue", "b10"), Horse("blue", "c10"), Guard("blue", "d10"),
                     General("blue", "e9"), Guard("blue", "f10"), Elephant("blue", "g10"), Horse("blue", "h10"),
                     Chariot("blue", "i10"), Cannon("blue", "b8"), Cannon("blue", "h8"), Soldier("blue", "a7"),
                     Soldier("blue", "c7"), Soldier("blue", "e7"), Soldier("blue", "g7"), Soldier("blue", "i7")]
        role_all = role_red + role_blue
        board = {}
        # Creates a list that stores all the positions of the board.
        for column in column_label:
            for row in row_label:
                self._board_pos.append(column + row)

        # Initialize the board with None values
        for position in self._board_pos:
            board[position] = None

        # Add the pieces to the board with their first position
        for square in board:
            for role in role_all:
                position = role.get_position()
                if square == position:
                    board[square] = role

        # Finish initializing
        return board

    def checkmate(self, piece):
        """
        Takes a parameter that represents the piece object.
        Return True when checkmate and update the game status to end the game. Return False, otherwise.
        """
        escape_lst_red = []
        escape_lst_blue = []
        owner = piece.get_player()

        if owner == "blue":
            general_pos = self.get_general_pos("red")
            general = self.search_pos(general_pos)

            # Check the general's next step can whether escapes from in check
            for move in self.get_track_red():
                if self.valid_move(piece, move) is False:
                    escape_lst_red.append(move)

            last_valid_red = []
            for move in escape_lst_red:
                if self.valid_move(general, move) is True:
                    last_valid_red.append(move)

            # Remove the general from the current position (on Board)
            self.clear_board(general)

            left_move_red = []
            # Should also scan all remaining pieces of the blue player
            for move in last_valid_red:
                for role, pos in list(self._blue.get_remain_piece().items()):
                    piece_obj = self.search_pos(pos)
                    if self.valid_move(piece_obj, move) is True:
                        left_move_red.append(move)

            # Add back general's position
            self.move_board(general, general_pos)

            left_char_red = []
            # Check whether red player's other pieces can help
            for role, pos in list(self._red.get_remain_piece().items()):
                piece_obj = self.search_pos(pos)
                if piece_obj.get_role() == "General":
                    continue
                left_char_red.append(piece_obj)

            for red_char in left_char_red:
                for position in self.get_board_pos():
                    if self.valid_move(red_char, position) is True and self.next_move(piece) is False:
                        return False
                    # Piece captured
                    if self.valid_move(red_char, piece.get_position()) is True:
                        return False

            # Compare two lists
            remain_route = set(last_valid_red) - set(left_move_red)

            # After scanning all escape route
            if len(remain_route) != 0:
                return False
            # No place to escape
            else:
                self._game_state = "BLUE_WON"
                return True

        if owner == "red":
            general_pos = self.get_general_pos("blue")
            general = self.search_pos(general_pos)

            # Check the general's next step can whether escapes from in check
            for move in self.get_track_blue():
                if self.valid_move(piece, move) is False:
                    escape_lst_blue.append(move)

            last_valid_blue = []
            for move in escape_lst_blue:
                if self.valid_move(general, move) is True:
                    last_valid_blue.append(move)

            # Remove the general from the current position (on Board)
            self.clear_board(general)

            left_move_blue = []
            # Should also scan all remaining pieces of the red player
            for move in last_valid_blue:
                for role, pos in list(self._red.get_remain_piece().items()):
                    piece_obj = self.search_pos(pos)
                    if self.valid_move(piece_obj, move) is True:
                        left_move_blue.append(move)

            # Add back general's position
            self.move_board(general, general_pos)

            # Check whether blue player's other pieces can help
            left_char_blue = []
            for role, pos in list(self._blue.get_remain_piece().items()):
                piece_obj = self.search_pos(pos)
                if piece_obj.get_role() == "General":
                    continue
                left_char_blue.append(piece_obj)

            for blue_char in left_char_blue:
                for position in self.get_board_pos():
                    if self.valid_move(blue_char, position) is True and self.next_move(piece) is False:
                        return False
                    # Piece captured
                    if self.valid_move(blue_char, piece.get_position()) is True:
                        return False

            # Compare two lists
            remain_route = set(last_valid_blue) - set(left_move_blue)

            # After scanning all escape route
            if len(remain_route) != 0:
                return False
            # No place to escape
            else:
                self._game_state = "RED_WON"
                return True

    def track_general(self, piece):
        """
        Takes a parameter that represents the piece object.
        Track General's valid moves by modifying the list that stores the valid moves of each general.
        """
        if piece.get_player() == "blue":
            self._track_blue = []
            for move in self.get_palace_blue():
                if self.valid_move(piece, move) is True:
                    self._track_blue.append(move)
        else:
            self._track_red = []
            for move in self.get_palace_red():
                if self.valid_move(piece, move) is True:
                    self._track_red.append(move)
        return

    def get_general_pos(self, player):
        """
        Takes Takes a parameter that represents the player.
        Return that player's general position.
        """
        general_pos = None
        if player == "blue":
            for role in self._blue.get_remain_piece():
                if role == "General":
                    general_pos = self._blue.get_remain_piece()[role]
        else:
            for role in self._red.get_remain_piece():
                if role == "General":
                    general_pos = self._red.get_remain_piece()[role]
        return general_pos

    def clear_board(self, piece):
        """
        Takes a parameter that represents the piece object.
        Clears out the original place of the piece on board.
        """
        for square in self._board:
            # Clears out the piece's original place
            if square == piece.get_position():
                self._board[square] = None
                return

    def move_board(self, piece, pos):
        """
        Takes two parameters that represent the square and the piece object.
        Updates the piece's position on the board.
        """
        for square in self._board:
            # Moves the piece object to the new square
            if square == pos:
                self._board[square] = piece
                return

    def next_move(self, piece):
        """
        Take the piece object as the parameter.
        Return True when the next move to the opponent's general's position is valid.
        """
        player_own = piece.get_player()

        # If the piece belongs to the red player
        if player_own == "red":
            # Find general's position
            general_pos = self.get_general_pos("blue")
            # Call valid move method to check
            if self.valid_move(piece, general_pos) is True:
                # Update in check
                self._blue.set_in_check(True)
                return True
            # Also, check other pieces of red can whether capture blue's general
            for role, pos in list(self._red.get_remain_piece().items()):
                piece_obj = self.search_pos(pos)
                if self.valid_move(piece_obj, general_pos) is True:
                    # Update in check
                    self._blue.set_in_check(True)
                    return True
            return False

        # If the piece belongs to the blue player
        if player_own == "blue":
            # Find general's position
            general_pos = self.get_general_pos("red")
            # Call valid move method to check
            if self.valid_move(piece, general_pos) is True:
                # Update in check
                self._red.set_in_check(True)
                return True
            # Also, check other pieces of blue can whether capture red's general
            for role, pos in list(self._blue.get_remain_piece().items()):
                piece_obj = self.search_pos(pos)
                if self.valid_move(piece_obj, general_pos) is True:
                    # Update in check
                    self._red.set_in_check(True)
                    return True
            return False

    def valid_move(self, piece, end_pos):
        """
        Takes two parameters that represent the piece object and its target square.
        According to its role:
        If the move is invalid, then return False.
        Otherwise, return True.
        """
        # Gets the piece's role
        piece_role = piece.get_role()

        if piece_role == "General":
            # Special case list
            invalid_move = ["d2", "e1", "e3", "f2", "d9", "e8", "e10", "f9"]
            # Gets the current square
            its_pos = piece.get_position()
            # Checks this piece belongs to which player
            player_own = piece.get_player()
            # Gets its palace
            if player_own == "red":
                palace = self.get_palace_red()
            else:
                palace = self.get_palace_blue()
            # Checks whether the target square is in the palace
            if end_pos not in palace:
                return False

            # Checks the target square is whether occupied
            pos_object = self.search_pos(end_pos)
            if pos_object is not None:
                # If occupied, then checks this piece belongs to which player
                if player_own == pos_object.get_player():
                    # If these two pieces belong to the same player, return False
                    return False

            # Checks whether the move is valid
            if abs(int(end_pos[1:]) - int(its_pos[1:])) > 1:
                return False
                # Checks alphabet
            if abs(ord(end_pos[0]) - ord(its_pos[0])) > 1:
                return False
            # Special Case
            if (its_pos in invalid_move) and (end_pos in invalid_move):
                return False
            return True

        if piece_role == "Guard":
            # Special case list
            invalid_move = ["d2", "e1", "e3", "f2", "d9", "e8", "e10", "f9"]
            # Gets the current square
            its_pos = piece.get_position()
            # Checks this piece belongs to which player
            player_own = piece.get_player()
            # Gets its palace
            if player_own == "red":
                palace = self.get_palace_red()
            else:
                palace = self.get_palace_blue()
            # Checks whether the target square is in the palace
            if end_pos not in palace:
                return False

            # Checks the target square is whether occupied
            pos_object = self.search_pos(end_pos)
            if pos_object is not None:
                # If occupied, then checks this piece belongs to which player
                if player_own == pos_object.get_player():
                    # If these two pieces belong to the same player, return False
                    return False

            # Checks whether the move is valid
            if abs(int(end_pos[1:]) - int(its_pos[1:])) > 1:
                return False
            # Checks alphabet
            if abs(ord(end_pos[0]) - ord(its_pos[0])) > 1:
                return False
            # Special Case
            if (its_pos in invalid_move) and (end_pos in invalid_move):
                return False
            return True

        if piece_role == "Horse":
            # Gets the current square
            its_pos = piece.get_position()
            # Gets the owner
            player_own = piece.get_player()

            # Checks whether the target square is on the board
            if end_pos not in self.get_board_pos():
                return False

            # Checks the target square is whether occupied
            pos_object = self.search_pos(end_pos)
            if pos_object is not None:
                # If occupied, then checks this piece belongs to which player
                if player_own == pos_object.get_player():
                    # If these two pieces belong to the same player, return False
                    return False

            # Check the move
            # Moves one step orthogonally
            first_move = [(its_pos[0] + str(int(its_pos[1:]) + 1)), (its_pos[0] + str(int(its_pos[1:]) - 1)),
                          (chr(ord(its_pos[0]) + 1) + its_pos[1:]), (chr(ord(its_pos[0]) - 1) + its_pos[1:])]

            not_block = []
            move_lst = []
            # Check whether it is occupied (block)
            for index, value in enumerate(first_move):
                if self.search_pos(value) is None:
                    not_block.append(value)

            # Moves one step diagonally outward
            for first_pos in not_block:
                # Move down
                if int(first_pos[1:]) - int(its_pos[1:]) == 1:
                    first_pos = first_pos[0] + str(int(first_pos[1:]) + 1)
                    move_lst.append(chr(ord(first_pos[0]) + 1) + first_pos[1:])
                    move_lst.append(chr(ord(first_pos[0]) - 1) + first_pos[1:])
                # Move up
                if int(first_pos[1:]) - int(its_pos[1:]) == -1:
                    first_pos = first_pos[0] + str(int(first_pos[1:]) - 1)
                    move_lst.append(chr(ord(first_pos[0]) + 1) + first_pos[1:])
                    move_lst.append(chr(ord(first_pos[0]) - 1) + first_pos[1:])
                # Move right
                if ord(first_pos[0]) - ord(its_pos[0]) == 1:
                    first_pos = chr(ord(first_pos[0]) + 1) + first_pos[1:]
                    move_lst.append(first_pos[0] + str(int(first_pos[1:]) + 1))
                    move_lst.append(first_pos[0] + str(int(first_pos[1:]) - 1))
                # Move left
                if ord(first_pos[0]) - ord(its_pos[0]) == -1:
                    first_pos = chr(ord(first_pos[0]) - 1) + first_pos[1:]
                    move_lst.append(first_pos[0] + str(int(first_pos[1:]) + 1))
                    move_lst.append(first_pos[0] + str(int(first_pos[1:]) - 1))

            valid_lst = []
            # Gets the valid moves list
            for move in move_lst:
                # Check whether it is on the board
                if move in self.get_board_pos():
                    valid_lst.append(move)

            if end_pos not in valid_lst:
                return False
            return True

        if piece_role == "Elephant":
            # Gets the current square
            its_pos = piece.get_position()
            # Gets the owner
            player_own = piece.get_player()

            # Checks whether the target square is on the board
            if end_pos not in self.get_board_pos():
                return False

            # Checks the target square is whether occupied
            pos_object = self.search_pos(end_pos)
            if pos_object is not None:
                # If occupied, then checks this piece belongs to which player
                if player_own == pos_object.get_player():
                    # If these two pieces belong to the same player, return False
                    return False

            # Check the move
            first_move = [(its_pos[0] + str(int(its_pos[1:]) + 1)), (its_pos[0] + str(int(its_pos[1:]) - 1)),
                          (chr(ord(its_pos[0]) + 1) + its_pos[1:]), (chr(ord(its_pos[0]) - 1) + its_pos[1:])]
            not_block = []
            second_move = []

            # Check whether it is occupied (block)
            for index, value in enumerate(first_move):
                if self.search_pos(value) is None:
                    not_block.append(value)

            # Check one step diagonally outward whether is blocked
            for first_pos in not_block:
                # Move down
                if int(first_pos[1:]) - int(its_pos[1:]) == 1:
                    first_pos = first_pos[0] + str(int(first_pos[1:]) + 1)
                    block_1 = chr(ord(first_pos[0]) + 1) + first_pos[1:]
                    block_2 = chr(ord(first_pos[0]) - 1) + first_pos[1:]
                    first_pos = first_pos[0] + str(int(first_pos[1:]) + 1)
                    if self.search_pos(block_1) is None:
                        second_move.append(chr(ord(first_pos[0]) + 2) + first_pos[1:])
                    if self.search_pos(block_2) is None:
                        second_move.append(chr(ord(first_pos[0]) - 2) + first_pos[1:])

                # Move up
                if int(first_pos[1:]) - int(its_pos[1:]) == -1:
                    first_pos = first_pos[0] + str(int(first_pos[1:]) - 1)
                    block_3 = chr(ord(first_pos[0]) + 1) + first_pos[1:]
                    block_4 = chr(ord(first_pos[0]) - 1) + first_pos[1:]
                    first_pos = first_pos[0] + str(int(first_pos[1:]) - 1)
                    if self.search_pos(block_3) is None:
                        second_move.append(chr(ord(first_pos[0]) + 2) + first_pos[1:])
                    if self.search_pos(block_4) is None:
                        second_move.append(chr(ord(first_pos[0]) - 2) + first_pos[1:])

                # Move right
                if ord(first_pos[0]) - ord(its_pos[0]) == 1:
                    first_pos = chr(ord(first_pos[0]) + 1) + first_pos[1:]
                    block_5 = first_pos[0] + str(int(first_pos[1:]) + 1)
                    block_6 = first_pos[0] + str(int(first_pos[1:]) - 1)
                    first_pos = chr(ord(first_pos[0]) + 1) + first_pos[1:]
                    if self.search_pos(block_5) is None:
                        second_move.append(first_pos[0] + str(int(first_pos[1:]) + 2))
                    if self.search_pos(block_6) is None:
                        second_move.append(first_pos[0] + str(int(first_pos[1:]) - 2))

                # Move left
                if ord(first_pos[0]) - ord(its_pos[0]) == -1:
                    first_pos = chr(ord(first_pos[0]) - 1) + first_pos[1:]
                    block_7 = first_pos[0] + str(int(first_pos[1:]) + 1)
                    block_8 = first_pos[0] + str(int(first_pos[1:]) - 1)
                    first_pos = chr(ord(first_pos[0]) - 1) + first_pos[1:]
                    if self.search_pos(block_7) is None:
                        second_move.append(first_pos[0] + str(int(first_pos[1:]) + 2))
                    if self.search_pos(block_8) is None:
                        second_move.append(first_pos[0] + str(int(first_pos[1:]) - 2))

            # Get the last possible route
            last_move = []
            # Gets the valid moves list
            for move in second_move:
                # Check whether it is on the board
                if move in self.get_board_pos():
                    last_move.append(move)

            if end_pos not in second_move:
                return False
            return True

        if piece_role == "Chariot":
            # Gets the current square
            its_pos = piece.get_position()
            # Gets the owner
            player_own = piece.get_player()

            # Checks whether the target square is on the board
            if end_pos not in self.get_board_pos():
                return False

            # Checks the target square is whether occupied
            pos_object = self.search_pos(end_pos)
            if pos_object is not None:
                # If occupied, then checks this piece belongs to which player
                if player_own == pos_object.get_player():
                    # If these two pieces belong to the same player, return False
                    return False

            # In the palace
            case_dic = {1: ["d8", "e9", "f10"], 2: ["d10", "e9", "f8"], 3: ["d1", "e2", "f3"], 4: ["d3", "e2", "f1"]}
            for num in range(1, 5):
                case = case_dic[num]
                if its_pos in case and end_pos in case:
                    if (its_pos == case[0] and end_pos == case[2]) and self.search_pos(case[1]) is not None:
                        return False
                    if (its_pos == case[2] and end_pos == case[0]) and self.search_pos(case[1]) is not None:
                        return False
                    return True

            # Check move
            vertical_lst = []
            horizontal_lst = []
            # Go forward or backward:
            if (ord(end_pos[0]) - ord(its_pos[0])) == 0:
                pos_range = (int(end_pos[1:]) - int(its_pos[1:]))
                # move one step
                if abs(pos_range) == 1:
                    return True
                if pos_range > 0:
                    for num in range(1, pos_range):
                        rows = int(its_pos[1:]) + num
                        position = its_pos[0] + str(rows)
                        vertical_lst.append(position)
                else:
                    for num in range(1, abs(pos_range)):
                        rows = int(its_pos[1:]) - num
                        position = its_pos[0] + str(rows)
                        vertical_lst.append(position)

            # Go left or right
            if (int(end_pos[1:]) - int(its_pos[1:])) == 0:
                pos_range = (ord(end_pos[0]) - ord(its_pos[0]))
                # move one step
                if abs(pos_range) == 1:
                    return True
                if pos_range > 0:
                    for num in range(1, pos_range):
                        columns = ord(its_pos[0]) + num
                        position = chr(columns) + str(its_pos[1:])
                        horizontal_lst.append(position)
                else:
                    for num in range(1, abs(pos_range)):
                        columns = ord(its_pos[0]) - num
                        position = chr(columns) + str(its_pos[1:])
                        horizontal_lst.append(position)

            # Not moving vertically or horizontally
            if vertical_lst == [] and horizontal_lst == []:
                return False

            # Check whether there is a piece between the route
            ver_occupied = []
            hor_occupied = []
            for pos in vertical_lst:
                if self.search_pos(pos) is not None:
                    ver_occupied.append(pos)

            for pos in horizontal_lst:
                if self.search_pos(pos) is not None:
                    hor_occupied.append(pos)

            if ver_occupied == [] and hor_occupied == []:
                return True
            return False

        if piece_role == "Cannon":
            # Gets the current square
            its_pos = piece.get_position()
            # Gets the owner
            player_own = piece.get_player()

            # Checks whether the target square is on the board
            if end_pos not in self.get_board_pos():
                return False

            # Checks the target square is whether occupied
            pos_object = self.search_pos(end_pos)
            if pos_object is not None:
                # If occupied, then checks this piece belongs to which player
                if player_own == pos_object.get_player():
                    # If these two pieces belong to the same player, return False
                    return False
                # The target square cannot be another Cannon
                if pos_object.get_role() == "Cannon":
                    return False

            # In the palace
            case_dic = {1: ["d8", "e9", "f10"], 2: ["d10", "e9", "f8"], 3: ["d1", "e2", "f3"], 4: ["d3", "e2", "f1"]}
            for num in range(1, 5):
                case = case_dic[num]
                if its_pos in case and end_pos in case:
                    if (its_pos == case[0] and end_pos == case[2]) and self.search_pos(case[1]) is not None:
                        return True
                    if (its_pos == case[2] and end_pos == case[0]) and self.search_pos(case[1]) is not None:
                        return True
                    return False

            # Check move
            vertical_lst = []
            horizontal_lst = []
            # Go forward or backward:
            if (ord(end_pos[0]) - ord(its_pos[0])) == 0:
                pos_range = (int(end_pos[1:]) - int(its_pos[1:]))
                if pos_range > 0:
                    for num in range(1, pos_range):
                        rows = int(its_pos[1:]) + num
                        position = its_pos[0] + str(rows)
                        vertical_lst.append(position)
                else:
                    for num in range(1, abs(pos_range)):
                        rows = int(its_pos[1:]) - num
                        position = its_pos[0] + str(rows)
                        vertical_lst.append(position)
            # Go left or right
            if (int(end_pos[1:]) - int(its_pos[1:])) == 0:
                pos_range = (ord(end_pos[0]) - ord(its_pos[0]))
                if pos_range > 0:
                    for num in range(1, pos_range):
                        columns = ord(its_pos[0]) + num
                        position = chr(columns) + str(its_pos[1:])
                        horizontal_lst.append(position)
                else:
                    for num in range(1, abs(pos_range)):
                        columns = ord(its_pos[0]) - num
                        position = chr(columns) + str(its_pos[1:])
                        horizontal_lst.append(position)
            # Not moving vertically or horizontally
            if vertical_lst == [] and horizontal_lst == []:
                return False

            ver_screen = []
            hor_screen = []
            for pos in vertical_lst:
                if self.search_pos(pos) is not None:
                    ver_screen.append(pos)

            for pos in horizontal_lst:
                if self.search_pos(pos) is not None:
                    hor_screen.append(pos)

            # Between two squares can only exist one element
            if len(ver_screen) == 1 and (hor_screen == []):
                for element in ver_screen:
                    # Cannot cross another Cannon
                    if self.search_pos(element).get_role() == "Cannon":
                        return False
                return True
            if (ver_screen == []) and (len(hor_screen) == 1):
                for element in hor_screen:
                    # Cannot cross another Cannon
                    if self.search_pos(element).get_role() == "Cannon":
                        return False
                return True
            return False

        if piece_role == "Soldier":
            # Gets the current square
            its_pos = piece.get_position()
            # Gets the owner
            player_own = piece.get_player()

            # Checks whether the target square is on the board
            if end_pos not in self.get_board_pos():
                return False

            # Checks the target square is whether occupied
            pos_object = self.search_pos(end_pos)
            if pos_object is not None:
                # If occupied, then checks this piece belongs to which player
                if player_own == pos_object.get_player():
                    # If these two pieces belong to the same player, return False
                    return False

            # Check the move
            if (int(its_pos[1:]) - int(end_pos[1:])) == 0:
                if abs(ord(its_pos[0]) - ord(end_pos[0])) == 1:
                    return True
            # They cannot move backward, so find who owns it
            if ord(its_pos[0]) - ord(end_pos[0]) == 0:
                if player_own == "blue":
                    if (int(its_pos[1:]) - int(end_pos[1:])) == 1:
                        return True
                else:
                    if (int(its_pos[1:]) - int(end_pos[1:])) == -1:
                        return True

            # Soldiers may also move one point diagonally "forward" when within the enemy palace
            if its_pos in self.get_palace_all():
                if player_own == "blue":
                    if its_pos == "d3" and end_pos == "e2":
                        return True
                    if its_pos == "f3" and end_pos == "e2":
                        return True
                    if its_pos == "e2" and end_pos == "d1":
                        return True
                    if its_pos == "e2" and end_pos == "f1":
                        return True
                if player_own == "red":
                    if its_pos == "d8" and end_pos == "e9":
                        return True
                    if its_pos == "f8" and end_pos == "e9":
                        return True
                    if its_pos == "e9" and end_pos == "d10":
                        return True
                    if its_pos == "e9" and end_pos == "f10":
                        return True
            return False

    def print_board(self):
        """
        Print out the board.
        """
        rows = [["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1", "i1"],
                ["a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2", "i2"],
                ["a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3", "i3"],
                ["a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4", "i4"],
                ["a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5", "i5"],
                ["a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6", "i6"],
                ["a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7", "i7"],
                ["a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8", "i8"],
                ["a9", "b9", "c9", "d9", "e9", "f9", "g9", "h9", "i9"],
                ["a10", "b10", "c10", "d10", "e10", "f10", "g10", "h10", "i10"]]

        for pos in self.get_board():
            piece = self.get_board()[pos]
            if piece is None:
                pieces = "空"
                color = "white"
            else:
                player = piece.get_player()
                role = piece.get_role()
                if player == "blue":
                    color = "blue"
                else:
                    color = "red"
                # Role
                if role == "General":
                    pieces = "將"
                elif role == "Guard":
                    pieces = "士"
                elif role == "Elephant":
                    pieces = "象"
                elif role == "Horse":
                    pieces = "馬"
                elif role == "Chariot":
                    pieces = "車"
                elif role == "Soldier":
                    pieces = "兵"
                else:
                    pieces = "包"
            # Player

            for num in range(1, 11):
                if int(pos[1:]) == num:
                    for index, position in enumerate(rows[num-1]):
                        if pos == position:
                            rows[num-1][index] = colored(pieces, color)

        columns = ["a", " b", " c", "d", " e", "f", " g", "h", " i"]
        print(" ", *columns, sep=' * ')
        for index, row in enumerate(rows):
            if index == 9:
                print(0, *row, sep=' | ')
            else:
                print((index + 1), *row, sep=' | ')


class Piece:
    """
    Represents piece objects on the board.
    """

    def __init__(self, player, position):
        """
        Creates an piece object with different private data members and initializes all data members.
        """
        self._player = player
        self._position = position

    def get_player(self):
        """
        Returns the player who owns this piece.
        """
        return self._player

    def get_position(self):
        """
        Returns the current position.
        """
        return self._position

    def set_position(self, new_pos):
        """
        Takes a new position as a parameter.
        Sets to the new position.
        """
        self._position = new_pos


class General(Piece):
    """
    Represents a General.
    Inherits from Piece.
    """

    def __init__(self, player, position):
        super().__init__(player, position)
        self._role = "General"

    def get_role(self):
        """
        Returns the piece's role.
        """
        return self._role


class Guard(Piece):
    """
    Represents a Guard.
    Inherits from Piece.
    """

    def __init__(self, player, position):
        super().__init__(player, position)
        self._role = "Guard"

    def get_role(self):
        """
        Returns the piece's role.
        """
        return self._role


class Horse(Piece):
    """
    Represents a Horse.
    Inherits from Piece.
    """

    def __init__(self, player, position):
        super().__init__(player, position)
        self._role = "Horse"

    def get_role(self):
        """
        Returns the piece's role.
        """
        return self._role


class Elephant(Piece):
    """
    Represents an Elephant.
    Inherits from Rectangle
    """

    def __init__(self, player, position):
        super().__init__(player, position)
        self._role = "Elephant"

    def get_role(self):
        """
        Returns the piece's role.
        """
        return self._role


class Chariot(Piece):
    """
    Represents a Chariot.
    Inherits from Piece.
    """

    def __init__(self, player, position):
        super().__init__(player, position)
        self._role = "Chariot"

    def get_role(self):
        """
        Returns the piece's role.
        """
        return self._role


class Cannon(Piece):
    """
    Represents a Cannons.
    Inherits from Piece.
    """

    def __init__(self, player, position):
        super().__init__(player, position)
        self._role = "Cannon"

    def get_role(self):
        """
        Returns the piece's role.
        """
        return self._role


class Soldier(Piece):
    """
    Represents a Soldier.
    Inherits from Piece.
    """

    def __init__(self, player, position):
        super().__init__(player, position)
        self._role = "Soldier"

    def get_role(self):
        """
        Returns the piece's role.
        """
        return self._role


class Blue:
    """
    Represents a blue player.
    """
    def __init__(self):
        """
        Creates a blue player object with different private data members and initializes all data members.
        """
        self._player = "blue"
        # Initializes the in check status to False
        self._in_check = False
        # Initializes the dictionary used to track the player's remaining pieces to the initial setup
        self._remain_piece = {"Chariot1": "a10", "Elephant1": "b10", "Horse1": "c10", "Guard1": "d10", "General": "e9",
                              "Guard2": "f10", "Elephant2": "g10", "Horse2": "h10", "Chariot2": "i10", "Cannon1": "b8",
                              "Cannon2": "h8", "Soldier1": "a7", "Soldier2": "c7", "Soldier3": "e7", "Soldier4": "g7",
                              "Soldier5": "i7"}

    def get_player(self):
        """
        Returns the player's identity.
        """
        return self._player

    def get_in_check(self):
        """
        Returns the player's in check status.
        """
        return self._in_check

    def set_in_check(self, status):
        """
        Takes one parameter.
        Sets the player's in check status to the new status.
        """
        self._in_check = status

    def get_remain_piece(self):
        """
        Returns the player's remaining pieces dictionary.
        """
        return self._remain_piece

    def remove_piece(self, piece):
        """
        Takes a parameter that represents the piece object.
        According to its position to remove the piece from the remaining piece dictionary.
        """
        position = piece.get_position()
        # Notice: RuntimeError-dictionary changed size during iteration (Use list to solve)
        for role, pos in list(self._remain_piece.items()):
            if pos == position:
                del self._remain_piece[role]

    def update_position(self, piece, end_pos):
        """
        Takes two parameters that represent the piece object and the square.
        Updates the player's pieces' position.
        """
        position = piece.get_position()
        for role, pos in list(self._remain_piece.items()):
            if pos == position:
                self._remain_piece[role] = end_pos

    def restore_removed(self, piece, pos):
        """
        Takes two parameters that represent the piece object and the square.
        Add back the piece that being removed.
        """
        role = piece.get_role
        self._remain_piece[role] = pos


class Red:
    """
    Represents a red player.
    """
    def __init__(self):
        """
        Creates a red player object with different private data members and initializes all data members.
        """
        self._player = "red"
        # Initializes the in check status to False
        self._in_check = False
        # Initializes the dictionary used to track the player's remaining pieces to the initial setup
        self._remain_piece = {"Chariot1": "a1", "Elephant1": "b1", "Horse1": "c1", "Guard1": "d1", "General": "e2",
                              "Guard2": "f1", "Elephant2": "g1", "Horse2": "h1", "Chariot2": "i1", "Cannon1": "b3",
                              "Cannon2": "h3", "Soldier1": "a4", "Soldier2": "c4", "Soldier3": "e4", "Soldier4": "g4",
                              "Soldier5": "i4"}

    def get_player(self):
        """
        Returns the player's identity.
        """
        return self._player

    def get_in_check(self):
        """
        Returns the player's in check status.
        """
        return self._in_check

    def set_in_check(self, status):
        """
        Takes one parameter.
        Sets the player's in check status to the new status.
        """
        self._in_check = status

    def get_remain_piece(self):
        """
        Returns the player's remaining pieces dictionary.
        """
        return self._remain_piece

    def remove_piece(self, piece):
        """
        Takes a parameter that represents the piece object.
        According to its position to remove the piece from the remaining piece dictionary.
        """
        position = piece.get_position()
        # Notice: RuntimeError-dictionary changed size during iteration (Use list to solve)
        for role, pos in list(self._remain_piece.items()):
            if pos == position:
                del self._remain_piece[role]

    def update_position(self, piece, end_pos):
        """
        Takes two parameters that represent the piece object and the square.
        Updates the player's pieces' position.
        """
        position = piece.get_position()
        for role, pos in list(self._remain_piece.items()):
            if pos == position:
                self._remain_piece[role] = end_pos

    def restore_removed(self, piece, pos):
        """
        Takes two parameters that represent the piece object and the square.
        Add back the piece that being removed.
        """
        role = piece.get_role
        self._remain_piece[role] = pos


if __name__ == '__main__':
    # Example Game - Red Wins 
    game = JanggiGame()
    print(game.make_move("c7", "c6"))  # Soldier (blue)
    print(game.make_move("c1", "d3"))  # Horse (red)
    print(game.make_move("b10", "d7"))  # Elephant (blue)
    print(game.make_move("b3", "e3"))  # Cannon (red)
    print(game.make_move("c10", "d8"))  # Horse (blue)
    print(game.make_move("h1", "g3"))  # Horse (red)
    print(game.make_move("e7", "e6"))  # Soldier (blue)
    print(game.make_move("e3", "e6"))  # Cannon (red) eat blue solider
    game.print_board()

    print(game.make_move("h8", "c8"))  # Cannon (blue)
    print(game.make_move("d3", "e5"))  # Horse (red)
    print(game.make_move("c8", "c4"))  # Cannon (blue) eat red soldier # c4 soldier

    print(game.make_move("e5", "c4"))  # Horse (red) eat blue Cannon

    print(game.make_move("i10", "i8"))  # Chariot (blue)
    print(game.make_move("g4", "f4"))  # Solider (red)
    print(game.make_move("i8", "f8"))  # Chariot (blue)
    print(game.make_move("g3", "h5"))  # Horse (red)
    print(game.make_move("h10", "g8"))  # Horse (blue)
    print(game.make_move("e6", "e3"))  # Cannon (red) "in check" Blue general
    print("Blue should in check: " + str(game.is_in_check("blue")))   # True
    game.print_board()

    print(game.make_move("f8", "f8"))  # In check cannot pass False!!
    print(game.make_move("a7", "a6"))  # Is already being in check, should move-> False

    print(game.make_move("f8", "e8"))  # Escapes from being in check by moving by other pieces Chariot (blue)
    print("Blue should not in check (print False): " + str(game.is_in_check("blue")))   # False
    game.print_board()

    print(game.make_move("e3", "e8"))  # Cannon (red) Eat blue Chariot
    print(game.make_move("e9", "e8"))  # General (blue) eat red Cannon
    print(game.make_move("h5", "g7"))  # Horse (red) eat blue Soldier and "in check" blue
    print("Blue should in check: " + str(game.is_in_check("blue")))   # True
    game.print_board()

    print(game.make_move("d7", "f4"))  # False!! Should move away in check

    print(game.make_move("e8", "f8"))  # General (blue)
    print(game.make_move("a1", "a3"))  # Chariot (red)
    print(game.make_move("c6", "c5"))  # Soldier (blue)
    print(game.make_move("a3", "d3"))  # Chariot (red)
    print(game.make_move("d7", "f4"))  # Elephant (blue)
    print(game.make_move("d3", "d8"))  # Chariot (red) Eat blue Horse and in check blue
    print("Blue should in check: " + str(game.is_in_check("blue")))   # True
    game.print_board()

    print(game.make_move("f8", "f9"))  # General (blue)
    print("Blue should not in check (print False): " + str(game.is_in_check("blue")))   # False
    game.print_board()

    print(game.make_move("g7", "e8"))  # Horse (red)

    print(game.make_move("b8", "e8"))  # Cannon (blue) Eat red Horse in check red

    print("Red should in check: " + str(game.is_in_check("red")))   # True
    game.print_board()

    print(game.make_move("d8", "e8"))  # Chariot (red) Eat blue Cannon
    print("Red should not in check (print False): " + str(game.is_in_check("red")))   # False
    game.print_board()

    print(game.make_move("c5", "c4"))  # Soldier (blue) Eat red Horse
    print(game.make_move("e8", "g8"))  # Chariot (red) Eat blue Horse
    print(game.make_move("g10", "e7"))  # Elephant (blue)
    print(game.make_move("e4", "f4"))  # Soldier (red) Eat blue Elephant

    print(game.make_move("a10", "b10"))  # Chariot (blue)
    print(game.make_move("g8", "g10"))  # Chariot (red)
    print(game.make_move("e7", "h9"))  # Elephant (blue)
    print(game.make_move("h3", "h10"))  # Cannon (red)
    print(game.make_move("b10", "b1"))  # Chariot (blue) eat red Elephant

    print(game.make_move("i1", "h1"))  # Chariot (red)
    print(game.make_move("c4", "c3"))  # Soldier (blue)
    print(game.make_move("h1", "h9"))  # Chariot (red) eat blue elephant in check
    print("Blue should in check: " + str(game.is_in_check("blue")))   # True
    game.print_board()

    print(game.make_move("f9", "f8"))  # General (blue) escape
    print("Blue should not in check (print False): " + str(game.is_in_check("blue")))
    game.print_board()

    print(game.make_move("h10", "f10"))  # Cannon (red) eat blue Guard
    print(game.make_move("b1", "b9"))  # Chariot (blue)

    print(game.make_move("h9", "b9"))  # Chariot (red) eat blue Chariot
    print("Blue should not in check (print False): " + str(game.is_in_check("blue")))   # False
    game.print_board()

    print(game.make_move("c3", "c2"))  # Soldier (blue)

    print(game.make_move("g10", "g8"))  # Cannon (red) checkmate
    game.print_board()

    print("Blue should in check: " + str(game.is_in_check("blue")))   # True
    game.print_board()

    print(game.get_game_state())  # Red Wins

    # Game over
    print(game.make_move("f8", "e8"))  # General (blue)
    print(game.make_move("c2", "c1"))  # Soldier (blue))
