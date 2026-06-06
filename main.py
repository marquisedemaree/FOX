from dashboard.controller import Dashboard
from simulation.state_manager import StateManager


def main():

    # 1: INITIALIZE COMPONENTS
    state = StateManager()
    dashboard = Dashboard()

    # 2: MAIN SIMULATION LOOP
    while state.running:

        # 2.1: TICK DASHBOARD & GET USER ACTIONS
        frame_dt = dashboard.tick()
        actions = dashboard.get_input()

        # 2.2: EXECUTE USER ACTIONS
        state.do_actions(actions)

        # 2.3: ADVANCE TIME
        if not state.paused:
            state.advance(frame_dt)

        # 2.4: GENERATE STATE DICT
        state.get_state_dict()

        # 2.5: VISUALIZE CURRENT STATE
        dashboard.draw(state.state_dict)

    # 3: CLEANUP
    dashboard.close()

if __name__ == "__main__":
    main()
