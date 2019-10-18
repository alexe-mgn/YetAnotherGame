from Engine.config import COLLISION_TYPE

import math

"""
pymunk collision handlers
"""

"""
class Handler:

    @staticmethod
    def begin(arbiter, space, data):
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
"""


class HandlerTracked:

    @staticmethod
    def begin(arbiter, space, data):
        sha, shb = arbiter.shapes
        ba, bb = sha.body, shb.body
        sa, sb = getattr(ba, 'sprite', None), getattr(bb, 'sprite', None)
        if sa is None or sb is None:
            return True
        col = sa.collideable(sb) and sb.collideable(sa)
        if col:
            data['sprite_a'], data['sprite_b'] = sa, sb

            def f(*args):
                sa.effect(sb, arbiter, first=True)
                sb.effect(sa, arbiter, first=False)
                sa.post_effect(sb, arbiter, first=True)
                sb.post_effect(sa, arbiter, first=False)

            space.add_post_step_callback(f, frozenset((id(sa), id(sb))))
        return col


class HandlerProjectile(HandlerTracked):

    @staticmethod
    def separate(arbiter, space, data):
        ss = arbiter.shapes[0]
        sprite = ss.body.sprite
        if sprite:
            vel = sprite.velocity
            sprite.angle = math.degrees(math.atan2(vel[1], vel[0]))
        return


handlers = {
    COLLISION_TYPE.TRACKED: HandlerTracked,
    COLLISION_TYPE.PROJECTILE: HandlerProjectile
}


def get_handler(col_type):
    return handlers.get(col_type, None)
