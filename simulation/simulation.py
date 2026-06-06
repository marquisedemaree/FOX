# simuulation/simulation.py

import math
import random
import config
from dataclasses import dataclass


@dataclass
class SensorReading:
    sensor_id: int
    x: float
    y: float
    temperature: float
    humidity: float
    smoke: float
    timestamp: float

class Fire:
    '''
    Represents a fire event with location and growth over time.
    METHODS:
        - radius(): calculates current fire radius based on elapsed time.
    '''

    def __init__(self, x, y, start_time):
        '''
        Initializes fire with center coordinates and creation time.
        INPUT:
            - x, y: float, fire center coordinates.
            - start_time: float, simulation time when fire was created.
        '''

        # 1: Store fire center coordinates
        self.x = float(x)
        self.y = float(y)

        # 2: Store fire creation time
        self.start_time = float(start_time)

    def radius(self, sim_time):
        '''
        Determines elapsed simulation time and expands fire radius.
        INPUT:
            - sim_time: float, current simulation time.
        OUTPUT:
            - radius: float, current fire radius based on growth speed.
        '''
        elapsed = max(0.0, sim_time - self.start_time)
        radius = config.FIRE_INITIAL_RADIUS + elapsed * config.FIRE_SPREAD_SPEED
        return radius

class Sensor:
    '''
    Represents a single environmental sensor with fixed location.
    '''
    def __init__(self, sensor_id, x, y):
        '''
        Initializes sensor with unique ID and coordinates.
        INPUT:
            - sensor_id: int, unique identifier for the sensor.
            - x, y: float, sensor coordinates in the simulation world.
        '''
        self.sensor_id = sensor_id
        self.x = float(x)
        self.y = float(y)

class SensorSimulator:
    '''
    Manage the grid of sensors and active fires, generating readings each cycle.
    METHODS:
        - advance_time(): advances the simulation clock.
        - reset(): clears all fires and resets time.
        - add_fire(): adds a new fire at specified coordinates.
        - get_fire_snapshots(): creates visualization data for active fires.
        - generate_all(): produces sensor readings with fire effects applied.
    '''
    
    def __init__(self):
        '''
        Create a grid of sensors and set initial state.
        '''
        self.sensors = []
        self.fires = []
        self.sim_time = 0.0
        self._create_grid()

    def _create_grid(self):
        '''
        Create a grid of sensors evenly spaced across the simulation world.
        '''

        # 1: RESET SENSOR STORAGE
        self.sensors = []
        sensor_id = 0

        # 2: CALCULATE QUADRANT SIZE AND SPACING
        quadrant_size = config.WORLD_SIZE / 2
        spacing = quadrant_size / config.GRID_PER_QUADRANT

        # 3: CREATE SENSORS IN ALL FOUR QUADRANTS
        for qy in range(2):
            for qx in range(2):

                # 3.1: DETERMINE QUADRANT OFFSET
                offset_x = qx * quadrant_size
                offset_y = qy * quadrant_size

                # 3.2: FILL QUADRANT WITH SENSORS
                for j in range(config.GRID_PER_QUADRANT):
                    for i in range(config.GRID_PER_QUADRANT):

                        # 3.2.1: CENTER SENSOR WITHIN CELL
                        x = offset_x + (i + 0.5) * spacing
                        y = offset_y + (j + 0.5) * spacing

                        # 3.2.2: CREATE SENSOR, INCREMENT ID
                        self.sensors.append(Sensor(sensor_id, x, y))
                        sensor_id += 1

    def advance_time(self, dt):
        '''
        Advances the simulation clock by a specified delta time.
        INPUT:
            - dt: float, time in seconds to advance the simulation.
        '''
        self.sim_time += max(0.0, dt)

    def reset(self):
        '''
        Resets the simulation by clearing all fires and resetting time.
        '''
        self.fires = []
        self.sim_time = 0.0

    def add_fire(self, x, y):
        '''
        Adds a new fire at the specified coordinates with the current simulation time.
        INPUT:
            - x, y: float, coordinates where the fire should be created.
        '''
        self.fires.append(Fire(x, y, self.sim_time))

    def get_fire_snapshots(self):
        '''
        Creates fire visualization data.
        OUTPUT:
            - snapshots: list of dictionaries with fire properties: {
                "x": float
                "y": float
                "radius": float
                "start_time": float
            }
        '''

        snapshots = []

        # CONVERT FIRE OBJECTS INTO DRAWABLE DICTIONARIES
        for fire in self.fires:
            snapshots.append(
                {
                    "x": fire.x,
                    "y": fire.y,
                    "radius": fire.radius(self.sim_time),
                    "start_time": fire.start_time,
                }
            )

        return snapshots

    def _apply_fire_effects(self, x, y, temperature, humidity, smoke):
        '''
        Apply fire influence to environmental readings
        INPUT:
            - x, y: float, coordinates of the sensor reading.
            - temperature, humidity, smoke: float, baseline readings before fire effects.
        OUTPUT:            
            - temperature, humidity, smoke: float, readings after fire effects.
        '''

        # 1: PROCESS ALL ACTIVE FIRES
        for fire in self.fires:

            # 1.1: DETERMINE CURRENT FIRE RADIUS
            radius = fire.radius(self.sim_time)

            # 1.2: IGNORE INACTIVE FIRES
            if radius <= 0.0:
                continue

            # 1.3: CALCULATE DISTANCE FROM FIRE CENTER
            dx = x - fire.x
            dy = y - fire.y
            distance = math.hypot(dx, dy)

            # 1.4: APPLY EFFECTS ONLY INSIDE RADIUS
            if distance < radius:

                # 1.4.1: SCALE EFFECTS BY DISTANCE IF TAPER ENABLED
                if config.FIRE_LINEAR_TAPER:
                    factor = 1.0 - (distance / radius)
                else:
                    factor = 1.0

                # 1.4.2: MODIFY ENVIRONMENTAL CONDITIONS
                temperature += config.FIRE_TEMPERATURE_INCREASE * factor
                smoke += config.FIRE_SMOKE_INCREASE * factor
                humidity -= config.FIRE_HUMIDITY_DROP * factor

        # 2: LIMIT READINGS TO VALID MIN VALUES
        humidity = max(0.0, humidity)
        smoke = max(0.0, smoke)

        return temperature, humidity, smoke

    def generate_all(self):
        '''
        Generate readings for all sensors.
        OUTPUT:
            - readings: [SensorReading]
        '''

        readings = []

        # 1: Generate one reading per sensor
        for sensor in self.sensors:
            
            # 1.1: Baseline environmental noise
            temperature = config.AMBIENT_TEMPERATURE + random.uniform(
                -config.TEMP_NOISE, config.TEMP_NOISE
            )
            humidity = config.AMBIENT_HUMIDITY + random.uniform(
                -config.HUMIDITY_NOISE, config.HUMIDITY_NOISE
            )
            smoke = max(
                0.0,
                config.AMBIENT_SMOKE + random.uniform(
                    -config.SMOKE_NOISE,
                    config.SMOKE_NOISE,
                ),
            )

            # 1.2: Apply active fire effects
            temperature, humidity, smoke = self._apply_fire_effects(
                sensor.x,
                sensor.y,
                temperature,
                humidity,
                smoke,
            )

            # 1.3: Store completed sensor reading
            readings.append(
                SensorReading(
                    sensor_id=sensor.sensor_id,
                    x=sensor.x,
                    y=sensor.y,
                    temperature=temperature,
                    humidity=humidity,
                    smoke=smoke,
                    timestamp=self.sim_time,
                )
            )

        return readings
