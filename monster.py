import math
import pygame

from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MONSTER_COLOR,
    MONSTER_RADIUS,
)


class Monster:
    def __init__(self, x: float, y: float, speed: float) -> None:
        self.x = x
        self.y = y
        self.speed = speed

    def update_towards(self, player, dt_seconds: float) -> None:
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 1e-4:
            self.x += (dx / dist) * self.speed * dt_seconds
            self.y += (dy / dist) * self.speed * dt_seconds
        self.x = max(
            16.0 + MONSTER_RADIUS,
            min(float(WINDOW_WIDTH - 16 - MONSTER_RADIUS), self.x),
        )
        self.y = max(
            16.0 + MONSTER_RADIUS,
            min(float(WINDOW_HEIGHT - 16 - MONSTER_RADIUS), self.y),
        )

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(
            screen,
            MONSTER_COLOR,
            (int(self.x), int(self.y)),
            MONSTER_RADIUS,
        )
