import time

from threading import Thread
from queue import Queue


class RaceOn:
    def __init__(self):
        # Racing_status
        self.racing = False

    def check(self, queue_input):
        keep_going = True
        n = 0
        start_time = time.time()
        while keep_going:
            n += 1
            # print(queue_input)

            if not queue_input.empty():
                user_input = queue_input.get(block=False)
                if user_input == "q":
                    # previous = self.racing
                    delta_time = time.time() - start_time
                    print(n, delta_time)
                    keep_going = False
                    self.racing = False
                elif user_input == "p":
                    self.racing = not self.racing
                else:
                    self.racing = True

            self.race()



            # test exception

            # try:
            #     user_input = queue_input.get(block=False)
            #     # previous = self.racing
            #     if user_input == "q":
            #         delta_time = time.time() - start_time
            #         print(n, delta_time)
            #         keep_going = False
            #         self.racing = False
            #     elif user_input == "p":
            #         self.racing = not self.racing
            #     else:
            #         self.racing = True
            # except:
            #     pass
            # finally:
            #     self.race()



            # print(self.racing)
            # if previous is False and self.racing is True:
            #     print("FeqrrfFFREQFEQRREQ=====")
            #     self.race()


    def race(self):
        # self.racing = True
        if self.racing:
            print("racing")
        # n = 0
        # while self.racing:
        #    n +=1
        # return n

    # TODO (pclement) reinitialize to init values
    def stop(self):
        self.racing = False




def get_input(out_q):
    while True:
        user_input = input("q to quit")
        out_q.put(user_input)
        if user_input == "q":
            break



if __name__ == '__main__':

    if __name__ == '__main__':
        race_on = None
        race_on = RaceOn()
        print("Are you ready ?")

        racing_prompt = """Press 'q' + enter to totally stop the race\n"""
        try:
            q = Queue()
            input_thread = Thread(target=get_input, args=(q,))
            race_thread = Thread(target=race_on.check, args=(q,))
            input_thread.start()
            race_thread.start()
            # keep_going = True
            # while keep_going:
            #     Thread(race_on.check_status, args=(q,))
            #     user_input = input("q to quit")
            #     if user_input == 'q':




        except KeyboardInterrupt:
            if race_on is not None:
                race_on.stop()
        finally:
            if race_on is not None:
                race_on.stop()
