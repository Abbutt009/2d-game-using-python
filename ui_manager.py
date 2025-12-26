from ursina import *
from config import INITIAL_HEALTH


class UIManager:
    def __init__(self, game_state):
        self.game_state = game_state
        
        # Explosion animation
        self.boom = Animation(
            "assets/boom",
            model="quad",
            scale=3,
            x=100,
            y=100,
            visible=False,
            loop=False,
            autoplay=False,
            duration=0.2,
        )

        # Score displays
        self.score_label = Text(
            text="Score: 0",
            position=(0.65, 0.45),
            origin=(0, 0),
            scale=2,
            color=color.black,
            enabled=False,
        )

        self.high_score_label = Text(
            text="Best: 0",
            position=(0.65, 0.40),
            origin=(0, 0),
            scale=2,
            color=color.dark_gray,
            enabled=False,
        )

        # Boss health
        self.boss_health_text = Text(
            parent=camera.ui,
            text="BOSS HP: 20",
            position=(0, 0.45),
            origin=(0, 0),
            scale=2.5,
            color=color.red,
            enabled=False,
            z=7,
        )

        # Health hearts
        self.hearts = []
        for i in range(INITIAL_HEALTH):
            heart = Entity(
                parent=camera.ui,
                model="quad",
                texture="assets/heart",
                scale=0.04,
                position=(-0.85 + (i * 0.045), 0.42),
                enabled=False,
                color=color.red,
            )
            self.hearts.append(heart)

        # Damage flash
        self.damage_flash = Entity(
            parent=camera.ui,
            model="quad",
            scale=(2, 2),
            color=color.rgba(255, 0, 0, 0),
            z=5,
            enabled=True,
        )

        # Pause menu
        self.pause_screen = Entity(parent=camera.ui, enabled=False, z=8)
        Entity(parent=self.pause_screen, model="quad", scale=(2, 2), 
               color=color.black33, z=9)
        Text(
            parent=self.pause_screen,
            text="PAUSED\n\nPress P to Resume\nPress Q to Quit",
            scale=2,
            y=0,
            color=color.yellow,
            origin=(0, 0),
            z=10,
        )

        # Game over screen
        self.gameover_screen = Entity(parent=camera.ui, enabled=False, z=5)
        Entity(parent=self.gameover_screen, model="quad", scale=(2, 2), 
               color=color.black33, z=0)
        Text(
            parent=self.gameover_screen,
            text="GAME OVER",
            scale=2,
            y=0.25,
            x=0,
            color=color.red,
            origin=(0, 0),
            z=1,
        )
        self.final_score_label = Text(
            parent=self.gameover_screen,
            text=f"Score: 0",
            scale=1.5,
            x=-0.2,
            y=0.05,
            color=color.white,
            origin=(0, 0),
            z=1,
        )
        self.high_score_display = Text(
            parent=self.gameover_screen,
            text=f"Best: 0",
            scale=1.5,
            x=0.2,
            y=0.05,
            color=color.yellow,
            origin=(0, 0),
            z=1,
        )
        self.restart_button = Button(
            parent=self.gameover_screen,
            text="RESTART",
            color=color.green,
            scale=(0.25, 0.08),
            x=-0.14,
            y=-0.15,
            z=1,
        )
        self.quit_button = Button(
            parent=self.gameover_screen,
            text="EXIT",
            color=color.red,
            scale=(0.25, 0.08),
            x=0.14,
            y=-0.15,
            z=1,
            on_click=application.quit,
        )

        # Controls screen
        self.controls_screen = Entity(parent=camera.ui, enabled=True, z=9)
        Entity(parent=self.controls_screen, model="quad", scale=(1, 0.7), 
               color=color.black66, z=10)
        Text(
            parent=self.controls_screen,
            text="PLAYER CONTROLS",
            scale=0.1,
            y=0.35,
            color=color.yellow,
            origin=(0, 0),
            z=11,
        )
        Text(
            parent=self.controls_screen,
            text=(
                "MOVEMENT:\n"
                " W or UP ARROW: Fly Up\n"
                " S or DOWN ARROW: Fly Down\n\n"
                "WEAPONRY:\n"
                " ENTER or SPACE: Fire Bullet\n\n"
                "GAMEPLAY:\n"
                " P: Pause/Unpause\n"
                " Q or ESCAPE: Quit Game\n\n"
                "Press START or SPACE/ENTER to Begin..."
            ),
            scale=1.5,
            y=0,
            x=-0.5,
            origin=(-0.5, 0),
            font="VeraMono.ttf",
            line_height=1.2,
            color=color.black,
            z=11,
        )
        self.start_button = Button(
            parent=self.controls_screen,
            text="START (Begin Game)",
            color=color.green,
            scale=(0.35, 0.08),
            y=-0.3,
            z=11,
        )

    def update_hearts(self, health):
        """Show/hide hearts based on health"""
        for i, heart in enumerate(self.hearts):
            if i < health:
                heart.color = color.red
                heart.enabled = True
            else:
                heart.enabled = False

    def flash_damage(self):
        """Red flash + camera shake"""
        self.damage_flash.color = color.rgba(255, 0, 0, 120)
        self.damage_flash.animate(
            "color", color.rgba(255, 0, 0, 0), duration=0.1, curve=curve.out_quad
        )
        camera.shake(duration=0.2, magnitude=1.5)

    def show_explosion(self, position):
        """Show explosion at position"""
        self.boom.position = position
        self.boom.visible = True
        self.boom.start()
        invoke(setattr, self.boom, "visible", False, delay=self.boom.duration)

    def start_game(self, game_state):
        """Show game UI"""
        self.gameover_screen.enabled = False
        self.controls_screen.enabled = False
        self.pause_screen.enabled = False
        self.boss_health_text.enabled = False
        self.score_label.enabled = True
        self.high_score_label.enabled = True
        self.high_score_label.text = f"Best: {game_state.high_score}"
        self.score_label.text = f"Score: {game_state.score}"
        self.update_hearts(game_state.health)

    def show_game_over(self, game_state):
        """Show game over screen"""
        self.score_label.enabled = False
        self.high_score_label.enabled = False
        self.pause_screen.enabled = False
        self.controls_screen.enabled = False
        self.boss_health_text.enabled = False

        for heart in self.hearts:
            heart.enabled = False

        game_state.save_high_score()
        self.final_score_label.text = f"Score: {game_state.score}"
        self.high_score_display.text = f"Best: {game_state.high_score}"
        self.gameover_screen.enabled = True