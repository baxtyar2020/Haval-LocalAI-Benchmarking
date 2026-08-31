"""Rising Game Developer Phase 1: Unity loops as executable Python."""

G_RD_L_TESTS = """
p = CoinCollector()
p.move(1)
assert p.x > 0
p.grounded = True
p.jump()
assert p.vy > 0
air = p.vy
p.grounded = False
p.jump()
assert p.vy == air
assert p.collect("Coin") is True and p.score == 1
assert p.collect("Enemy") is False
"""

G_RD_L_SEED = """
class CoinCollector:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.vy = 0.0
        self.grounded = True
        self.score = 0
    def move(self, axis):
        self.x += float(axis) * 6.0
    def jump(self):
        if self.grounded:
            self.vy = 11.0
            self.grounded = False
    def collect(self, tag):
        if tag != "Coin":
            return False
        self.score += 1
        return True
"""

G_RD_L_BAD = """
class CoinCollector:
    def __init__(self):
        self.x = 0
        self.vy = 0
        self.grounded = False
        self.score = 0
    def move(self, axis):
        self.x += 100
    def jump(self):
        self.vy = 11
    def collect(self, tag):
        self.score += 1
        return True
"""

G_RD_B_TESTS = """
c = PatrolChaser(0.0, 0.0, 10.0, detect=5.0, lose=8.0)
assert c.state == "patrol"
c.set_player(3.0)
c.step()
assert c.state == "chase"
c.set_player(100.0)
c.step()
assert c.state == "return"
c.x = c.home
c.step()
assert c.state == "patrol"
"""

G_RD_B_SEED = """
class PatrolChaser:
    def __init__(self, x, point_a, point_b, detect=5.0, lose=8.0):
        self.x = float(x)
        self.a = float(point_a)
        self.b = float(point_b)
        self.detect = float(detect)
        self.lose = float(lose)
        self.state = "patrol"
        self.target = self.b
        self.home = float(x)
        self.player = None
    def set_player(self, px):
        self.player = float(px)
    def _walk(self, dest, speed):
        if self.x < dest:
            self.x = min(dest, self.x + speed)
        elif self.x > dest:
            self.x = max(dest, self.x - speed)
    def step(self):
        if self.player is None:
            return
        d = abs(self.x - self.player)
        if self.state == "patrol":
            self._walk(self.target, 2.0)
            if abs(self.x - self.target) <= 0.15:
                self.target = self.a if self.target == self.b else self.b
            if d <= self.detect:
                self.state = "chase"
        elif self.state == "chase":
            self._walk(self.player, 4.0)
            if d > self.lose:
                self.state = "return"
        elif self.state == "return":
            self._walk(self.home, 2.0)
            if abs(self.x - self.home) <= 0.15:
                self.state = "patrol"
"""

G_RD_B_BAD = """
class PatrolChaser:
    def __init__(self, x, point_a, point_b, detect=5.0, lose=8.0):
        self.state = "patrol"
        self.home = x
    def set_player(self, px):
        pass
    def step(self):
        self.state = "patrol"
"""

G_RD_H_TESTS = """
d = PlayerDash()
assert d.try_dash(0.0, 1, 100.0) is True
assert d.try_dash(0.1, 1, 100.0) is False
d2 = PlayerDash()
ok = d2.try_dash(0.0, 1, 0.5)
assert ok is True
assert d2.x < 0.5
b = PlayerDash()
assert b.dash_broken(0.0, 1, 100.0) is True
assert b.dash_broken(0.05, 1, 100.0) is True
"""

G_RD_H_SEED = """
class PlayerDash:
    def __init__(self, dash_speed=18.0, dash_time=0.14, cooldown=0.45):
        self.dash_speed = dash_speed
        self.dash_time = dash_time
        self.cooldown = cooldown
        self.dashing = False
        self.cooldown_until = -1.0
        self.x = 0.0
    def try_dash(self, now, facing, wall_dist):
        if self.dashing or now < self.cooldown_until:
            return False
        self.dashing = True
        self.cooldown_until = now + self.cooldown
        step = self.dash_speed * self.dash_time
        sign = 1.0 if facing >= 0 else -1.0
        if wall_dist < step:
            self.x += max(0.0, wall_dist - 0.05) * sign
        else:
            self.x += step * sign
        self.dashing = False
        return True
    def dash_broken(self, now, facing, wall_dist):
        step = self.dash_speed * self.dash_time
        sign = 1.0 if facing >= 0 else -1.0
        self.x += step * sign
        return True
"""

G_RD_H_BAD = """
class PlayerDash:
    def __init__(self, dash_speed=18.0, dash_time=0.14, cooldown=0.45):
        self.x = 0.0
    def try_dash(self, now, facing, wall_dist):
        self.x += 100
        return True
    def dash_broken(self, now, facing, wall_dist):
        return False
"""
