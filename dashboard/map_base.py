# dashboard/map_base.py

import pygame
import config


def draw_map_background(self):
        '''
        Solid map background, color from congifig.
        '''
        pygame.draw.rect(
            self.screen,
            config.MAP_BG_COLOR,
            (0, 0, config.WORLD_SIZE, config.WORLD_SIZE),
        )

def draw_quadrants(self):
    '''
    Draws separation lines for map quadrants.
    '''

    # 1: CALCULATE MIDPOINT
    mid = config.WORLD_SIZE // 2
    
    # 2: DRAW VERTICAL LINE
    pygame.draw.line(
        self.screen,
        config.QUADRANT_LINE_COLOR,
        (mid, 0),
        (mid, config.WORLD_SIZE),
        1,
    )
    
    # 3: DRAW HORIZONTAL LINE
    pygame.draw.line(
        self.screen,
        config.QUADRANT_LINE_COLOR,
        (0, mid),
        (config.WORLD_SIZE, mid),
        1,
    )

def _sensor_color(reading):
        '''
        Defines conditions for color-coded sensors.
        INPUT:      
            - reading: SensorReading
        RETURN:
            - (int, int, int) for sensor color
        '''

        # 1: Fire conditions: Cross all 3 thresholds
        fire_like = (
            reading.temperature > config.TEMP_ALERT_THRESHOLD
            and reading.humidity < config.HUMIDITY_ALERT_THRESHOLD
            and reading.smoke > config.SMOKE_ALERT_THRESHOLD
        )

        # 2: Elevated: Approaching 1+ threshold
        elevated = (
            reading.temperature > config.AMBIENT_TEMPERATURE + 3.0
            or reading.smoke > 0.08
            or reading.humidity < config.AMBIENT_HUMIDITY - 5.0
        )

        # 3: Return appropriate color
        if fire_like:
            return config.SENSOR_FIRE_COLOR
        elif elevated:
            return config.SENSOR_ELEVATED_COLOR
        else:
             return config.SENSOR_NORMAL_COLOR

def draw_sensors(self, readings):
    '''
    Draws sensors on dashboard with color-coded reading.
    INPUT:
        - readings: [SensorReading]
    '''

    # 1: ITERATE THROUGH READINGS
    for reading in readings:

        # 1.1: DETERMINE COLOR BASED ON READING
        color = _sensor_color(reading)
        
        # 1.2: DRAW CIRCLE FOR SENSOR
        pygame.draw.circle(
            self.screen,
            color,
            (int(reading.x), int(reading.y)),
            config.SENSOR_RADIUS,
        )

def draw_map_base(self):
    '''
    Draws the base map with background and quadrants.
    '''
    draw_map_background(self)
    draw_quadrants(self)
