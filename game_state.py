from ursina import window
from config import *


class GameState:
    def __init__(self):
        self.score = 0
        self.high_score = 0
        self.health = INITIAL_HEALTH
        self.state = "paused_controls"
        self.has_boss_spawned = False
        self.boss_spawn_score = BOSS_SPAWN_SCORE_INITIAL
        self.bosses_defeated_count = 0
        self.enemies_killed_since_boss = 0
        self.normal_fly_health_bonus = 0

    def reset(self):
        """Reset game state for new game"""
        self.score = 0
        self.health = INITIAL_HEALTH
        self.state = "playing"
        self.has_boss_spawned = False
        self.boss_spawn_score = BOSS_SPAWN_SCORE_INITIAL
        self.bosses_defeated_count = 0
        self.normal_fly_health_bonus = 0
        self.enemies_killed_since_boss = 0

    def get_boss_health(self):
        """Calculate boss health (increases by 3 per defeat)"""
        return BOSS_HEALTH_MAX + (self.bosses_defeated_count * 3)

    def get_fly_health(self):
        """Calculate enemy health based on score"""
        if self.score >= 180:
            base = 6
        elif self.score >= 150:
            base = 5
        elif self.score >= 110:
            base = 4
        elif self.score >= 50:
            base = 3
        elif self.score >= 15:
            base = 2
        else:
            base = 1
        return base + self.normal_fly_health_bonus

    def load_high_score(self):
        """Load high score from storage"""
        try:
            result = window.storage.get("high_score", False)
            if result and hasattr(result, "value") and result.value:
                self.high_score = int(result.value)
        except:
            self.high_score = 0

    def save_high_score(self):
        """Save high score to storage"""
        if self.score > self.high_score:
            self.high_score = self.score
            try:
                window.storage.set("high_score", str(self.high_score), False)
            except:
                pass