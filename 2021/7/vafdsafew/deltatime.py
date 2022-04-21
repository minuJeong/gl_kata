import glfw


class Time(object):
    time = 0
    elapsed_frames = 0
    elapsed_time = 0
    delta_time = 0
    framerate = 0

    _prev_time = 0

    @staticmethod
    def next_frame():
        Time.elapsed_frames += 1

        t = glfw.get_time()

        Time.time = t
        Time.elapsed_time = t
        Time.delta_time = t - Time._prev_time
        Time.framerate = 1.0 / Time.delta_time

        Time._prev_time = t