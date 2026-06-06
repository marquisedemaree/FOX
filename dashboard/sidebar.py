# dashboard/sidebar.py

import pygame
import config


def _alert_color(severity):
    '''
    Defines color-coding for alerts based on severity.
    INPUT:      
        - severity: str, "low", "medium", or "high"
    RETURN:     
        - (int, int, int) for alert color
    '''
    if severity == "high":
        return config.ALERT_HIGH_COLOR
    if severity == "medium":
        return config.ALERT_MEDIUM_COLOR
    return config.ALERT_LOW_COLOR

def _blit_text(self, text, font, color, x, y):
    '''
    Helper function to blit text and return new y position.
    INPUT:
        - text: str to render
        - font: pygame Font object
        - color: (int, int, int) for text color
        - x: int, x-coordinate to blit text
        - y: int, y-coordinate to blit text
    RETURN:     
        - int, new y-coordinate after blitting text
    '''
    surface = font.render(text, True, color)
    self.screen.blit(surface, (x, y))
    return y + surface.get_height()

def _draw_container(self, pos):
    '''
    Draws sidebar container background.
    INPUT:
        - pos: dict with "x" and "y" for initial draw position
    '''
    pygame.draw.rect(
            self.screen,
            config.SIDEBAR_BG_COLOR,
            (pos["x"], 0, config.SIDEBAR_WIDTH, config.WORLD_SIZE),
        )

def _draw_title(self, pos):
    '''
    Draws dashboard title at top of sidebar.
    INPUT:
        - pos: dict with "x" and "y" for initial draw position
    '''
    pos["y"] = _blit_text(
        self, 
        "FOX Dashboard", 
        self.font_large, 
        config.TEXT_COLOR, 
        pos["x"] + 18, 
        pos["y"]
    )

def _draw_status(self, pos, state_dict):
    '''
    Draws simulation status section in sidebar.
    INPUT:
        - pos: dict with "x" and "y" for current draw position
        - state_dict: dict with simulation state entries: {
            "paused": bool
            "sim_time": float
            "sensor_interval": float
        }
    '''
    
    # 1: Spacing before section
    pos["y"] += 10

    # 2: Get simulation status text 
    status_text = "Paused" if state_dict["paused"] else "Running"

    # 3: Draw simulation status
    pos["y"] = _blit_text(
        self,
        f"Status: {status_text}",
        self.font_medium,
        config.TEXT_COLOR,
        pos["x"] + 18,
        pos["y"],
    )

    # 4: Simulation time
    pos["y"] = _blit_text(
        self,
        f"Simulation time: {state_dict['sim_time']:.1f}s",
        self.font_small,
        config.MUTED_TEXT_COLOR,
        pos["x"] + 18,
        pos["y"] + 2,
    )

    # 5: Sensor emission interval
    pos["y"] = _blit_text(
        self,
        f"Tick interval: {state_dict['sensor_interval']:.1f}s",
        self.font_small,
        config.MUTED_TEXT_COLOR,
        pos["x"] + 18,
        pos["y"] + 2,
    )

def _draw_metrics(self, pos, state_dict):
    '''
    Draws simulation metrics section in sidebar.
    INPUT:
        - pos: dict with "x" and "y" for current draw position
        - state_dict: dict with simulation state: {
            "sensor_count": int
            "fire_count": int
            "events_per_second": float
            "queue_size": int
            "total_alerts": int
            "alerts_this_tick": int
        }
    '''

    # 1: Spacing before section
    pos["y"] += 14

    # 2: Metrics section title
    pos["y"] = _blit_text(
        self, 
        "Metrics", 
        self.font_medium, 
        config.TEXT_COLOR, 
        pos["x"] + 18, 
        pos["y"]
    )

    # 3: Metrics display lines
    metrics = [
        f"Active sensors: {state_dict['sensor_count']}",
        f"Fires: {state_dict['fire_count']}",
        f"Events/sec: {state_dict['events_per_second']:.1f}",
        f"Queue size: {state_dict['queue_size']}",
        f"Alerts total: {state_dict['total_alerts']}",
        f"Alerts this tick: {state_dict['alerts_this_tick']}",
    ]

    # 4: Draw each metrics line
    for line in metrics:
        pos["y"] = _blit_text(
            self, 
            line, 
            self.font_small, 
            config.TEXT_COLOR, 
            pos["x"] + 18, 
            pos["y"] + 6
        )

def _draw_controls(self, pos):
    '''
    Draws user control instructions in sidebar.
    INPUT:
        - pos: dict with "x" and "y" for current draw position
    '''

    # 1: Spacing before section
    pos["y"] += 14

    # 2: Controls section title
    pos["y"] = _blit_text(
        self, "Controls", 
        self.font_medium, 
        config.TEXT_COLOR, 
        pos["x"] + 18, 
        pos["y"]
    )

    # 3: Control instruction lines
    controls = [
        "Click map  - create fire",
        "Space      - pause/resume",
        "R          - reset simulation",
    ]

    # 4: Draw each control instruction
    for line in controls:
        pos["y"] = _blit_text(
            self, 
            line, 
            self.font_small, 
            config.TEXT_COLOR, 
            pos["x"] + 18, 
            pos["y"] + 6
        )

def _draw_alerts(self, pos, state_dict):
    '''
    Draws recent alert feed in sidebar.
    INPUT:
        - pos: dict with "x" and "y" for current draw position
        - state_dict: dict with simulation state: {"recent_alerts": [Alert]}
    '''
    
    # 1: Spacing before section
    pos["y"] += 14

    # 2: Alert feed section title
    pos["y"] = _blit_text(
        self, 
        "Recent Alerts", 
        self.font_medium, 
        config.TEXT_COLOR, 
        pos["x"] + 18, 
        pos["y"]
    )

    # 3: Get most recent alert list
    recent_alerts = state_dict["recent_alerts"]

    # 4: Empty alert feed message
    if not recent_alerts:
        _blit_text(
            self,
            "No alerts yet",
            self.font_small,
            config.MUTED_TEXT_COLOR,
            pos["x"] + 18,
            pos["y"] + 8,
        )
        return

    # 5: Draw recent alerts from newest to oldest
    for alert in reversed(recent_alerts[-config.MAX_ALERT_FEED:]):

        # 5.1: Get alert details
        color = _alert_color(alert.severity)
        line1 = f"[t={alert.timestamp:.1f}] {alert.region}"
        line2 = f"{alert.severity.upper()} @ ({int(alert.x)}, {int(alert.y)})"

        # 5.2: Draw alert details
        pos["y"] = _blit_text(
            self,
            line1, 
            self.font_small, 
            color, 
            pos["x"] + 18, 
            pos["y"] + 8
        )
        pos["y"] = _blit_text(
            self,
            line2,
            self.font_small,
            config.MUTED_TEXT_COLOR,
            pos["x"] + 28,
            pos["y"] + 2,
        )

        # 5.3: Stop drawing if sidebar fills vertically
        if pos["y"] > config.WORLD_SIZE - 30:
            break

def draw_sidebar(self, state_dict):
        '''
        Draws a dashboard sidebar with instructions, simulation stats, & alerts
        INPUT:
            - state_dict: dict: {
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

        # 1: Define initial draw positions
        pos = {"x":config.WORLD_SIZE, "y":18}

        # 2: Basic sidebar setup
        _draw_container(self, pos)
        _draw_title(self, pos)        

        # 3: Draw sidebar elements
        _draw_status(self, pos, state_dict)
        _draw_metrics(self, pos, state_dict)
        _draw_controls(self, pos)
        _draw_alerts(self, pos, state_dict)
