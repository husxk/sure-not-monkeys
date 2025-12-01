import sys
import math
import random
import pygame

from config import *
from player import Player
from monster import Monster
from bullet import Bullet


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
    bullets: list[Bullet],
    timer_surface: pygame.Surface,
    timer_pos: tuple[int, int],
    hp_surface: pygame.Surface,
    hp_pos: tuple[int, int],
    lvl_surface: pygame.Surface,
    lvl_pos: tuple[int, int],
    xp_surface: pygame.Surface,
    xp_pos: tuple[int, int],
) -> None:
    screen.fill(BACKGROUND_COLOR)

    screen.blit(timer_surface, timer_pos)
    screen.blit(hp_surface, hp_pos)
    screen.blit(lvl_surface, lvl_pos)
    screen.blit(xp_surface, xp_pos)

    y = 20
    for surf in hint_surfaces:
        screen.blit(surf, (20, y))
        y += hint_line_height

    for monster in monsters:
        monster.draw(screen)

    for bullet in bullets:
        bullet.draw(screen)

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
            return Monster(
                x,
                y,
                float(MONSTER_SPEED),
                float(MONSTER_RADIUS),
                MONSTER_COLOR,
                float(MONSTER_MAX_HP),
            )

    # Fallback: place near a corner far from player
    x = 16.0 if player.x > WINDOW_WIDTH / 2 else float(WINDOW_WIDTH - 16)
    y = 16.0 if player.y > WINDOW_HEIGHT / 2 else float(WINDOW_HEIGHT - 16)
    return Monster(
        x,
        y,
        float(MONSTER_SPEED),
        float(MONSTER_RADIUS),
        MONSTER_COLOR,
        float(MONSTER_MAX_HP),
    )


def generate_boss(player: Player) -> Monster:
    # Integer scale with player level: floor(level / step), min 1
    scale = max(1, int(player.level) // int(BOSS_SPAWN_LEVEL_STEP))
    scaled_radius = float(BOSS_RADIUS) * float(scale)
    scaled_hp = float(BOSS_MAX_HP) * float(scale)
    # Spawn far from player near edges
    for _ in range(32):
        x = random.uniform(16.0, float(WINDOW_WIDTH - 16))
        y = random.uniform(16.0, float(WINDOW_HEIGHT - 16))
        if (
            math.hypot(x - player.x, y - player.y)
            >= MONSTER_MIN_DISTANCE_FROM_PLAYER
        ):
            return Monster(
                x,
                y,
                float(BOSS_SPEED),
                scaled_radius,
                BOSS_COLOR,
                scaled_hp,
            )
    # Fallback: corner
    x = 16.0 if player.x > WINDOW_WIDTH / 2 else float(WINDOW_WIDTH - 16)
    y = 16.0 if player.y > WINDOW_HEIGHT / 2 else float(WINDOW_HEIGHT - 16)
    return Monster(
        x,
        y,
        float(BOSS_SPEED),
        scaled_radius,
        BOSS_COLOR,
        scaled_hp,
    )


def apply_monster_damage(
    player: Player,
    monsters: list[Monster],
    dt_seconds: float,
) -> None:
    damage_total = 0.0
    for m in monsters:
        if math.hypot(player.x - m.x, player.y - m.y) <= (
            float(PLAYER_RADIUS) + float(m.radius) + PLAYER_MONSTER_PADDING
        ):
            damage_total += MONSTER_DAMAGE_PER_SECOND * dt_seconds
    if damage_total > 0.0:
        player.take_damage(damage_total)


def separate_monsters(monsters: list[Monster]) -> None:
    if len(monsters) <= 1:
        return
    # Per-pair min distance using each entity's radius
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
                min_dist = (
                    float(mi.radius)
                    + float(mj.radius)
                    + MONSTER_SEPARATION_PADDING
                )
                if dist < min_dist:
                    overlap = float(min_dist - dist) * 0.5
                    nx = dx / dist
                    ny = dy / dist
                    mi.x -= nx * overlap
                    mi.y -= ny * overlap
                    mj.x += nx * overlap
                    mj.y += ny * overlap
                    # clamp to screen
                    mi.x = max(
                        16.0 + float(mi.radius),
                        min(
                            float(
                                WINDOW_WIDTH - 16 - float(mi.radius)
                            ),
                            mi.x,
                        ),
                    )
                    mi.y = max(
                        16.0 + float(mi.radius),
                        min(
                            float(
                                WINDOW_HEIGHT - 16 - float(mi.radius)
                            ),
                            mi.y,
                        ),
                    )
                    mj.x = max(
                        16.0 + float(mj.radius),
                        min(
                            float(
                                WINDOW_WIDTH - 16 - float(mj.radius)
                            ),
                            mj.x,
                        ),
                    )
                    mj.y = max(
                        16.0 + float(mj.radius),
                        min(
                            float(
                                WINDOW_HEIGHT - 16 - float(mj.radius)
                            ),
                            mj.y,
                        ),
                    )


def separate_player_and_monsters(
    player: Player,
    monsters: list[Monster],
) -> None:
    for m in monsters:
        dx = m.x - player.x
        dy = m.y - player.y
        dist = math.hypot(dx, dy)
        if dist < 1e-6:
            dx, dy, dist = 1.0, 0.0, 1.0
        min_dist = (
            float(PLAYER_RADIUS)
            + float(m.radius)
            + PLAYER_MONSTER_PADDING
        )
        if dist < min_dist:
            overlap = float(min_dist - dist)
            nx = dx / dist
            ny = dy / dist
            m.x += nx * overlap
            m.y += ny * overlap
            # clamp to screen
            m.x = max(
                16.0 + float(m.radius),
                min(
                    float(WINDOW_WIDTH - 16 - float(m.radius)),
                    m.x,
                ),
            )
            m.y = max(
                16.0 + float(m.radius),
                min(
                    float(
                        WINDOW_HEIGHT - 16 - float(m.radius)
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


def compute_spawn_interval(elapsed_seconds: float) -> float:
    # Decrease interval every full minute by a fixed step,
    # down to a minimum cap.
    period = float(MONSTER_SPAWN_SCALING_PERIOD_SECONDS)
    minutes = int(elapsed_seconds // period)
    interval = (
        MONSTER_SPAWN_INTERVAL_SECONDS
        - minutes * MONSTER_SPAWN_INTERVAL_STEP_SECONDS
    )
    if interval < MONSTER_SPAWN_INTERVAL_MIN_SECONDS:
        interval = MONSTER_SPAWN_INTERVAL_MIN_SECONDS
    return float(interval)


def initialize_game() -> tuple[
    pygame.Surface,
    pygame.time.Clock,
    pygame.font.Font,
    list[pygame.Surface],
    int,
    Player,
    list[Monster],
    list[Bullet],
    int,
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
        [],
        int(BOSS_SPAWN_LEVEL_STEP),
    )


def game_loop(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    font: pygame.font.Font,
    hint_surfaces: list[pygame.Surface],
    hint_line_height: int,
    player: Player,
    monsters: list[Monster],
    bullets: list[Bullet],
    next_boss_level: int,
) -> None:

    time_accumulator = 0.0
    next_spawn_time = compute_spawn_interval(0.0)
    next_shot_time = 0.0
    next_volley_time = 0.0

    while True:
        dt_ms = clock.tick(FPS)
        dt = dt_ms / 1000.0
        time_accumulator += dt

        if poll_quit_requested():
            return

        move_x, move_y = compute_move_vector()
        player.update(move_x, move_y, dt)

        # Face towards mouse cursor
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player.update_facing_towards(
            float(mouse_x), float(mouse_y)
        )

        while time_accumulator >= next_spawn_time:
            monsters.append(generate_monster(player))
            next_spawn_time += compute_spawn_interval(
                time_accumulator
            )

        # Boss spawn on level milestones
        if player.level >= next_boss_level:
            monsters.append(generate_boss(player))
            next_boss_level += int(BOSS_SPAWN_LEVEL_STEP)

        update_monsters(monsters, player, dt)

        separate_monsters(monsters)
        separate_player_and_monsters(player, monsters)

        apply_monster_damage(player, monsters, dt)

        # Shooting continuously from facing direction
        while time_accumulator >= next_shot_time:
            fx, fy = player.get_facing()
            if not fx and not fy:
                fx, fy = 1.0, 0.0
            vx = fx * BULLET_SPEED
            vy = fy * BULLET_SPEED
            mx, my = player.get_muzzle_position()
            bullets.append(Bullet(mx, my, vx, vy))
            next_shot_time += BULLET_COOLDOWN_SECONDS

        # Volley attack on its own cooldown
        while time_accumulator >= next_volley_time:
            fx, fy = player.get_facing()
            if not fx and not fy:
                fx, fy = 1.0, 0.0
            mx, my = player.get_muzzle_position()
            # Create symmetric angle offsets around 0\n
            count = int(VOLLEY_BULLET_COUNT)
            spread_deg = float(VOLLEY_SPREAD_DEGREES)
            if count <= 1:
                offsets = [0.0]
            else:
                step = spread_deg / float(count - 1)
                start = -spread_deg / 2.0
                offsets = [start + i * step for i in range(count)]
            for deg in offsets:
                rad = math.radians(deg)
                cos_a = math.cos(rad)
                sin_a = math.sin(rad)
                rx = fx * cos_a - fy * sin_a
                ry = fx * sin_a + fy * cos_a
                bvx = rx * float(VOLLEY_BULLET_SPEED)
                bvy = ry * float(VOLLEY_BULLET_SPEED)
                bullets.append(Bullet(mx, my, bvx, bvy))
            next_volley_time += float(VOLLEY_COOLDOWN_SECONDS)

        # Update bullets and remove off-screen
        alive_bullets: list[Bullet] = []
        for b in bullets:
            b.update(dt)
            if (
                b.x < -BULLET_RADIUS
                or b.x > WINDOW_WIDTH + BULLET_RADIUS
                or b.y < -BULLET_RADIUS
                or b.y > WINDOW_HEIGHT + BULLET_RADIUS
            ):
                continue
            alive_bullets.append(b)
        bullets[:] = alive_bullets

        # Bullet collisions
        new_monsters: list[Monster] = []
        for m in monsters:
            hit = False
            for b in list(bullets):
                if (
                    math.hypot(m.x - b.x, m.y - b.y)
                    <= (float(m.radius) + BULLET_RADIUS)
                ):
                    m.take_damage(
                        player.get_bullet_damage()
                    )
                    bullets.remove(b)
                    hit = True
                    if m.hp <= 0.0:
                        player.gain_xp(float(MONSTER_XP_ON_KILL))
                    break
            if m.hp > 0.0:
                new_monsters.append(m)
        monsters[:] = new_monsters

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
        line_h = font.get_linesize()
        hp_x = (
            WINDOW_WIDTH - hp_surface.get_width() - 20
        )
        hp_pos = (hp_x, 6 + line_h + 2)

        # Level above HP
        lvl_text = f"LVL: {player.level}"
        lvl_surface = font.render(lvl_text, True, TEXT_COLOR)
        lvl_x = (
            WINDOW_WIDTH - lvl_surface.get_width() - 20
        )
        lvl_pos = (lvl_x, 6)

        # XP below HP
        xp_text = (
            f"XP: {int(player.xp)}/"
            f"{int(player.xp_to_next)}"
        )
        xp_surface = font.render(xp_text, True, TEXT_COLOR)
        xp_x = (
            WINDOW_WIDTH - xp_surface.get_width() - 20
        )
        xp_pos = (xp_x, hp_pos[1] + line_h + 2)

        render_scene(
            screen,
            hint_surfaces,
            hint_line_height,
            player,
            time_accumulator,
            monsters,
            bullets,
            timer_surface,
            (timer_x, timer_y),
            hp_surface,
            hp_pos,
            lvl_surface,
            lvl_pos,
            xp_surface,
            xp_pos,
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
        bullets,
        next_boss_level,
    ) = initialize_game()

    game_loop(
        screen,
        clock,
        font,
        hint_surfaces,
        hint_line_height,
        player,
        monsters,
        bullets,
        next_boss_level,
    )

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    run()
