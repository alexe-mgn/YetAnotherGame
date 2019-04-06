from config import *


class HandlerTracked:

    @staticmethod
    def begin(arbiter, space, data):
        print(arbiter)
        return True

    @staticmethod
    def pre_solve(arbiter, space, data):
        return True

    @staticmethod
    def post_solve(arbiter, space, data):
        return

    @staticmethod
    def separate(arbiter, space, data):
        return


handlers = {
    COLLISION_TYPE.TRACKED: HandlerTracked
}


def get_handler(col_type):
    return handlers.get(col_type, None)
