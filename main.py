import sys
import math
import pygame

from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    BACKGROUND_COLOR,
    ACCENT_COLOR,
    HINT_TEXT_COLOR,
    FONT_NAME,
    WINDOW_CAPTION,
    HINT_TEXT,
    PLAYER_BASE_SPEED,
)


def poll_quit_requested() -> bool:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True

        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
        ):

            return True
    return False


def compute_move_vector() -> tuple[float, float]:
    keys = pygame.key.get_pressed()
    move_x = (
        (keys[pygame.K_d] or keys[pygame.K_RIGHT])
        - (keys[pygame.K_a] or keys[pygame.K_LEFT])
    )
    move_y = (
        (keys[pygame.K_s] or keys[pygame.K_DOWN])
        - (keys[pygame.K_w] or keys[pygame.K_UP])
    )

    if move_x or move_y:
        length = math.hypot(move_x, move_y)
        move_x /= length
        move_y /= length

    return float(move_x), float(move_y)


def update_player_position(
    position_x: float,
    position_y: float,
    move_x: float,
    move_y: float,
    speed_pixels_per_second: float,
    dt_seconds: float,
) -> tuple[float, float]:
    position_x += move_x * speed_pixels_per_second * dt_seconds
    position_y += move_y * speed_pixels_per_second * dt_seconds
    return position_x, position_y


def clamp_to_screen(position_x: float, position_y: float) -> tuple[float, float]:
    position_x = max(
        16,
        min(WINDOW_WIDTH - 16, position_x),
    )
    position_y = max(
        16,
        min(WINDOW_HEIGHT - 16, position_y),
    )
    return position_x, position_y


def compose_hint_surfaces(
    font: pygame.font.Font,
) -> tuple[list[pygame.Surface], int]:
    hint_lines = [
        font.render(line, True, HINT_TEXT_COLOR)
        for line in HINT_TEXT.splitlines()
        if line
    ]
    return hint_lines, font.get_linesize()


def render_scene(
    screen: pygame.Surface,
    hint_surfaces: list[pygame.Surface],
    hint_line_height: int,
    player_x: float,
    player_y: float,
    time_seconds: float,
) -> None:
    screen.fill(BACKGROUND_COLOR)

    y = 20
    for surf in hint_surfaces:
        screen.blit(surf, (20, y))
        y += hint_line_height

    pulse = 4 + int(3 * (1 + math.sin(time_seconds * 4)))
    pygame.draw.circle(
        screen,
        (60, 60, 72),
        (int(player_x), int(player_y)),
        18 + pulse,
        width=2,
    )

    pygame.draw.circle(
        screen,
        ACCENT_COLOR,
        (int(player_x), int(player_y)),
        12,
    )

    pygame.display.flip()


def initialize_game() -> tuple[
    pygame.Surface,
    pygame.time.Clock,
    list[pygame.Surface],
    int,
    float,
    float,
    float,
]:
    pygame.init()

    screen = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT)
    )

    pygame.display.set_caption(WINDOW_CAPTION)

    clock = pygame.time.Clock()

    font = pygame.font.SysFont(FONT_NAME, 28)
    hint_surfaces, hint_line_height = compose_hint_surfaces(font)

    player_pos_x = float(WINDOW_WIDTH // 2)
    player_pos_y = float(WINDOW_HEIGHT // 2)
    player_speed = float(PLAYER_BASE_SPEED)

    return (
        screen,
        clock,
        hint_surfaces,
        hint_line_height,
        player_pos_x,
        player_pos_y,
        player_speed,
    )


def game_loop(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    hint_surfaces: list[pygame.Surface],
    hint_line_height: int,
    player_pos_x: float,
    player_pos_y: float,
    player_speed: float,
) -> None:

    time_accumulator = 0.0

    while True:
        dt_ms = clock.tick(FPS)
        dt = dt_ms / 1000.0
        time_accumulator += dt

        if poll_quit_requested():
            return

        move_x, move_y = compute_move_vector()

        player_pos_x, player_pos_y = update_player_position(
            player_pos_x,
            player_pos_y,
            move_x,
            move_y,
            player_speed,
            dt,
        )

        player_pos_x, player_pos_y = clamp_to_screen(
            player_pos_x, player_pos_y
        )

        render_scene(
            screen,
            hint_surfaces,
            hint_line_height,
            player_pos_x,
            player_pos_y,
            time_accumulator,
        )


def run() -> None:
    (
        screen,
        clock,
        hint_surfaces,
        hint_line_height,
        player_pos_x,
        player_pos_y,
        player_speed,
    ) = initialize_game()

    game_loop(
        screen,
        clock,
        hint_surfaces,
        hint_line_height,
        player_pos_x,
        player_pos_y,
        player_speed,
    )

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    run()
