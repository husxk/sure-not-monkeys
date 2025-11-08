import pygame

from config import (
    BULLET_COLOR,
    BULLET_RADIUS,
)


class Bullet:
    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def update(self, dt_seconds: float) -> None:
        self.x += self.vx * dt_seconds
        self.y += self.vy * dt_seconds

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(
            screen,
            BULLET_COLOR,
            (int(self.x), int(self.y)),
            BULLET_RADIUS,
        )
