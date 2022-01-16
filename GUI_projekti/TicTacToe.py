""""
TIE-02100 Johdatus ohjelmointiin, kesä 2020
TIE-02106 Introduction to Programming, Summer 2020
Mikael U

GUI-project:
- Classic game of Tic-Tac-Toe
- 2 players (determined in global constant PLAYER_COUNT)
- Upon starting, game asks for names. Empty names or names containing only
  whitespace/s aren't allowed. Everything else goes.
- After confirming names, select a grid size from given options and confirm.
  This will initiate the game.

  GAMEPLAY:
- Players take turns in placing their marks on game board. Mark must be placed
  in an empty slot.
- Winner is whoever forms a connected chain with their own mark from one side
  of the game board to the other, as in full row, full column or 
  full diagonal.
- After game ends, it is possible to continue with same players by
  selecting desired grid size and confirming it again.
- Game will keep track of won rounds and present them in the right side
  of the screen.

  MISC:
- "Reset all" will reset program to its initial state

!Attempted level == Scalable Interface!
- Tried to make the code so that theoretically it would be scalable for any
    amount of players, grid sizes, etc...
"""

from tkinter import *
import random
import time

PLAYER_COUNT = 2

# First grid is always 3x3, where dimension is 3. For every consecutive
# option, we increase dimension by 2. So, with BOARD_OPTIONS = 3, we get
# 3x3, 5x5 and 7x7 grid size options.
BOARD_OPTIONS = 3
INITIAL_DIMENSION = 3

# Images to place on clicked buttons.
PLAYER_MARKS = ["circle.gif", "cross.gif"]
WINNER_MARKS = ["win_circle.gif", "win_cross.gif"]


class Player:
    """An object is formed for each player. Maintains id, name and wins.
    Can return all of them."""
    def __init__(self):
        self.__id = 0
        self.__name = ""
        self.__wins = 0

    def set_id(self, number):
        self.__id = number

    def return_id(self):
        return self.__id

    def name(self, name):
        self.__name = name

    def return_name(self):
        return self.__name

    def add_win(self):
        self.__wins += 1

    def return_wins(self):
        return self.__wins


class Tictactoe:
    def __init__(self):
        self.__window = Tk()
        self.__window.title("Tic-Tac-Toe")
        self.__list_of_players = []
        self.__list_of_marks = []
        self.__winning_marks = []
        self.__winner_lane = []

        # Lists for inspecting every possible winning combinations
        self.__horizontal_list = []
        self.__vertical_list = []
        self.__diagonal_list = []
        self.__reverse_diagonal_list = []

        # Initially the first player is chosen randomly. After that we
        # make sure players take turns in starting the game, if consecutive
        # games are played.
        self.__initial_turn = random.randint(0, PLAYER_COUNT - 1)
        self.__turn = self.__initial_turn

        # Coordinates will be used to
        self.__x_coord = 0
        self.__y_coord = 0

        # Form lists of PhotoImages for regular player marks and special marks
        # which are to be used after someone wins the game
        for file in PLAYER_MARKS:
            pic = PhotoImage(file=file)
            self.__list_of_marks.append(pic)

        for file in WINNER_MARKS:
            pic = PhotoImage(file=file)
            self.__winning_marks.append(pic)

        self.__empty_pic = PhotoImage(file="empty.gif")

        # Trying to make this a scalable interface. We utilize a variable that
        # stores the current value to be used for elements in
        # .configure(row=...). This way we can take any amount of players
        # or grid options and still make sure that all elements align
        # one after each other.
        self.__dynamic_y = 1

        # Various labels to present message/data will be used
        self.__name_header = Label(self.__window, text="Enter names below")

        # Buttons to confirm the name entries and grid size selection
        self.__accept_dimension = Button(self.__window, text="Confirm grid",
                                         command=self.generate_board,
                                         state=DISABLED)
        self.__accept_names = Button(self.__window, text="Confirm names",
                                     command=self.get_names, state=NORMAL)

        self.__name_entry_list = []
        for i in range(PLAYER_COUNT):
            """Function generates a GUI-element Entry for each player
            and stores them in the list. I want this to be the first element
            to be added to GUI, so we put them into .grid as well. Using
            dynamic_y (aka. increasing row-value) for each Entry-element."""
            self.__dynamic_y += 1

            label_text = "Player {:d}:".format(i+1)
            self.__name_label = Label(self.__window, text=label_text)
            self.__name_label.grid(row=self.__dynamic_y, column=1, sticky=W)

            self.__player_name = Entry(self.__window, width=10, state=NORMAL)
            self.__player_name.grid(row=self.__dynamic_y, column=2, sticky=W,
                                    padx=10)
            self.__name_entry_list.append(self.__player_name)

        # After Entries are added, we can button to accept names and increase
        # dynamic_y.
        self.__accept_names.grid(row=self.__dynamic_y + 1, column=1, padx=20,
                                 pady=5,sticky=N, columnspan=2)
        self.__dynamic_y += 1

        self.__board_buttons = []
        self.__score_labels = []

        self.__list_of_grids = []

        # We will inspect the lists within this dict when checking if game
        # has been won.
        self.__winning_lanes = {"horizontal": self.__horizontal_list,
                                "vertical": self.__vertical_list,
                                "diagonal": self.__diagonal_list,
                                "rev_diagonal": self.__reverse_diagonal_list}

        # Tie choice = IntVar() as variable to all radiobuttons.
        self.__choice = IntVar()
        grid_dim = INITIAL_DIMENSION
        self.__radio_buttons = []
        for i in range(BOARD_OPTIONS):
            """Generate a radio button (in hopes of extra points, obviously!)
            for each board option. Default is 3 options. Append radio buttons
            to list and add them to the grid."""
            self.__dynamic_y += 1
            dim_str = str(grid_dim)
            grid_text = dim_str + " x " + dim_str
            new_button = Radiobutton(self.__window, text=grid_text,
                                     variable=self.__choice, value=grid_dim,
                                     command=self.radio_button_clicked, pady=5,
                                     state=DISABLED)

            new_button.grid(row=self.__dynamic_y, column=1, sticky=N,
                            columnspan=2)
            self.__radio_buttons.append(new_button)
            grid_dim += 2

        self.__dynamic_y += 1

        # After Entries are added, we can place button to accept dimension and
        # increase dynamic_y.
        self.__accept_dimension.grid(row=self.__dynamic_y, column=1, padx=20,
                                     pady=5,
                                     columnspan=2, sticky=N)
        self.__dynamic_y += 1

        # Finally, at the bottom of the left hand size, we add buttons for
        # resetting the program and closing it.
        self.__reset_button = Button(self.__window, text="Reset all",
                                     command=self.reset_game)
        self.__exit_button = Button(self.__window, text="Exit game",
                                    command=self.__window.destroy)
        self.__reset_button.grid(row=self.__dynamic_y, column=2, columnspan=1,
                                 sticky=E, padx=5)
        self.__exit_button.grid(row=self.__dynamic_y, column=1, columnspan=1,
                                padx=5)

        self.__name_header.grid(row=1, column=1, sticky=N, columnspan=2)
        self.__status_label = Label(self.__window, text="Game status")
        self.__turn_label = Label(self.__window)
        self.__misc_label = Label(self.__window)

    def start(self):
        """Name speaks for itself, will start our mainloop."""
        self.__window.mainloop()

    def radio_button_clicked(self):
        """Upon selecting any of the radio buttons representing grid
        dimensions, we can activate the "Confirm"-button"""

        self.__accept_dimension.configure(state=NORMAL)

    def clear_score_and_board(self, reset="no"):
        """ Will clean lists of score labels and buttons, which will need to
        be re-drawn for next round. If game is reset, will also delete all
        player objects from list.

        params:
        reset="no": If game is fully reset, give value "yes" to delete all
              existing players
        """
        if reset == "yes":
            for x in self.__list_of_players:
                del x
            self.__list_of_players.clear()

        if self.__board_buttons:
            for x in self.__score_labels:
                x.destroy()
        self.__score_labels.clear()

        if self.__board_buttons:
            for x in self.__board_buttons:
                for button in x:
                    button.destroy()
        self.__board_buttons.clear()

    def generate_board(self):
        """Generate game grid after choosing grid size. This will be called
        for each consecutive game, so clear label text, scores and board
        as well before remaking everything."""
        self.__misc_label.configure(text="")
        self.clear_score_and_board()
        self.__accept_dimension.configure(state=DISABLED)
        dimension = self.__choice.get()

        # Disable all radio buttons
        self.change_radio_buttons(DISABLED)

        # Store column value inside for loop, so we can place our labels
        # to the right side of game grid after all buttons are generated.
        store_column = 0

        # Make a dimension x dimension list to represent game grid and
        # populate it with buttons
        for i in range(0, dimension, 1):
            self.__board_buttons.append([])
            for j in range(0, dimension, 1):
                new_button = Button(self.__window, image=self.__empty_pic)
                new_button.grid(row=3 + i, column=3 + j, padx=1,
                                pady=1)

                self.__status_label.grid(row=2, column=4+j, columnspan=3)
                self.__turn_label.grid(row=4, column=4 + j, columnspan=3)
                self.__misc_label.grid(row=3, column=4 + j, columnspan=3)

                new_button.configure(command=self.move_callback(i, j))
                self.__board_buttons[i].append(new_button)

                store_column = 4 + j

        # Add labels to the right hand side of game grid. Again, should be
        # done in a scalable fashion.
        self.make_score_label(5, store_column)
        self.update_turn_label()

    def make_score_label(self, ro, col):
        """Form labels for each player's score (scalable) to the right side
        of the game grid.
        params:
        ro = row, where we start adding labels
        col = column, where we start adding labels"""
        for x in self.__list_of_players:
            player_id = x.return_id()
            player_wins = x.return_wins()
            player_name = x.return_name()

            string = "Total wins for Player {:d}({:s}): {:d}".\
                format(player_id + 1, player_name, player_wins)

            score_label = Label(self.__window, text=string)
            score_label.grid(row=ro, column=col)
            self.__score_labels.append(score_label)

            ro += 1

    def move_callback(self, x, y):
        """Called when clicking a button in grid. Tying a function to a button
        and to give it 2 parameters proved to be a bit tricky, so here is my
        workaround.
        param:
        x and y: coordinates, so we can locate button in list within a list.
        """
        return lambda: self.make_move(x, y)

    def update_turn_label(self):
        """Update turn label, used after each turn."""
        player = self.__turn
        name = self.__list_of_players[player].return_name()
        string = "Player {:d}({:s}), your turn!".format(player + 1, name)
        self.__turn_label.configure(text=string, fg="blue")

    def update_wins(self):
        """Win labels represent the wins-variable from class Player.
        Find wins for each player and show them in labels."""
        for x in range(len(self.__list_of_players)):
            player_id = self.__list_of_players[x].return_id()
            player_wins = self.__list_of_players[x].return_wins()
            player_name = self.__list_of_players[x].return_name()

            string = "Total wins for Player {:d}({:s}): {:d}". \
                format(player_id + 1, player_name, player_wins)
            self.__score_labels[x].configure(text=string)

    def get_names(self):
        """Monitor the name entry fields and take names when all of them are
        acceptable."""

        # Name needs to be not empty nor full of whitespace.
        for x in self.__name_entry_list:
            if not x.get().strip():
                self.__name_header.configure(text="No empty names pffff!")
                self.__window.update_idletasks()
                time.sleep(2)
                self.__name_header.configure(text="Enter names below")
                return

        # When all names are acceptable, go through them and make class Player
        # objects, which are added to list.
        for x in range(len(self.__name_entry_list)):
            person = self.__name_entry_list[x]
            person.configure(state=DISABLED)

            new_player = Player()
            new_player.name(person.get().strip())
            new_player.set_id(x)
            self.__list_of_players.append(new_player)

        # After names are accepted, disable name buttons and enable
        # radiobuttons for choosing grid size.
        self.__accept_names.configure(state=DISABLED)
        self.change_radio_buttons(NORMAL)

    def check_lanes(self, button, player_id, player_number):
        """Check all possible winning lines when a button is pressed. Also
        determine whether we are having a tie or not.
        params:
        button: the pressed button
        player_id: id used to find player object
        player_number: Player1, 2, 3, etc..."""
        is_a_tie = True
        dimension = self.__choice.get()

        # Find coordinates for pressed button
        for i in range(dimension):
            for j in range(dimension):
                if self.__board_buttons[j][i] == button:
                    self.__x_coord = i
                    self.__y_coord = j

        self.__horizontal_list.clear()
        self.__vertical_list.clear()
        self.__diagonal_list.clear()
        self.__reverse_diagonal_list.clear()

        # Idea is to have a list for every possible winning combination
        # for that particular button. Add buttons to list if condition is met.
        # Later, if one list has the length of dimension, we know it is a win.
        for i in range(dimension):
            button_hor = self.__board_buttons[self.__y_coord][i]
            if button_hor['text'] == player_id:
                self.__horizontal_list.append(button_hor)

            button_ver = self.__board_buttons[i][self.__x_coord]
            if button_ver['text'] == player_id:
                self.__vertical_list.append(button_ver)

            button_diagonal = self.__board_buttons[i][i]
            if button_diagonal['text'] == player_id:
                self.__diagonal_list.append(button_diagonal)

            button_reverse_diagonal = self.__board_buttons[dimension - 1 - i][i]
            if button_reverse_diagonal['text'] == player_id:
                self.__reverse_diagonal_list.append(button_reverse_diagonal)

        # Check for tie. If even one button is still NORMAL, it is not a tie.
        for x in self.__board_buttons:
            for button in x:
                if button['state'] == NORMAL:
                    is_a_tie = False

        # If player wins or it is a tie, start new game. Else, keep going.
        if self.did_player_win(dimension, player_number):
            self.highlight_lane()
            self.start_next_game()
            self.__misc_label.configure(
                text="Choose grid for a new game!", fg="red")

        elif is_a_tie:
            self.__misc_label.configure(
                text="Choose grid for a new game!", fg="red")

            self.start_next_game()
            self.__turn_label.configure(text="It is a tie!", fg="red")

        else:
            self.__turn = (self.__turn + 1) % PLAYER_COUNT
            self.update_turn_label()

    def did_player_win(self, dimension, player_number):
        """Inspect if player won a game after their last move. If any of the
        possible winning lane lists reached length of dimension, player has
        won. Add a win, disable buttons and return True.
        params:
        dimension: dimension of grid
        player_number: Player1, 2, 3, etc..."""
        player = self.__list_of_players[player_number]

        for x in self.__winning_lanes:
            if len(self.__winning_lanes[x]) == dimension:
                for i in range(dimension):
                    for button in self.__board_buttons[i]:
                        button.configure(state=DISABLED)

                self.__list_of_players[player_number].add_win()
                win_string = "Player {:d}({:s}) won the match!".\
                    format(player. return_id() + 1, player.return_name())
                self.__turn_label.configure(text=win_string, fg="green")

                self.update_wins()
                self.__winner_lane = self.__winning_lanes[x]
                return True

    def highlight_lane(self):
        """After winning a game, the winner lane gets highlighted with
        different image."""
        winner_mark = self.__winning_marks[self.__turn]
        for button in self.__winner_lane:
            button.configure(image=winner_mark)
            self.__window.update_idletasks()
            time.sleep(0.30)

    def start_next_game(self):
        """After game is over, give the possibility to choose different grid
        size."""
        self.__choice.set(NONE)
        self.__initial_turn = (self.__initial_turn + 1) % PLAYER_COUNT
        self.__turn = self.__initial_turn
        self.change_radio_buttons(NORMAL)

    def make_move(self, x, y):
        """Find whose turn it is. Then change icon and disable button based
        on which button was pressed.
        params:
        x and y: button coordinates, can find button from list."""
        player_number = self.__turn
        player_id = str(self.__list_of_players[player_number].return_id())

        mark = self.__list_of_marks[player_number]
        button = self.__board_buttons[x][y]
        button.configure(state=DISABLED, image=mark, text=player_id,
                         relief='sunken')
        self.check_lanes(button, player_id, player_number)

    def reset_game(self):
        """Reset the game to the same view than you would see when first
        running the program"""
        self.start_next_game()
        self.change_radio_buttons(DISABLED)
        self.change_name_entries()
        self.__accept_dimension.configure(state=DISABLED)
        self.__accept_names.configure(state=NORMAL)
        self.clear_score_and_board("yes")
        self.__turn_label.configure(text="")
        self.__status_label.configure(text="")
        self.__misc_label.configure(text="")

    def change_radio_buttons(self, cmd):
        """Enable or disable radio buttons.
        cmd: either normal or disabled."""
        for x in self.__radio_buttons:
            x.configure(state=cmd)

    def change_name_entries(self):
        """Activate the name entry fields and delete the names from them."""
        for name in self.__name_entry_list:
            name.configure(state=NORMAL)
            name.delete(0, END)


def main():
    # Start the mainloop
    game = Tictactoe()
    game.start()


main()



