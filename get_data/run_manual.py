import argparse
import json
import sys
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(PARENT_DIR)

from get_data.src import training_session as ts
from get_data.src import label_handler as lh


def get_args(description):
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--session_template", action="store_true",
                       help="Print the expected session template json to be placed in the 'picture_dir'")
    group.add_argument("-o", "--output_dir", type=str,
                       help="Path to the output directory where the picture shall be saved")
    parser.add_argument("-d", "--delay", type=float, default=0.1,
                        help="Provide the delay (in sec) between 2 capture of images.\n")
    return parser.parse_args()


def run_manual():
    """Run the car in manual mode (control with xbox pad), record pictures and create associated labels."""
    args = get_args(str(run_manual.__doc__))
    if args.session_template:
        print(f'Session template:\n{json.dumps(lh.Label().get_default_session_template(), indent=4)}')
        exit()
    session = ts.TrainingSession(args.delay, output_dir=args.output_dir)

    print("Are you ready to drive?")
    starting_prompt = """Press 'go' + enter to start.
    Press 'show' + enter to start with the printing mode.
    Press 'q' + enter to totally stop the race.
    """
    racing_prompt = """Press 'q' + enter to totally stop the race\n"""
    keep_going = True
    started = False

    try:
        while keep_going:
            user_input = input(racing_prompt) if started else input(starting_prompt)
            if user_input == "go" and not started:
                print("Race is on.")
                session.run(show_mode=False)
                started = True
            elif user_input == "show" and not started:
                print("Race is on. test mode")
                session.run(show_mode=True)
                started = True
            elif user_input == "q":
                keep_going = False
    except KeyboardInterrupt:
        pass
    finally:
        if session:
            session.joy.close()
            session.camera.close()
        print("Race is over.")


if __name__ == "__main__":
    run_manual()
