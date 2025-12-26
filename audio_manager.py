from ursina import Audio

class AudioManager:
    def __init__(self):
        self.audio_cache = {}
        self.boss_music = None
        self.bg_music = None

    def preload_audio(self):
        """Pre-load all audio files"""
        sounds = {
            "enemy_damage": "Enemy_damage.mp3",
            "enemy_kill": "Enemy_kill.wav",
            "gameover": "gameover.mp3",
            "shoot": "Laser_shoot.wav",
            "boss_die": "Boss_die.wav",
            "player_damage": "Enemy_damage.mp3",
        }

        for name, file in sounds.items():
            try:
                self.audio_cache[name] = Audio(
                    f"assets/{file}", autoplay=False, loop=False
                )
            except:
                print(f"Warning: {file} not found")

        try:
            self.bg_music = Audio(
                "assets/Background_music.mp3", loop=True, autoplay=False, volume=1.5
            )
        except:
            self.bg_music = None
            print("Warning: Background_music.mp3 not found")

        try:
            self.boss_music = Audio(
                "assets/Boss_entry.mp3", loop=True, autoplay=False, volume=0.5
            )
        except:
            self.boss_music = None
            print("Warning: Boss_entry.mp3 not found")

    def play_sound(self, name):
        """Play a pre-loaded sound effect"""
        if name in self.audio_cache:
            try:
                self.audio_cache[name].play()
            except:
                pass

    def start_boss_music(self):
        """Stop background music and start boss music"""
        if self.bg_music and hasattr(self.bg_music, "stop"):
            self.bg_music.stop()
        if self.boss_music and hasattr(self.boss_music, "play"):
            self.boss_music.play()

    def stop_boss_music(self):
        """Stop boss music and restart background music"""
        if self.boss_music and hasattr(self.boss_music, "stop"):
            self.boss_music.stop()
        if self.bg_music and hasattr(self.bg_music, "play"):
            self.bg_music.play()

    def start_bg_music(self):
        """Start background music"""
        if self.bg_music and hasattr(self.bg_music, "play"):
            self.bg_music.play()

    def stop_all_music(self):
        """Stop all music"""
        if self.bg_music and hasattr(self.bg_music, "stop"):
            self.bg_music.stop()
        if self.boss_music and hasattr(self.boss_music, "stop"):
            self.boss_music.stop()

    def pause_all(self):
        """Pause all music"""
        if self.bg_music and hasattr(self.bg_music, "pause"):
            self.bg_music.pause()
        if self.boss_music and hasattr(self.boss_music, "pause"):
            self.boss_music.pause()

    def resume_all(self, is_boss_fight):
        """Resume appropriate music"""
        if is_boss_fight and self.boss_music and hasattr(self.boss_music, "play"):
            self.boss_music.play()
        elif self.bg_music and hasattr(self.bg_music, "play"):
            self.bg_music.play()