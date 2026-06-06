# dashboard/controller.py

import pygame
import config
from dashboard.map_base import draw_map_base, draw_sensors
from dashboard.fires import draw_fires
from dashboard.sidebar import draw_sidebar


class Dashboard:
    '''
    Manage the Pygame window, user input, and drawing of elements.
    METHODS:
        - tick(): Control framerate of the dashboard.
        - draw(): Update the display based on current state.
        - get_input(): Capture user interactions.
        - close(): Exit Pygame.
    '''

    def __init__(self):
        '''
        Sets up Pygame window with basic formatting.
        '''
        
        # 1: INITIALIZE PYGAME AND WINDOW
        pygame.init()
        pygame.display.set_caption("FOX - Fire Observation eXchange")
        
        # 2: SET UP DISPLAY, CLOCK, AND FONTS
        self.screen = pygame.display.set_mode(
            (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        )
        
        # 3: CLOCK FOR FRAMERATE CONTROL, FONTS FOR TEXT
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont(None, 20)
        self.font_medium = pygame.font.SysFont(None, 26)
        self.font_large = pygame.font.SysFont(None, 34)

    def tick(self):
        '''
        Limits loop to target framerate.
        '''
        return self.clock.tick(config.FPS) / 1000.0

    def get_input(self):
        '''
        Receives user input from Pygame.
        OUTPUT:     
            - actions:  dict: {
                            "quit": bool
                            "toggle_pause": bool
                            "reset": bool
                            "fire_click": None or (int, int)
                        }
        '''

        # 1: DEFINE POSSIBLE ACTIONS
        actions = {
            "quit": False,
            "toggle_pause": False,
            "reset": False,
            "fire_click": None
        }

        # 2: RECORD EACH ACTION
        for event in pygame.event.get():

            # 2.1 HANDLE PYGAME EXIT
            if event.type == pygame.QUIT:
                actions["quit"] = True

            # 2.2 RECORD KEYPRESS
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    actions["toggle_pause"] = True
                elif event.key == pygame.K_r:
                    actions["reset"] = True

            # 2.3 NEW FIRE
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if 0 <= mx < config.WORLD_SIZE and 0 <= my < config.WORLD_SIZE:
                    actions["fire_click"] = (mx, my)

        return actions

    def draw(self, state_dict):
        '''
        Draws dashboard based on current state.
        INPUT:      
            - state_dict:   dict: {
                                "paused": bool
                                "sim_time": float
                                "sensor_interval": float
                                "sensor_count": int
                                "fire_count": int
                                "events_per_second": float
                                "queue_size": int
                                "alerts_this_tick": int
                                "total_alerts": int
                                "recent_alerts": [Alert]
                                "load_summary": {str: dict}
                                "readings": [SensorReading]
                                "fires": [Fire]
                            }
        '''

        # 1: FILL BACKGROUND
        self.screen.fill(config.SIDEBAR_BG_COLOR)
        
        # 2: DRAW ELEMENTS
        draw_map_base(self)
        draw_fires(self, state_dict["fires"])
        draw_sensors(self, state_dict["readings"])
        draw_sidebar(self, state_dict)

        # 3: UPDATE ENTIRE DISPLAY
        pygame.display.flip()

    def close(self):
        pygame.quit()
