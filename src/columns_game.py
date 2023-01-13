# Columns Pygame UI

# TODO:
    # Game Over Screen - handle scenarios/errors

import pygame
import columns
import random
from collections import namedtuple


_FRAME_RATE = 30
_GAME_SPEED = 30

JEWEL_IMAGES = [
    'ruby', 'sapphire', 'emerald',
    'diamond', 'pearl',
    'amethyst', 'topaz'
    ]

BorderStyle = namedtuple('BorderStyle', 'color thickness')


_FIELD_ROWS = 13
_FIELD_COLS = 6


_INITIAL_WIDTH = 360
_INITIAL_HEIGHT = _INITIAL_WIDTH * _FIELD_ROWS / _FIELD_COLS

_BACKGROUND_COLOR = pygame.Color(0, 34, 64)


class ColumnsGame:
    def __init__(self):
        self._running = True
        self._game_over = False
        self._state = columns.GameState(_FIELD_ROWS, _FIELD_COLS)
        self._game_tick = _GAME_SPEED


    def run(self) -> None:
        pygame.init()

        try:
            clock = pygame.time.Clock()

            self._jewel_images = []
            for img in JEWEL_IMAGES:
                self._jewel_images.append(
                    pygame.image.load(img + '.png')
                    )

            self._create_display((_INITIAL_WIDTH, _INITIAL_HEIGHT))

            while self._running:
                clock.tick(_FRAME_RATE)

                self._redraw()

                try:
                    self._update()
                except columns.GameOver:
                    self._end_game()
                

        finally:
            pygame.quit()


    def _update(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._end_game()
                self._end_program()
            if event.type == pygame.KEYDOWN:
                if not self._game_over:
                    self._handle_keys()

        if not self._game_over:
            self._handle_time()
            self._handle_faller_creation()


    def _handle_time(self) -> None:
        self._game_tick -= 1
        
        if self._game_tick == 0:
            self._state.handle_time()
            self._game_tick = _GAME_SPEED


    def _handle_faller_creation(self) -> None:
        if self._state.get_faller_position() == None:
            if not self._state.match_exists():
                self._state.update_faller()
                
                field = self._state.field()
                available_cols = []
                for col in range(field.cols()):
                    pos = columns.Position(0, col)
                    if field.is_empty_space(pos):
                        available_cols.append(col)

                if len(available_cols) == 0:
                    self._end_game()
                    return

                random_col_index = random.randint(
                    0, len(available_cols) - 1)
                random_col = available_cols[random_col_index]
            
                self._state.drop_faller(random_col + 1)


    def _handle_keys(self) -> None:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:
            if self._state.get_faller_position() != None:
                self._state.rotate_faller()
        if keys[pygame.K_LEFT]:
            if self._state.get_faller_position() != None:
                self._state.move_faller_column(-1)
        if keys[pygame.K_RIGHT]:
            if self._state.get_faller_position() != None:
                self._state.move_faller_column(1)

        if keys[pygame.K_DOWN]:
            self._state.handle_time()
            

    def _end_game(self) -> None:
        self._game_over = True


    def _end_program(self) -> None:
        self._running = False


    def _redraw(self) -> None:
        self._draw_background()
        self._draw_field()
        if self._game_over:
            self._draw_game_over()
        pygame.display.flip()


    def _draw_background(self) -> None:
        surface = pygame.display.get_surface()
        surface.fill(_BACKGROUND_COLOR)


    def _draw_field(self) -> None:
        field = self._state.field()
        
        surface = pygame.display.get_surface()
        surface_width = surface.get_width()
        surface_height = surface.get_height()

        cell_length = surface_width / _FIELD_COLS

        if cell_length * _FIELD_ROWS > surface_height:
            cell_length = surface_height / _FIELD_ROWS


        center_offset_x = (surface_width - (cell_length * _FIELD_COLS)) / 2
        center_offset_y = (surface_height - (cell_length * _FIELD_ROWS)) / 2
                

        for i in range(field.visible_rows()):
            for j in range(field.cols()):   
                topleft_pixel_x = cell_length * j + center_offset_x
                topleft_pixel_y = cell_length * i + center_offset_y

                offset = 15 * ((j % 2 + i % 2) % 2)

                cell_color = pygame.Color(2 + offset,
                                          3 + offset,
                                          15 + offset)

                frozen_border = BorderStyle(pygame.Color(0, 0, 0), 1)
                falling_border = BorderStyle(pygame.Color(24, 24, 240), 2)
                landed_border = BorderStyle(pygame.Color(240, 24, 24), 3)
                matched_border = BorderStyle(pygame.Color(24, 240, 24), 4)

                border_color, thickness = frozen_border

                pos = columns.Position(i, j)
                jewel = field.get_cell(pos)

                if jewel.state() == 1:
                    border_color, thickness = falling_border
                elif jewel.state() == 2:
                    border_color, thickness = landed_border
                elif jewel.state() == 3:
                    border_color, thickness = matched_border
                
                # Cell Background Color
                pygame.draw.rect(surface, cell_color,
                                 pygame.Rect(
                                     topleft_pixel_x, topleft_pixel_y,
                                     cell_length, cell_length))

                # Cell Border
                pygame.draw.lines(
                    surface, border_color, True,
                    [(topleft_pixel_x, topleft_pixel_y),
                     (topleft_pixel_x + cell_length - thickness,
                      topleft_pixel_y),
                     (topleft_pixel_x + cell_length - thickness,
                      topleft_pixel_y + cell_length - thickness),
                     (topleft_pixel_x,
                      topleft_pixel_y + cell_length - thickness)],
                    thickness
                )

                # Jewel
                if not field.is_empty_space(pos):
                    jewel_rect = pygame.Rect(
                        topleft_pixel_x, topleft_pixel_y,
                        cell_length, cell_length)

                    scaled_image = pygame.transform.scale(
                        self._jewel_images[jewel.color() - 1],
                        (cell_length, cell_length))

                    surface.blit(scaled_image, jewel_rect)

        

    def _draw_game_over(self) -> None:
        surface = pygame.display.get_surface()
        surface_width = surface.get_width()
        surface_height = surface.get_height()

        message = 'GAME OVER'

        font_size = surface_width // 10

        if surface_width > surface_height:
            font_size = surface_height // 13
            
        font = pygame.font.SysFont(None, font_size)
        
        text_image = font.render(message, True, pygame.Color(255, 25, 25))
        text_rect = text_image.get_rect(
            center = (surface_width / 2, surface_height / 2)
            )
        surface.blit(text_image, text_rect)


    def _create_display(self, size: (int, int)) -> None:
        pygame.display.set_mode(size, pygame.RESIZABLE)




if __name__ == '__main__':
    ColumnsGame().run()
