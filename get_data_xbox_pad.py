import argparse

from get_data.utils import training_session as ts


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("delay", type=float,
                        help="Provide the delay between 2 capture of images.\n")
    parser.add_argument("output_dir", type=str, help="Path to the directory where the picture shall be saved")
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
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
