import sys
import math
import random
import pygame

from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    BACKGROUND_COLOR,
    HINT_TEXT_COLOR,
    TEXT_COLOR,
    FONT_NAME,
    WINDOW_CAPTION,
    HINT_TEXT,
    PLAYER_BASE_SPEED,
    PLAYER_RADIUS,
    MONSTER_COLOR,
    MONSTER_RADIUS,
    MONSTER_SPAWN_INTERVAL_SECONDS,
    MONSTER_MIN_DISTANCE_FROM_PLAYER,
    MONSTER_SPEED,
    MONSTER_DAMAGE_DISTANCE,
    MONSTER_DAMAGE_PER_SECOND,
    MONSTER_SEPARATION_PASSES,
    MONSTER_SEPARATION_PADDING,
    PLAYER_MONSTER_PADDING,
)
from player import Player
from monster import Monster


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
    player: Player,
    time_seconds: float,
    monsters: list[Monster],
    timer_surface: pygame.Surface,
    timer_pos: tuple[int, int],
    hp_surface: pygame.Surface,
    hp_pos: tuple[int, int],
) -> None:
    screen.fill(BACKGROUND_COLOR)

    screen.blit(timer_surface, timer_pos)
    screen.blit(hp_surface, hp_pos)

    y = 20
    for surf in hint_surfaces:
        screen.blit(surf, (20, y))
        y += hint_line_height

    for monster in monsters:
        monster.draw(screen)

    player.draw(screen, time_seconds)

    pygame.display.flip()


def generate_monster(player: Player) -> Monster:
    # Try random positions away from the player
    for _ in range(32):
        x = random.uniform(16.0, float(WINDOW_WIDTH - 16))
        y = random.uniform(16.0, float(WINDOW_HEIGHT - 16))
        if (
            math.hypot(x - player.x, y - player.y)
            >= MONSTER_MIN_DISTANCE_FROM_PLAYER
        ):
            return Monster(x, y, float(MONSTER_SPEED))

    # Fallback: place near a corner far from player
    x = 16.0 if player.x > WINDOW_WIDTH / 2 else float(WINDOW_WIDTH - 16)
    y = 16.0 if player.y > WINDOW_HEIGHT / 2 else float(WINDOW_HEIGHT - 16)
    return Monster(x, y, float(MONSTER_SPEED))


def apply_monster_damage(
    player: Player,
    monsters: list[Monster],
    dt_seconds: float,
) -> None:
    damage_total = 0.0
    for m in monsters:
        if (
            math.hypot(player.x - m.x, player.y - m.y)
            <= MONSTER_DAMAGE_DISTANCE
        ):
            damage_total += MONSTER_DAMAGE_PER_SECOND * dt_seconds
    if damage_total > 0.0:
        player.take_damage(damage_total)


def separate_monsters(monsters: list[Monster]) -> None:
    if len(monsters) <= 1:
        return
    min_dist = float(MONSTER_RADIUS * 2) + MONSTER_SEPARATION_PADDING
    for _ in range(MONSTER_SEPARATION_PASSES):
        for i in range(len(monsters)):
            mi = monsters[i]
            for j in range(i + 1, len(monsters)):
                mj = monsters[j]
                dx = mj.x - mi.x
                dy = mj.y - mi.y
                dist = math.hypot(dx, dy)
                if dist < 1e-6:
                    # tiny nudge to avoid zero division
                    dx, dy, dist = 1.0, 0.0, 1.0
                if dist < min_dist:
                    overlap = (min_dist - dist) * 0.5
                    nx = dx / dist
                    ny = dy / dist
                    mi.x -= nx * overlap
                    mi.y -= ny * overlap
                    mj.x += nx * overlap
                    mj.y += ny * overlap
                    # clamp to screen
                    mi.x = max(
                        16.0 + MONSTER_RADIUS,
                        min(
                            float(
                                WINDOW_WIDTH - 16 - MONSTER_RADIUS
                            ),
                            mi.x,
                        ),
                    )
                    mi.y = max(
                        16.0 + MONSTER_RADIUS,
                        min(
                            float(
                                WINDOW_HEIGHT - 16 - MONSTER_RADIUS
                            ),
                            mi.y,
                        ),
                    )
                    mj.x = max(
                        16.0 + MONSTER_RADIUS,
                        min(
                            float(
                                WINDOW_WIDTH - 16 - MONSTER_RADIUS
                            ),
                            mj.x,
                        ),
                    )
                    mj.y = max(
                        16.0 + MONSTER_RADIUS,
                        min(
                            float(
                                WINDOW_HEIGHT - 16 - MONSTER_RADIUS
                            ),
                            mj.y,
                        ),
                    )


def separate_player_and_monsters(
    player: Player,
    monsters: list[Monster],
) -> None:
    min_dist = float(PLAYER_RADIUS + MONSTER_RADIUS) \
        + PLAYER_MONSTER_PADDING
    for m in monsters:
        dx = m.x - player.x
        dy = m.y - player.y
        dist = math.hypot(dx, dy)
        if dist < 1e-6:
            dx, dy, dist = 1.0, 0.0, 1.0
        if dist < min_dist:
            overlap = min_dist - dist
            nx = dx / dist
            ny = dy / dist
            m.x += nx * overlap
            m.y += ny * overlap
            # clamp to screen
            m.x = max(
                16.0 + MONSTER_RADIUS,
                min(
                    float(WINDOW_WIDTH - 16 - MONSTER_RADIUS),
                    m.x,
                ),
            )
            m.y = max(
                16.0 + MONSTER_RADIUS,
                min(
                    float(
                        WINDOW_HEIGHT - 16 - MONSTER_RADIUS
                    ),
                    m.y,
                ),
            )


def update_monsters(
    monsters: list[Monster],
    player: Player,
    dt_seconds: float,
) -> None:
    for monster in monsters:
        monster.update_towards(player, dt_seconds)


def initialize_game() -> tuple[
    pygame.Surface,
    pygame.time.Clock,
    pygame.font.Font,
    list[pygame.Surface],
    int,
    Player,
    list[Monster],
]:
    pygame.init()

    screen = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT)
    )

    pygame.display.set_caption(WINDOW_CAPTION)

    clock = pygame.time.Clock()

    font = pygame.font.SysFont(FONT_NAME, 28)
    hint_surfaces, hint_line_height = compose_hint_surfaces(font)

    player = Player(
        float(WINDOW_WIDTH // 2),
        float(WINDOW_HEIGHT // 2),
        float(PLAYER_BASE_SPEED),
    )

    return (
        screen,
        clock,
        font,
        hint_surfaces,
        hint_line_height,
        player,
        [],
    )


def game_loop(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    font: pygame.font.Font,
    hint_surfaces: list[pygame.Surface],
    hint_line_height: int,
    player: Player,
    monsters: list[Monster],
) -> None:

    time_accumulator = 0.0
    next_spawn_time = MONSTER_SPAWN_INTERVAL_SECONDS

    while True:
        dt_ms = clock.tick(FPS)
        dt = dt_ms / 1000.0
        time_accumulator += dt

        if poll_quit_requested():
            return

        move_x, move_y = compute_move_vector()
        player.update(move_x, move_y, dt)

        while time_accumulator >= next_spawn_time:
            monsters.append(generate_monster(player))
            next_spawn_time += MONSTER_SPAWN_INTERVAL_SECONDS

        update_monsters(monsters, player, dt)

        separate_monsters(monsters)
        separate_player_and_monsters(player, monsters)

        apply_monster_damage(player, monsters, dt)

        # Timer string and surface
        total_seconds = int(time_accumulator)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        timer_text = f"{minutes:02d}:{seconds:02d}"
        timer_surface = font.render(
            timer_text, True, TEXT_COLOR
        )
        timer_x = (
            WINDOW_WIDTH // 2
            - timer_surface.get_width() // 2
        )
        timer_y = 6

        # HP string and surface
        hp_text = f"HP: {int(player.hp)}"
        hp_surface = font.render(hp_text, True, TEXT_COLOR)
        hp_x = (
            WINDOW_WIDTH - hp_surface.get_width() - 20
        )
        hp_pos = (hp_x, 6)

        render_scene(
            screen,
            hint_surfaces,
            hint_line_height,
            player,
            time_accumulator,
            monsters,
            timer_surface,
            (timer_x, timer_y),
            hp_surface,
            hp_pos,
        )


def run() -> None:
    (
        screen,
        clock,
        font,
        hint_surfaces,
        hint_line_height,
        player,
        monsters,
    ) = initialize_game()

    game_loop(
        screen,
        clock,
        font,
        hint_surfaces,
        hint_line_height,
        player,
        monsters,
    )

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    run()
