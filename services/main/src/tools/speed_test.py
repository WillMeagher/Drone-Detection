import time

class SpeedTest:

    def __init__(self, loops_per_print=100):
        self.loops_per_print = loops_per_print
        self.cur_loop = 0
        self.total_loops = 0
        self.loops_per_second = 0
        self.start = time.time()


    def loop(self, print_loops=False):
        self.cur_loop += 1
        self.total_loops += 1

        if self.cur_loop == self.loops_per_print:
            self.cur_loop = 0
            end = time.time()
            elapsed = end - self.start
            self.loops_per_second = self.loops_per_print / elapsed
            if print_loops:
                print(str(self.loops_per_second) + " loops per second")
            self.start = end

    def get_loops_per_second(self):
        return self.loops_per_second

    def get_total_loops(self):
        return self.total_loops