from ursina import *
from config import *
from game_state import *
from audio_manager import *
from ui_manager import *
from entities import *
from enemy_spawner import *
 
app = Ursina(title="shooting game")

window.vsync = True
window.fullscreen = True

# Initialize managers
game_state = GameState()
audio_manager = AudioManager()
ui_manager = UIManager(game_state)
enemy_spawner = EnemySpawner(game_state, audio_manager, ui_manager)

# Background
Entity(model="quad", texture="assets/BG", scale=36, z=1)

# Player
player = Player()

Sky()
camera.orthographic = True
camera.fov = 20


def update():
    """Main game loop"""
    if game_state.state != "playing":
        return

    # Player movement
    up = held_keys["w"] or held_keys["up arrow"]
    down = held_keys["s"] or held_keys["down arrow"]
    player.y += up * 10 * time.dt
    player.y -= down * 10 * time.dt
    player.y = clamp(player.y, MIN_Y, MAX_Y)
    player.rotation_z = -20 if up else (20 if down else 0)

    # Update enemies
    enemy_spawner.update_enemies(player, ui_manager)


def input(key):
    """Handle keyboard input"""
    if key == "q" or key == "escape":
        application.quit()

    # Pause toggle
    if key == "p":
        if game_state.state == "playing":
            game_state.state = "paused"
            ui_manager.pause_screen.enabled = True
            enemy_spawner.pause_spawning()
            audio_manager.pause_all()
        elif game_state.state == "paused":
            game_state.state = "playing"
            ui_manager.pause_screen.enabled = False
            enemy_spawner.resume_spawning()
            audio_manager.resume_all(game_state.has_boss_spawned)
        return

    # Restart
    if game_state.state == "game_over" and key == "r":
        start_game()
        return

    # Shoot / Start
    if key == "enter" or key == "space":
        if game_state.state == "paused_controls":
            start_game()
            return
        if game_state.state == "playing":
            audio_manager.play_sound("shoot")
            Bullet(y=player.y, x=player.x + 2, game_state=game_state, 
                   audio_manager=audio_manager, enemy_spawner=enemy_spawner, 
                   ui_manager=ui_manager)


def start_game():
    """Start new game"""
    game_state.reset()
    enemy_spawner.reset()
    ui_manager.start_game(game_state)
    player.y = 5
    player.enabled = True
    audio_manager.start_bg_music()
    invoke(enemy_spawner.spawn_fly, delay=1.5)


def game_over():
    """Handle game over"""
    game_state.state = "game_over"
    enemy_spawner.stop_spawning()
    audio_manager.stop_all_music()
    audio_manager.play_sound("gameover")
    player.enabled = False
    ui_manager.show_game_over(game_state)
    enemy_spawner.hide_all_enemies()


# Setup callbacks
ui_manager.start_button.on_click = start_game
ui_manager.restart_button.on_click = start_game
enemy_spawner.game_over_callback = game_over

# Initialize
audio_manager.preload_audio()
game_state.load_high_score()
ui_manager.high_score_label.text = f"Best: {game_state.high_score}"

app.run()