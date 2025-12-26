from ursina import *
from config import *


class Player(Animation):
    def __init__(self):
        super().__init__(
            "assets/player", 
            collider="box", 
            y=5, 
            x=-14, 
            enabled=False
        )


class Bullet(Entity):
    def __init__(self, game_state, audio_manager, enemy_spawner, ui_manager, **kwargs):
        super().__init__(
            model="quad",
            texture="assets/Bullet",
            collider="box",
            name="bullet",
            **kwargs,
        )
        self.speed = BULLET_SPEED
        self.game_state = game_state
        self.audio_manager = audio_manager
        self.enemy_spawner = enemy_spawner
        self.ui_manager = ui_manager

    def update(self):
        """Move bullet and check collisions"""
        if self.game_state.state == "playing":
            self.x += self.speed * time.dt

            # Check collision with enemies
            for fly in self.enemy_spawner.flies:
                if self.intersects(fly).hit:
                    self.handle_bullet_hit(fly)
                    return

            # Destroy if off-screen
            if self.x > 15:
                destroy(self)

    def handle_bullet_hit(self, fly):
        """Process bullet hitting an enemy"""
        fly.current_health -= 1
        destroy(self)
        fly.shake(duration=0.1, magnitude=0.5)

        self.audio_manager.play_sound("enemy_damage")

        # Update boss HP display
        if fly.is_boss:
            self.ui_manager.boss_health_text.text = f"BOSS HP: {fly.current_health}"

        # Check if enemy is destroyed
        if fly.current_health <= 0:
            self.ui_manager.show_explosion(fly.position)

            if fly.is_boss:
                score_value = BOSS_POINTS
                self.audio_manager.play_sound("boss_die")
                self.enemy_spawner.handle_boss_defeat()
            else:
                score_value = 1
                self.audio_manager.play_sound("enemy_kill")
                self.game_state.enemies_killed_since_boss += 1

            self.enemy_spawner.flies.remove(fly)
            destroy(fly)
            self.game_state.score += score_value
            self.ui_manager.score_label.text = f"Score: {self.game_state.score}"


class Enemy(Entity):
    def __init__(self, is_boss=False, **kwargs):
        super().__init__(
            model="cube",
            texture="assets/fly",
            collider="box",
            scale=BOSS_SIZE if is_boss else ENEMY_SIZE,
            **kwargs,
        )
        self.current_health = 1
        self.max_health = 1
        self.is_boss = is_boss
        if is_boss:
            self.color = color.red
            self.name = "boss_fly"