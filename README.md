# FOX
FOX - Fire Observation eXchange
A scalable distributed system for early wildfire detection.

## Quick Start
These instructions will help you run RAT locally for demo and evaluation.

### Prerequisites
- Git
- Python 3.10+

Not sure if you meet these requirements? Follow this guide: https://github.com/marquisedemaree/prerequisites/blob/main/README.md

### Installation
From the command line:

1. Clone the repository: `git clone https://github.com/marquisedemaree/FOX.git`

2. Change the directory to RAT: `cd FOX`

3. Create a Virtual Environment: `python3 -m venv .venv`

4. Activate Virtual Environment:
    - Mac: `source .venv/bin/activate`
    - Windows: `.venv\Scripts\activate` 

5. Install dependencies: `pip install -r requirements.txt`

## Usage
Run the full FOX pipeline: `python main.py`

This will:

- Launch the interactive Pygame dashboard.
- Initialize 1,024 virtual environmental sensors arranged across four geographic regions.
- Generate temperature, humidity, and smoke readings at regular intervals.
- Stream sensor events through a simulated message queue.
- Route events to four regional worker nodes for parallel processing.
- Evaluate detection rules and generate wildfire alerts when fire conditions are detected.
- Visualize sensors, active fires, system metrics, and alerts in real time.
- Allow users to create fires, pause the simulation, and reset the environment. :contentReference[oaicite:0]{index=0}

### Controls
| Key | Action |
|------|---------|
| Left Click | Create a fire at the selected location |
| Space | Pause / Resume simulation |
| R | Reset simulation |
| Close Window | Exit application |

## Features
- Distributed Sensor Network: Simulates 1,024 environmental sensors across a 32×32 grid. 
- Message Queue Pipeline: Buffers and streams sensor events through a thread-safe FIFO queue. 
- Regional Partitioning: Routes events to four geographic regions (NorthWest, NorthEast, SouthWest, SouthEast). 
- Parallel Event Processing: Uses worker threads to process regional sensor data concurrently. 
- Wildfire Detection Engine: Detects fire conditions using temperature, smoke, and humidity thresholds. 
- Severity-Based Alerting: Classifies detections as low, medium, or high severity and maintains alert history. 
- Dynamic Fire Simulation: Models expanding wildfire zones that influence nearby sensor readings over time. 
- Real-Time Dashboard: Displays sensor status, active fires, alerts, queue activity, and performance metrics. 
- Interactive Scenario Creation: Users can create fires anywhere on the map and immediately observe system behavior. 
- Portfolio-Ready Distributed Systems Demonstration: Showcases event streaming, message queues, regional partitioning, parallel processing, and real-time visualization in a single application. :contentReference[oaicite:10]{index=10}
