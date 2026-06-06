# dashboard/fires.py

import pygame
import config


def draw_fires(self, fires):
        '''
        Draws active fires on the dashboard.
        INPUT:      
            - self: Dashboard
            - fires: [Fire]
        '''

        # 1: ITERATE THROUGH FIRES
        for fire in fires:

            # 1.1 EXTRACT FIRE DETAILS
            x = int(fire["x"])
            y = int(fire["y"])
            radius = max(1, int(fire["radius"]))

            # 1.2 GRAY SHADING
            shade_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                shade_surface,
                (180, 180, 180, 50),
                (radius, radius),
                radius,
            )
            self.screen.blit(shade_surface, (x - radius, y - radius))

            # 1.3 FIRE RING
            pygame.draw.circle(
                self.screen,
                config.FIRE_RING_COLOR,
                (x, y),
                radius,
                2,
            )

            # 1.4 FIRE CORE
            pygame.draw.circle(
                self.screen,
                config.FIRE_CORE_COLOR,
                (x, y),
                5,
            )
