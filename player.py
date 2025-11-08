import math
import pygame

from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    ACCENT_COLOR,
    PLAYER_RADIUS,
    PLAYER_MAX_HP,
)


class Player:
    def __init__(self, x: float, y: float, speed: float) -> None:
        self.x = x
        self.y = y
        self.speed = speed
        self.hp = float(PLAYER_MAX_HP)

    def take_damage(self, amount: float) -> None:
        if amount <= 0:
            return
        self.hp = max(0.0, self.hp - amount)

    def update(self, move_x: float, move_y: float, dt_seconds: float) -> None:
        self.x += move_x * self.speed * dt_seconds
        self.y += move_y * self.speed * dt_seconds
        self._clamp_to_screen()

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
