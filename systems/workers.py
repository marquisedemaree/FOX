# systems/workers.py

from concurrent.futures import ThreadPoolExecutor

import config


def get_region_name(x, y, world_size=None):
    '''
    Determine the region name based on the coordinates.
    INPUT: 
        - x, y: int
        - world_size: int
    OUTPUT: 
        - str: "NorthWest", "NorthEast", "SouthWest", or "SouthEast"
    '''
    
    # 1: DETERMINE MIDPOINT
    size = config.WORLD_SIZE if world_size is None else world_size
    mid = size / 2

    # 2: CLASSIFY QUADRANT
    north = y < mid
    west = x < mid

    # 3: RETURN REGION NAME
    if north and west:
        return "NorthWest"
    if north and not west:
        return "NorthEast"
    if not north and west:
        return "SouthWest"
    return "SouthEast"


def compute_severity_score(temperature, humidity, smoke):
    '''
    Compute the severity score based on environmental readings.
    INPUT: 
        - temperature, humidity, smoke: float
    OUTPUT: 
        - float
    '''

    # 1: CALCULATE EXCESS/DEFICIT
    temp_excess = max(0.0, temperature - config.TEMP_ALERT_THRESHOLD)
    smoke_excess = max(0.0, smoke - config.SMOKE_ALERT_THRESHOLD)
    humidity_drop = max(0.0, config.HUMIDITY_ALERT_THRESHOLD - humidity)

    # 2: WEIGHT AND SUM
    score = (
        temp_excess * config.TEMP_SCORE_WEIGHT
        + smoke_excess * config.SMOKE_SCORE_WEIGHT
        + humidity_drop * config.HUMIDITY_SCORE_WEIGHT
    )

    return score


def classify_severity(score):
    '''
    Return severity level based on score thresholds.
    INPUT: 
        - score: float
    OUTPUT: 
        - str: "low", "medium", or "high"
    '''

    if score >= config.SEVERITY_SCORE_MEDIUM:
        return "high"
    
    if score >= config.SEVERITY_SCORE_LOW:
        return "medium"
    
    return "low"


def evaluate_detection(event):
    '''
    Evaluate the detection of an event based on its environmental readings.
    INPUT: 
        - event: Event
    OUTPUT: 
        - dict: {
            "detected": bool,
            "temp_trigger": bool,
            "humidity_trigger": bool,
            "smoke_trigger": bool,
                "severity_score": float,
                "severity": str or None
            }
    '''

    # 1: CHECK TRIGGERS
    temp_trigger = event.temperature > config.TEMP_ALERT_THRESHOLD
    humidity_trigger = event.humidity < config.HUMIDITY_ALERT_THRESHOLD
    smoke_trigger = event.smoke > config.SMOKE_ALERT_THRESHOLD

    # 2: DETERMINE IF EVENT IS DETECTED
    detected = temp_trigger and humidity_trigger and smoke_trigger

    # 3: COMPUTE SEVERITY
    severity_score = 0.0
    severity = None

    # 4: COMPUTE SEVERITY IF ALL TRIGGERS ARE ACTIVE
    if detected:
        severity_score = compute_severity_score(
            event.temperature,
            event.humidity,
            event.smoke,
        )
        severity = classify_severity(severity_score)

    return {
        "detected": detected,
        "temp_trigger": temp_trigger,
        "humidity_trigger": humidity_trigger,
        "smoke_trigger": smoke_trigger,
        "severity_score": severity_score,
        "severity": severity,
    }


class RegionalWorker:
    '''
    Worker responsible for processing events in a specific region.
    Each worker maintains counters for processed events and detections.
    METHODS:
        - process_events(events): Process a batch of events and update counters.
    '''

    def __init__(self, region_name):
        '''
        Initialize the worker with a region name and reset counters.
        INPUT: 
            - region_name: str
        '''
        self.region_name = region_name
        self.last_batch_count = 0
        self.total_processed = 0
        self.last_detection_count = 0
        self.total_detections = 0

    def process_events(self, events):
        '''
        Process a batch of events, evaluate detections, and update counters.
        INPUT: 
            - events: [Event]
        OUTPUT: 
            - [dict] with processed event data and detection results
        '''

        processed = []
        detection_count = 0

        # 1: PROCESS EACH EVENT
        for event in events:

            # 1.1: EVALUATE DETECTION
            detection = evaluate_detection(event)

            # 1.2: UPDATE DETECTION COUNT
            if detection["detected"]:
                detection_count += 1

            # 1.3: APPEND PROCESSED EVENT DATA
            processed.append(
                {
                    "region": self.region_name,
                    "sensor_id": event.sensor_id,
                    "x": event.x,
                    "y": event.y,
                    "temperature": event.temperature,
                    "humidity": event.humidity,
                    "smoke": event.smoke,
                    "timestamp": event.timestamp,
                    "detected": detection["detected"],
                    "temp_trigger": detection["temp_trigger"],
                    "humidity_trigger": detection["humidity_trigger"],
                    "smoke_trigger": detection["smoke_trigger"],
                    "severity_score": detection["severity_score"],
                    "severity": detection["severity"],
                }
            )

        # 2: UPDATE WORKER COUNTERS
        self.last_batch_count = len(processed)
        self.total_processed += len(processed)
        self.last_detection_count = detection_count
        self.total_detections += detection_count

        return processed


class WorkerManager:
    '''
    Route events to regional workers and aggregate results.
    METHODS:
        - route_events(events): Route events to the correct regional workers.
        - process_batch(events): Process a batch of events in parallel.
        - get_load_summary(): Get a summary of current load and detection counts.
        - reset_counters(): Reset all worker counters for a new simulation run.
    '''

    def __init__(self):
        '''
        Initialize the worker manager and create workers for each region.
        '''
        self.workers = {
            name: RegionalWorker(name) for name in config.REGION_NAMES
        }

    def route_events(self, events):
        '''
        Route events to the appropriate regional workers based on their coordinates.
        INPUT: 
            - events: list of Event
        OUTPUT: 
            - dict: {region_name: list of Event}
        '''

        routed = {name: [] for name in config.REGION_NAMES}

        # ROUTE EACH EVENT TO THE CORRECT REGION
        for event in events:
            region = get_region_name(event.x, event.y, config.WORLD_SIZE)
            routed[region].append(event)

        return routed

    def process_batch(self, events):
        '''
        Process a batch of events by routing them to regional workers.
        INPUT: 
            - events: list of Event
        OUTPUT: 
            - dict: {region_name: list of processed event data}
        '''

        routed = self.route_events(events)
        results = {}

        # 1: PROCESS EACH REGION IN PARALLEL
        with ThreadPoolExecutor(max_workers=4) as executor:
            
            # 1.1: SUBMIT TASKS FOR EACH REGION
            future_map = {
                region: executor.submit(
                    self.workers[region].process_events,
                    region_events,
                )
                for region, region_events in routed.items()
            }

            # 1.2: COLLECT RESULTS AS THEY COMPLETE
            for region, future in future_map.items():
                results[region] = future.result()

        return results

    def get_load_summary(self):
        '''
        Get a summary of the current load and detection counts for each region.
        OUTPUT: 
            - dict: {region_name: {
                "last_batch_count": int,
                "total_processed": int,
                "last_detection_count": int,
                "total_detections": int
            }}
        '''
        return {
            region: {
                "last_batch_count": worker.last_batch_count,
                "total_processed": worker.total_processed,
                "last_detection_count": worker.last_detection_count,
                "total_detections": worker.total_detections,
            }
            for region, worker in self.workers.items()
        }

    def reset_counters(self):
        '''
        Reset the counters for all workers to start a new simulation run.
        '''
        for worker in self.workers.values():
            worker.last_batch_count = 0
            worker.total_processed = 0
            worker.last_detection_count = 0
            worker.total_detections = 0
