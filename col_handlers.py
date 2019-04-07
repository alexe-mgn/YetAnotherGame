from config import *


class HandlerTracked:

    @staticmethod
    def begin(arbiter, space, data):
        sha, shb = arbiter.shapes
        ba, bb = sha.body, shb.body
        sa, sb = ba.sprite, bb.sprite
        return sa.collideable(sb) and sb.collideable(sa)

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
