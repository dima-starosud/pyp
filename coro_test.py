import itertools
from queue import Queue
from threading import Thread


def small_number():
    return 0.001


def compute_one():
    s = 0
    while s < 1.01:
        s += small_number()
    return int(s)


def simple(n):
    i = 0
    while i < n:
        i += compute_one()
    return i


def generator_add_one_gen():
    while True:
        i = yield
        i += compute_one()
        yield i


def generator_step(g, i):
    next(g)
    return g.send(i)


def generator(n, workers_number=2):
    i = 0
    gs = itertools.cycle(generator_add_one_gen() for _ in range(workers_number))
    while i < n:
        g = next(gs)
        i = generator_step(g, i)
    return i


def threads_action(q_in: Queue, q_out: Queue, done, result):
    while not done():
        i = q_in.get()
        i += compute_one()
        q_out.put(i)
        result(i)


def threads(n, workers_number=2):
    qs = [Queue(maxsize=1) for _ in range(workers_number)]
    q_result = Queue()
    _done = False

    def done():
        return _done

    def result(i):
        if i >= n:
            nonlocal _done
            _done = True
            q_result.put(i)

    ts = [
        Thread(target=threads_action, args=(q1, q2, done, result))
        for q1, q2 in zip(qs, itertools.islice(itertools.cycle(qs), 1, None))
    ]
    for t in ts:
        t.start()
    qs[0].put(0)
    r = q_result.get()
    for t in ts:
        t.join()
    return r
