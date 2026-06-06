# simulation/state_manager.py

import config
from systems.alerts import AlertManager
from systems.queue_system import MessageQueue
from systems.workers import WorkerManager
from simulation.simulation import SensorSimulator


def build_empty_load_summary():
    '''
    Return a dictionary with initial load summary for each region.
    '''
    return {
        region: {
            "last_batch_count": 0,
            "total_processed": 0,
            "last_detection_count": 0,
            "total_detections": 0,
        }
        for region in config.REGION_NAMES
    }

class StateManager:
    '''
    Manage the overall state of the simulation.
    METHODS:
        - initial_state(): Set all state variables to their initial values.
        - do_actions(actions): Process user actions (pause, reset, add fire).
        - reset(): Reset the simulation to initial state.
        - advance(): Advance the simulation, process events.
        - get_eps(): Calculate and return the current Events Per Second (EPS).
        - get_state_dict(): Return a dictionary with the current sim state.
    '''

    def __init__(self):
        '''
        Initialize the StateManager with all components and set initial state.
        '''

        # 1: INITIALIZE COMPONENTS
        self.simulator = SensorSimulator()
        self.queue = MessageQueue()
        self.workers = WorkerManager()
        self.alerts = AlertManager()

        # 2: SET VARIABLES TO INITIAL STATE
        self.initial_state()
        self.paused = False
        self.running = True

    def initial_state(self):
        '''
        Set all state variables to their initial values.
        '''
        self.emit_accumulator = 0.0
        self.latest_readings = self.simulator.generate_all()
        self.last_events_generated = len(self.latest_readings)
        self.load_summary = build_empty_load_summary()

    def do_actions(self, actions):
        '''
        Process user actions (pause, reset, add fire).
        INPUT: 
            - actions: dict: {
                "quit": bool,
                "toggle_pause": bool,
                "reset": bool,
                "fire_click": (x, y) or None
            }
        '''
        
        if actions["quit"]:
            self.running = False
            self.pause = True
            return
        
        if actions["toggle_pause"]:
            self.paused = not self.paused
        
        if actions["reset"]:
            self.reset()
        
        if actions["fire_click"] is not None:
            self.simulator.add_fire(*actions["fire_click"])
    
    def reset(self):
        '''
        Resets all simulation variables to initial state.
        '''
        self.initial_state()
        self.simulator.reset()
        self.queue.clear()
        self.alerts.reset()
        self.workers.reset_counters()

    def advance(self, frame_dt):
        '''
        Advances the simulation clock and processes sensor events.
        INPUT:          
            - frame_dt: float, seconds since the previous update.
        '''

        # 1: ADVANCE SIMULATION TIME UNTIL NEXT EMISSION CYCLE
        self.simulator.advance_time(frame_dt)
        self.emit_accumulator += frame_dt

        # 2: RUN SENSOR UPDATE IF ENOUGH TIME HAS PASSED
        while self.emit_accumulator >= config.SENSOR_INTERVAL:

            # 2.1: NEW ALERT TICK, GET READINGS, PUSH TO QUEUE
            self.alerts.begin_tick()
            self.latest_readings = self.simulator.generate_all()
            self.queue.push_batch(self.latest_readings)

            # 2.2: DRAIN QUEUE, PROCESS, UPDATE SUMMARY
            self.queued_events = self.queue.drain()
            self.processed = self.workers.process_batch(self.queued_events)
            self.load_summary = self.workers.get_load_summary()

            # 2.3: CONVERT DETECTED FIRES INTO ALERTS
            self.alerts.ingest_processed_events(self.processed)

            # 2.4: STORE STATISTICS, REMOVE CYCLE FROM ACCUMULATOR
            self.last_events_generated = len(self.latest_readings)
            self.emit_accumulator -= config.SENSOR_INTERVAL

    def get_eps(self):
        '''
        Returns a float for EPS - Events Per Second.
        '''
        return (
                self.last_events_generated / config.SENSOR_INTERVAL
                if config.SENSOR_INTERVAL > 0
                else 0.0
            )
    
    def get_state_dict(self):
        '''
        Returns a dictionary with the current simulation state.
        OUTPUT: 
            - dict {
                "paused": bool,
                "sim_time": float,
                "sensor_interval": float,
                "sensor_count": int,
                "fire_count": int,
                "events_per_second": float,
                "queue_size": int,
                "alerts_this_tick": int,
                "total_alerts": int,
                "recent_alerts": list of dict,
                "load_summary": dict,
                "readings": list of dict,
                "fires": list of dict
            }
        '''
        self.state_dict = {
            "paused": self.paused,
            "sim_time": self.simulator.sim_time,
            "sensor_interval": config.SENSOR_INTERVAL,
            "sensor_count": len(self.simulator.sensors),
            "fire_count": len(self.simulator.fires),
            "events_per_second": self.get_eps(),
            "queue_size": self.queue.size(),
            "alerts_this_tick": self.alerts.get_last_tick_count(),
            "total_alerts": self.alerts.get_total_alert_count(),
            "recent_alerts": self.alerts.get_recent_alerts(),
            "load_summary": self.load_summary,
            "readings": self.latest_readings,
            "fires": self.simulator.get_fire_snapshots()
        }
