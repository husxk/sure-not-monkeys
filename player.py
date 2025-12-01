import math
import pygame

from config import *


class Player:
    def __init__(self, x: float, y: float, speed: float) -> None:
        self.x = x
        self.y = y
        self.speed = speed
        self.hp = float(PLAYER_MAX_HP)
        self.face_dx = 1.0
        self.face_dy = 0.0
        self.level = 1
        self.xp = 0.0
        self.xp_to_next = float(PLAYER_XP_BASE)

    def take_damage(self, amount: float) -> None:
        if amount <= 0:
            return
        self.hp = max(0.0, self.hp - amount)

    def update(self, move_x: float, move_y: float, dt_seconds: float) -> None:
        self.x += move_x * self.speed * dt_seconds
        self.y += move_y * self.speed * dt_seconds
        self._clamp_to_screen()
        if move_x or move_y:
            length = math.hypot(move_x, move_y) or 1.0
            self.face_dx = move_x / length
            self.face_dy = move_y / length

    def get_facing(self) -> tuple[float, float]:
        return self.face_dx, self.face_dy

    def get_muzzle_position(self) -> tuple[float, float]:
        offset = float(PLAYER_RADIUS + 6)
        return (
            self.x + self.face_dx * offset,
            self.y + self.face_dy * offset,
        )

    def get_bullet_damage(self) -> float:
        return float(
            BULLET_DAMAGE
            + BULLET_DAMAGE_PER_LEVEL * max(0, self.level - 1)
        )

    def update_facing_towards(
        self, target_x: float, target_y: float
    ) -> None:
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 1e-4:
            self.face_dx = dx / dist
            self.face_dy = dy / dist

    def gain_xp(self, amount: float) -> None:
        if amount <= 0:
            return
        self.xp += amount
        while self.xp >= self.xp_to_next:
            if self.level >= int(PLAYER_MAX_LEVEL):
                # cap reached: stop leveling further
                self.xp = min(self.xp, self.xp_to_next - 1.0)
                break
            self.xp -= self.xp_to_next
            self.level += 1
            # increase requirement modestly per level
            self.xp_to_next = float(
                int(self.xp_to_next * float(PLAYER_XP_MULTIPLIER))
            )
            # heal on level up
            self.hp = min(
                float(PLAYER_MAX_HP),
                self.hp + float(LEVEL_UP_HP_BONUS),
            )

    def _clamp_to_screen(self) -> None:
        self.x = max(16.0, min(float(WINDOW_WIDTH - 16), self.x))
        self.y = max(16.0, min(float(WINDOW_HEIGHT - 16), self.y))

    def draw(self, screen: pygame.Surface, time_seconds: float) -> None:
        pulse = 4 + int(3 * (1 + math.sin(time_seconds * 4)))
        pygame.draw.circle(
            screen,
            (60, 60, 72),
            (int(self.x), int(self.y)),
            18 + pulse,
            width=2,
        )
        pygame.draw.circle(
            screen,
            ACCENT_COLOR,
            (int(self.x), int(self.y)),
            PLAYER_RADIUS,
        )
        # Facing indicator (small triangle)
        fx, fy = self.get_facing()
        tip_len = float(PLAYER_RADIUS + 10)
        base_len = float(PLAYER_RADIUS - 2)
        half_w = 6.0
        tip = (self.x + fx * tip_len, self.y + fy * tip_len)
        bx = self.x + fx * base_len
        by = self.y + fy * base_len
        # perpendicular
        px, py = -fy, fx
        left = (bx + px * half_w, by + py * half_w)
        right = (bx - px * half_w, by - py * half_w)
        pygame.draw.polygon(
            screen,
            TEXT_COLOR,
            [(int(tip[0]), int(tip[1])),
             (int(left[0]), int(left[1])),
             (int(right[0]), int(right[1]))],
        )
