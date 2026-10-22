import array
import math
import random
import pygame
from game.color_button import ColorButton

# One pitch per pad: Red=C4, Blue=E4, Green=G4, Yellow=C5 (a C major arpeggio)
PAD_FREQUENCIES = [261.63, 329.63, 392.00, 523.25]
SAMPLE_RATE = 44100


def make_tone(freq, duration_ms=250, volume=0.4):
    """Build a sine-wave pygame Sound with a short fade in/out to avoid clicks."""
    total = int(SAMPLE_RATE * duration_ms / 1000)
    fade = int(SAMPLE_RATE * 0.01)
    samples = array.array("h")
    for i in range(total):
        envelope = min(1.0, i / fade, (total - i) / fade)
        value = int(32767 * volume * envelope * math.sin(2 * math.pi * freq * i / SAMPLE_RATE))
        samples.append(value)
    return pygame.mixer.Sound(buffer=samples.tobytes())


class GameEngine:
    # Playback speed settings (milliseconds)
    BASE_FLASH = 450
    BASE_PAUSE = 200
    MIN_FLASH = 150
    MIN_PAUSE = 60
    FLASH_STEP = 30   # flash gets this much shorter each round
    PAUSE_STEP = 14   # pause gets this much shorter each round

    # Player turn timer (milliseconds). The clock restarts after every correct click.
    BASE_TURN_TIME = 5000
    MIN_TURN_TIME = 2500
    TURN_TIME_STEP = 100  # less time per click as rounds advance

    def __init__(self, width, height):
        self.width = width
        self.height = height

        pad_size = 130
        gap = 24
        start_x = width // 2 - pad_size - (gap // 2)
        start_y = 150

        self.buttons = [
            ColorButton(0, pygame.Rect(start_x, start_y, pad_size, pad_size), (110, 20, 20), (255, 50, 50)),                      # Red
            ColorButton(1, pygame.Rect(start_x + pad_size + gap, start_y, pad_size, pad_size), (15, 60, 150), (40, 170, 255)),   # Blue
            ColorButton(2, pygame.Rect(start_x, start_y + pad_size + gap, pad_size, pad_size), (15, 100, 30), (50, 255, 90)),    # Green
            ColorButton(3, pygame.Rect(start_x + pad_size + gap, start_y + pad_size + gap, pad_size, pad_size), (140, 110, 10), (255, 235, 40)), # Yellow
        ]

        self.sequence = []
        self.player_input = []
        self.score = 0

        self.state = "WATCH"
        self.showing_step = 0
        self.step_start_time = 0
        self.flash_duration = self.BASE_FLASH
        self.pause_duration = self.BASE_PAUSE
        self.is_flashing = False

        self.player_lit_button = None
        self.player_lit_start = 0
        self.player_flash_duration = 150

        self.turn_start_time = 0
        self.turn_time_limit = self.BASE_TURN_TIME
        self.game_over_reason = ""

        self.font_title = pygame.font.SysFont(None, 40)
        self.font_medium = pygame.font.SysFont(None, 28)

        self.sounds = self.load_sounds()

        self.start_next_round()

    def load_sounds(self):
        """Create one tone per pad. Returns an empty list if audio is unavailable."""
        try:
            # Mono, 16-bit so the generated samples match the mixer format
            pygame.mixer.quit()
            pygame.mixer.init(SAMPLE_RATE, -16, 1, 512)
            return [make_tone(f) for f in PAD_FREQUENCIES]
        except pygame.error:
            return []

    def play_sound(self, color_id):
        if self.sounds:
            self.sounds[color_id].play()

    def light_button(self, color_id):
        """Light a pad and play its tone (used for both playback and clicks)."""
        self.buttons[color_id].is_lit = True
        self.play_sound(color_id)

    def start_next_round(self):
        new_color = random.randint(0, 3)

        self.sequence.append(new_color)

        # Speed up playback as rounds advance (never faster than the minimums)
        round_num = len(self.sequence)
        self.flash_duration = max(self.MIN_FLASH, self.BASE_FLASH - (round_num - 1) * self.FLASH_STEP)
        self.pause_duration = max(self.MIN_PAUSE, self.BASE_PAUSE - (round_num - 1) * self.PAUSE_STEP)

        self.player_input.clear()
        self.state = "WATCH"
        self.showing_step = 0
        self.step_start_time = pygame.time.get_ticks()
        self.is_flashing = True
        self.light_button(self.sequence[0])

    def update(self):
        now = pygame.time.get_ticks()

        if self.player_lit_button is not None:
            if now - self.player_lit_start >= self.player_flash_duration:
                self.player_lit_button.is_lit = False
                self.player_lit_button = None

        if self.state == "WATCH":
            current_btn_id = self.sequence[self.showing_step]

            if self.is_flashing:
                if now - self.step_start_time >= self.flash_duration:
                    self.buttons[current_btn_id].is_lit = False
                    self.is_flashing = False
                    self.step_start_time = now
            else:
                if now - self.step_start_time >= self.pause_duration:
                    self.showing_step += 1
                    if self.showing_step < len(self.sequence):
                        next_id = self.sequence[self.showing_step]
                        self.light_button(next_id)
                        self.is_flashing = True
                        self.step_start_time = now
                    else:
                        self.state = "PLAYER_TURN"
                        self.turn_time_limit = max(
                            self.MIN_TURN_TIME,
                            self.BASE_TURN_TIME - (len(self.sequence) - 1) * self.TURN_TIME_STEP,
                        )
                        self.turn_start_time = now

        elif self.state == "PLAYER_TURN":
            if now - self.turn_start_time >= self.turn_time_limit:
                self.game_over_reason = "TIME'S UP! GAME OVER"
                self.state = "GAME_OVER"

    def handle_event(self, event):
        if self.state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        if self.state == "PLAYER_TURN" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn.contains(event.pos):
                    self.light_button(btn.color_id)
                    self.player_lit_button = btn
                    self.player_lit_start = pygame.time.get_ticks()

                    self.register_player_click(btn.color_id)
                    break

    def register_player_click(self, color_id):
        self.player_input.append(color_id)
        current_idx = len(self.player_input) - 1

        if self.player_input[current_idx] != self.sequence[current_idx]:
            self.game_over_reason = "WRONG PATTERN! GAME OVER"
            self.state = "GAME_OVER"
            return

        if len(self.player_input) == len(self.sequence):
            self.score += 1
            self.start_next_round()
        else:
            # Correct click, pattern not finished yet: restart the countdown
            self.turn_start_time = pygame.time.get_ticks()

    def reset(self):
        self.sequence.clear()
        self.player_input.clear()
        self.score = 0
        for btn in self.buttons:
            btn.is_lit = False
        self.player_lit_button = None
        self.start_next_round()

    def render_timer_bar(self, screen):
        bar_width = 300
        bar_height = 16
        bar_x = self.width // 2 - bar_width // 2
        bar_y = 460

        elapsed = pygame.time.get_ticks() - self.turn_start_time
        remaining = max(0.0, 1.0 - elapsed / self.turn_time_limit)

        # Green -> yellow -> red as time runs out
        if remaining > 0.5:
            color = (80, 240, 130)
        elif remaining > 0.25:
            color = (255, 220, 80)
        else:
            color = (240, 70, 70)

        pygame.draw.rect(screen, (50, 54, 64), (bar_x, bar_y, bar_width, bar_height), border_radius=8)
        if remaining > 0:
            pygame.draw.rect(screen, color, (bar_x, bar_y, int(bar_width * remaining), bar_height), border_radius=8)
        pygame.draw.rect(screen, (70, 75, 85), (bar_x, bar_y, bar_width, bar_height), width=2, border_radius=8)

    def render(self, screen):
        screen.fill((22, 24, 30))

        title_surf = self.font_title.render("Memory Pattern Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 20))

        score_surf = self.font_medium.render(f"Score: {self.score}", True, (255, 220, 80))
        screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, 60))

        status_text = "Watch the pattern..." if self.state == "WATCH" else "Your turn: Click the pattern!"
        status_color = (190, 195, 205) if self.state == "WATCH" else (80, 240, 130)
        status_surf = self.font_medium.render(status_text, True, status_color)
        screen.blit(status_surf, (self.width // 2 - status_surf.get_width() // 2, 95))

        for btn in self.buttons:
            btn.render(screen)

        if self.state == "PLAYER_TURN":
            self.render_timer_bar(screen)

        if self.state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))

            over_surf = self.font_title.render(self.game_over_reason or "GAME OVER", True, (240, 70, 70))
            screen.blit(over_surf, (self.width // 2 - over_surf.get_width() // 2, self.height // 2 - 40))

            final_score_surf = self.font_medium.render(f"Final Score: {self.score}", True, (255, 255, 255))
            screen.blit(final_score_surf, (self.width // 2 - final_score_surf.get_width() // 2, self.height // 2 + 10))

            restart_surf = self.font_medium.render("Press [R] to Play Again", True, (200, 200, 200))
            screen.blit(restart_surf, (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 50))
