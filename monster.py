import math
import pygame

from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MONSTER_RADIUS,
)


class Monster:
    def __init__(
        self,
        x: float,
        y: float,
        speed: float,
        radius: float,
        color: tuple[int, int, int],
        max_hp: float,
    ) -> None:
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = float(radius)
        self.color = color
        self.hp = float(max_hp)

    def take_damage(self, amount: float) -> None:
        if amount <= 0:
            return
        self.hp = max(0.0, self.hp - amount)

    def update_towards(self, player, dt_seconds: float) -> None:
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 1e-4:
            self.x += (dx / dist) * self.speed * dt_seconds
            self.y += (dy / dist) * self.speed * dt_seconds
        self.x = max(
            16.0 + self.radius,
            min(float(WINDOW_WIDTH - 16 - self.radius), self.x),
        )
        self.y = max(
            16.0 + self.radius,
            min(float(WINDOW_HEIGHT - 16 - self.radius), self.y),
        )

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x), int(self.y)),
            int(self.radius),
        )
        # If larger than normal, draw an outline ring
        if self.radius > float(MONSTER_RADIUS):
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (int(self.x), int(self.y)),
                int(self.radius) + 4,
                width=2,
            )
