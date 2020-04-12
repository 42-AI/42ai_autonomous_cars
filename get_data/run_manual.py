import argparse
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).absolute().parents[1]))
from get_data.src import training_session as ts
from get_data.src import init_picture_folder as init


def get_args(description):
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-o", "--picture_dir", type=str,
                       help="Path to the output directory where the picture shall be saved")
    parser.add_argument("-d", "--delay", type=float, default=0.1,
                        help="Provide the delay (in sec) between 2 capture of images.\n")
    return parser.parse_args()


def run_manual():
    """
    Run the car in manual mode (control with xbox pad), record pictures and create associated labels. You can use a
    non-existing directory for automatic creation of the picture directory along with its session template.
    """
    args = get_args(str(run_manual.__doc__))
    init.init_picture_folder(picture_dir=args.picture_dir)
    session = ts.TrainingSession(args.delay, output_dir=args.picture_dir)

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
