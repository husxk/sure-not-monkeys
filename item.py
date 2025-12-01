import pygame

from config import ITEM_COLOR, ITEM_SIZE


class Item:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def draw(self, screen: pygame.Surface) -> None:
        half = ITEM_SIZE // 2
        rect = pygame.Rect(int(self.x) - half, int(self.y) - half,
                           ITEM_SIZE, ITEM_SIZE)
        pygame.draw.rect(screen, ITEM_COLOR, rect)
        pygame.draw.rect(screen, (40, 80, 40), rect, width=2)
