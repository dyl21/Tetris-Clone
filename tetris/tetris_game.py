# Tetris Clone Puzzle Game
# By Dan and Jenny
# Made with Pygame

import pygame
from pygame import mixer
import random

# creating the data structure for pieces
# setting up global vars
# functions
# - create_grid
# - draw_grid
# - draw_window
# - rotating shape in main
# - setting up the main

pygame.font.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()

# GLOBALS VARS
screen_width = 800
screen_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 20 height per block
block_size = 30
level = 1

top_left_x = (screen_width - play_width) // 2
top_left_y = screen_height - play_height

# MUSIC SECTION
pygame.mixer.music.load('music/01Pondering.wav')
pygame.mixer.music.play(-1, 0.0, 49000)

# SHAPE FORMATS

S = [['.....',
      '......',
      '..00..',
      '.00...',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes_list = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]


# index 0 - 6 represent shape
class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes_list.index(shape)]
        self.rotation = 0  # When clicking Up, add 1 to this for every rotation


def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for x in range(10)] for _ in range(20)]
    # Create 1 list for every row in grid, 20 rows, 20 sublists. At each sublist has 10 colors, 10 squares in each row,
    # 20 rows

    for row_val in range(len(grid)):  # i in the video
        for col_val in range(len(grid[row_val])):  # j in the video
            if (col_val, row_val) in locked_positions:
                key_val = locked_positions[(col_val, row_val)]
                grid[row_val][col_val] = key_val

    return grid


def convert_shape_format(shape):
    """Converts the shape and formats it based on if 0 is in each shape position and adds it to the list"""
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':  # Check if 0 exists in each position
                positions.append((shape.x + j, shape.y + i))  # Add position to list

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(shape, grid):
    """Takes all positions in list, adds it to the accepted position, and converts its position"""
    accepted_position = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_position = [j for sub in accepted_position for j in sub]

    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_position:
            if pos[1] > -1:  # Makes shape not spawn at top of screen; checks valid position
                return False
    return True


def check_lost(positions):
    """Checks if any positions are above the screen"""
    for pos in positions:
        x, y = pos
        if y < -1:
            return True

    return False


def get_shape():
    return Piece(5, -1, random.choice(shapes_list))
    # First two vals are x and y coords, start with y = -1 so its above the screen


def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont("retro", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2),
                         top_left_y + play_height / 2 - label.get_height() / 2))


def draw_grid(surface, row, col):  # Draws lines for the grid
    start_x = top_left_x
    start_y = top_left_y

    for row_val in range(row):
        pygame.draw.line(surface, (128, 128, 128), (start_x, start_y + row_val * block_size),
                         (start_x + play_width, start_y + row_val * block_size))
        for col_val in range(col):
            pygame.draw.line(surface, (128, 128, 128), (start_x + col_val * block_size, start_y),
                             (start_x + col_val * block_size, start_y + play_height))


def clear_rows(grid, locked):
    """Loops the grid backwards and sets all rows in grid to be cleared if 0, 0, 0 does not exist by getting
    every position in the row. Locks the position that needs to be deleted and deletes it. Row gets shifted
    and new row gets added."""
    increment = 0
    for i in range(len(grid) - 1, -1, -1):  # loops grid backwards
        row = grid[i]
        if (0, 0, 0) not in row:
            increment += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue

    if increment > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[:: -1]:  # don't overwrite existing rows
            x, y = key
            if y < ind:
                newKey = (x, y + increment)  # shifts everything down a position when row gets deleted
                locked[newKey] = locked.pop(key)  # uses new key

    return increment


def draw_next_shape(shape, surface):
    """Makes the next shape in the game appear on screen"""
    font = pygame.font.SysFont('retro', 30)
    next_shape_label = font.render('Next Shape:', 1, (255, 255, 255))
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color,
                                 (sx + j * block_size, sy + i * block_size, block_size, block_size), 0)

        surface.blit(next_shape_label, (sx + 10, sy - 30))


def saved_shape(surface):
    font = pygame.font.SysFont('retro', 30)
    swap_shape_label = font.render('Saved Shape:', 1, (255, 255, 255))
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    surface.blit(swap_shape_label, (sx + -10, sy - 30))
    return get_shape()


def max_score():
    with open('scores.txt', 'r') as file:
        lines = file.readlines()
        score = lines[0].strip()

    return score


def update_score(n_score):
    score = max_score()

    with open('scores.txt', 'w') as file:
        if int(score) > n_score:
            file.write(str(score))
        else:
            file.write(str(n_score))

    # Look to add previous and high score on screen


def draw_window(surface, grid, score=0, high_score=0, level=0):
    surface.fill((0, 0, 0))

    # Level label
    pygame.font.init()
    font = pygame.font.SysFont('retro', 60)
    level_label = font.render(f'Level: {level}', 1, (255, 255, 255))  # (Name, anti-aliasing, color)
    surface.blit(level_label, (top_left_x + play_width / 2 - (level_label.get_width() / 2), 30))

    # Current score
    font = pygame.font.SysFont('retro', 30)
    score_label = font.render('Score: ' + str(score), 1, (255, 255, 255))
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    surface.blit(score_label, (sx + 20, sy - 150))

    # high score
    high_score_label = font.render('High Score: ' + str(high_score), 1, (255, 255, 255))
    h_sx = top_left_x + 350
    h_sy = top_left_y + 300
    surface.blit(high_score_label, (h_sx + 20, h_sy + 160))

    for row_val in range(len(grid)):
        for col_val in range(len(grid[row_val])):
            pygame.draw.rect(surface, grid[row_val][col_val], (top_left_x + col_val * block_size, top_left_y + row_val *
                                                               block_size, block_size, block_size), 0)

    draw_grid(surface, 20, 10)
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)


# def game_state():
#     """Creates the basis for game stage levels"""
#     def __init__(self):
#         self.state = 'level_1'
#
#     def level_1(self):
# insert the code that draws the game to screen


def main(window):
    high_score = max_score()
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    level_time = 0
    score = 0

    while run:
        grid = create_grid(locked_positions)  # Constantly update grid
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        if level_time / 1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True  # Stop moving piece when it hits bottom of screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.x += 1

                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.x -= 1

                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.y -= 1

                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.rotation -= 1

                if event.key == pygame.K_SLASH:
                    saved_shape(window)

        shape_pos = convert_shape_format(current_piece)  # Checks all positions of pieces

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color  # Update color of grid
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            rows_cleared = clear_rows(grid, locked_positions)
            if rows_cleared == 1:
                score += 80
            elif rows_cleared == 2:
                score += 200
            elif rows_cleared == 3:
                score += 600
            elif rows_cleared == 4:
                score += 2400

        draw_window(window, grid, score, high_score, level)
        draw_next_shape(next_piece, window)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle("GAME OVER!", 80, (255, 255, 255), window)
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            update_score(score)


def main_menu(window):
    run = True
    while run:
        window.fill((0, 0, 0))
        draw_text_middle("Press any key to play", 60, (255, 255, 255), window)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                main(window)

    pygame.display.quit()


window = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Tetris')
main_menu(window)  # start game
