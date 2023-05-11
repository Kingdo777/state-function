def do_create():
    return 0


def do_read():
    return 0


def swap_out_state():
    pass


invoke_index = 1
state_size = 1
min_billing_time = 1


def get_idle_time(invoke_index_):
    return 0


def get_swap_time(invoke_index_):
    return 0


is_last_access = False


def create_state():
    do_create()
    try_release_state()
    ...


def get_state():
    state = do_read()
    try_release_state()
    ...


def try_release_state():
    if is_last_access:
        swap_out_state()
        return
    predicted_IT = get_idle_time(invoke_index)
    estimated_ST = get_swap_time(state_size)
    if predicted_IT - estimated_ST > min_billing_time:
        swap_out_state()
        async Timer.exec(predicted_IT - estimated_ST, swap_in_state)
