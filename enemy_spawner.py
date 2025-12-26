from ursina import *
import random
from config import *
from entities import Enemy


class EnemySpawner:
    def __init__(self, game_state, audio_manager, ui_manager):
        self.game_state = game_state
        self.audio_manager = audio_manager
        self.ui_manager = ui_manager
        self.flies = []
        self.spawn_timer = None
        self.game_over_callback = None

    def reset(self):
        """Clear all enemies"""
        for fly in self.flies:
            destroy(fly)
        self.flies.clear()
        if self.spawn_timer:
            self.spawn_timer.finish()
            self.spawn_timer = None

    def pause_spawning(self):
        """Pause enemy spawning"""
        if self.spawn_timer:
            self.spawn_timer.pause()

    def resume_spawning(self):
        """Resume enemy spawning"""
        if self.spawn_timer and self.spawn_timer.paused:
            self.spawn_timer.resume()
        else:
            invoke(self.spawn_fly, delay=1.0)

    def stop_spawning(self):
        """Stop spawning completely"""
        if self.spawn_timer:
            self.spawn_timer.pause()

    def hide_all_enemies(self):
        """Hide all enemies"""
        for fly in self.flies:
            fly.enabled = False

    def is_overlap(self, new_y, existing_flies):
        """Check if spawn position overlaps"""
        for fly in existing_flies:
            gap = fly.scale_y * 1.8
            if abs(new_y - fly.y) < gap:
                return True
        return False

    def spawn_fly(self):
        """Spawn regular enemies automatically"""
        if self.game_state.state != "playing":
            return

        # Check if boss should spawn
        if (
            self.game_state.score >= self.game_state.boss_spawn_score
            and not self.game_state.has_boss_spawned
            and self.game_state.enemies_killed_since_boss >= MIN_ENEMIES_BEFORE_BOSS
        ):
            self.show_boss_warning()
            return

        # Don't spawn during boss fight
        if self.game_state.has_boss_spawned:
            self.spawn_timer = invoke(self.spawn_fly, delay=2.0)
            return

        # Find valid spawn position
        nearby = [f for f in self.flies if f.x > 15]
        spawn_y = None

        for _ in range(10):
            y = random.uniform(MIN_Y, MAX_Y)
            if not self.is_overlap(y, nearby):
                spawn_y = y
                break

        # Spawn enemy
        if spawn_y is not None:
            new = Enemy(x=20, y=spawn_y, visible=True)
            new.current_health = self.game_state.get_fly_health()
            new.max_health = new.current_health
            self.flies.append(new)

        # Calculate next spawn delay
        delay = max(
            MIN_SPAWN_DELAY,
            BASE_SPAWN_DELAY - (self.game_state.score * SPAWN_DELAY_REDUCTION_RATE),
        )
        self.spawn_timer = invoke(self.spawn_fly, delay=delay)

    def show_boss_warning(self):
        """Show warning before boss spawns"""
        camera.shake(duration=2, magnitude=2)
        self.audio_manager.start_boss_music()
        invoke(self.spawn_boss_actual, delay=2)

    def spawn_boss_actual(self):
        """Create and spawn boss"""
        if self.spawn_timer:
            self.spawn_timer.pause()

        boss_health = self.game_state.get_boss_health()
        boss = Enemy(
            is_boss=True,
            x=20,
            y=random.uniform(MIN_Y + 2, MAX_Y - 2),
            visible=True,
        )
        boss.current_health = boss_health
        boss.max_health = boss_health
        self.flies.append(boss)
        self.game_state.has_boss_spawned = True

        # Show boss HP
        self.ui_manager.boss_health_text.text = f"BOSS HP: {boss_health}"
        self.ui_manager.boss_health_text.enabled = True

    def handle_boss_defeat(self):
        """Handle boss being defeated"""
        self.game_state.has_boss_spawned = False
        self.game_state.bosses_defeated_count += 1
        self.game_state.enemies_killed_since_boss = 0

        self.ui_manager.boss_health_text.enabled = False
        self.audio_manager.stop_boss_music()

        # Increase difficulty every 2 bosses
        if self.game_state.bosses_defeated_count % 2 == 0:
            self.game_state.normal_fly_health_bonus += 1

        self.game_state.boss_spawn_score = (
            self.game_state.score + MIN_ENEMIES_BEFORE_BOSS
        )

        # Resume spawning
        if self.spawn_timer:
            self.spawn_timer.finish()
        invoke(self.spawn_fly, delay=1.0)

    def handle_boss_escape(self):
        """Handle boss escaping"""
        self.game_state.has_boss_spawned = False
        self.game_state.enemies_killed_since_boss = 0
        self.game_state.boss_spawn_score = (
            self.game_state.score + MIN_ENEMIES_BEFORE_BOSS
        )

        self.ui_manager.boss_health_text.enabled = False
        self.audio_manager.stop_boss_music()

        # Resume spawning
        if self.spawn_timer and self.spawn_timer.paused:
            self.spawn_timer.resume()
        else:
            invoke(self.spawn_fly, delay=1.0)

    def get_current_fly_speed(self):
        """Calculate enemy speed"""
        score = self.game_state.score
        if score >= FLY_SPEED_MAX_SCORE:
            return MAX_FLY_SPEED
        if score < FLY_SPEED_START_SCORE:
            return MIN_FLY_SPEED
        t = (score - FLY_SPEED_START_SCORE) / (
            FLY_SPEED_MAX_SCORE - FLY_SPEED_START_SCORE
        )
        return lerp(MIN_FLY_SPEED, MAX_FLY_SPEED, t)

    def get_current_boss_speed(self):
        """Calculate boss speed"""
        score = self.game_state.score
        if score >= FLY_SPEED_MAX_SCORE:
            return MAX_BOSS_SPEED
        if score < FLY_SPEED_START_SCORE:
            return MIN_BOSS_SPEED
        t = (score - FLY_SPEED_START_SCORE) / (
            FLY_SPEED_MAX_SCORE - FLY_SPEED_START_SCORE
        )
        return lerp(MIN_BOSS_SPEED, MAX_BOSS_SPEED, t)

    def update_enemies(self, player, ui_manager):
        """Update all enemies each frame"""
        fly_speed = self.get_current_fly_speed()
        boss_speed = self.get_current_boss_speed()

        for fly in self.flies[:]:
            speed = boss_speed if fly.is_boss else fly_speed
            fly.x -= speed * time.dt

            # Enemy collides with player
            if fly.intersects(player).hit:
                ui_manager.show_explosion(fly.position)

                damage = BOSS_DAMAGE if fly.is_boss else 1

                if fly.is_boss:
                    self.audio_manager.play_sound("boss_die")
                    self.handle_boss_defeat()
                else:
                    self.audio_manager.play_sound("enemy_kill")

                self.flies.remove(fly)
                destroy(fly)

                self.game_state.health -= damage
                ui_manager.update_hearts(self.game_state.health)
                ui_manager.flash_damage()
                self.audio_manager.play_sound("player_damage")
                player.shake()

                if self.game_state.health <= 0 and self.game_over_callback:
                    self.game_over_callback()

            # Enemy escapes off-screen
            elif fly.x < -12:
                damage = BOSS_DAMAGE if fly.is_boss else 1

                if fly.is_boss:
                    self.handle_boss_escape()

                self.flies.remove(fly)
                destroy(fly)

                self.game_state.health -= damage
                ui_manager.update_hearts(self.game_state.health)
                ui_manager.flash_damage()
                self.audio_manager.play_sound("player_damage")

                if self.game_state.health <= 0 and self.game_over_callback:
                    self.game_over_callback()