import random
import pygame
from game.text_box import TextBox


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.score = 0
        self.total_attempts = 0

        # Streak system
        self.streak = 0
        self.streak_multiplier = 1

        self.feedback_msg = "Solve the card and press Enter!"
        self.feedback_color = (200, 205, 215)

        # Timer system
        self.time_limit = 10
        self.time_remaining = self.time_limit
        self.timer_start = pygame.time.get_ticks()

        self.num_a = 0
        self.num_b = 0
        self.operator = "+"

        box_w, box_h = 130, 44
        self.input_box = TextBox(width // 2 - 110, 230, box_w, box_h)
        self.submit_btn = pygame.Rect(width // 2 + 30, 230, 90, box_h)

        self.font_title = pygame.font.SysFont(None, 38)
        self.font_hud = pygame.font.SysFont(None, 26)
        self.font_card = pygame.font.SysFont(None, 56)
        self.font_btn = pygame.font.SysFont(None, 24)

        self.generate_new_card()

    def generate_new_card(self):
        self.operator = random.choice(["+", "-", "*", "/"])

        if self.operator == "/":
            # Generate a clean integer division problem.
            # Example: 4 * 3 = 12, so the question becomes 12 / 3 = 4.
            divisor = random.randint(2, 12)
            quotient = random.randint(2, 10)

            self.num_b = divisor
            self.num_a = divisor * quotient

        else:
            self.num_a = random.randint(3, 15)
            self.num_b = random.randint(2, 12)

            if self.operator == "-" and self.num_a < self.num_b:
                self.num_a, self.num_b = self.num_b, self.num_a

        self.input_box.clear()

        # Reset timer for new question
        self.time_remaining = self.time_limit
        self.timer_start = pygame.time.get_ticks()

    def compute_expected_answer(self):
        if self.operator == "+":
            return self.num_a + self.num_b
        elif self.operator == "-":
            return self.num_a - self.num_b
        elif self.operator == "*":
            return self.num_a * self.num_b
        elif self.operator == "/":
            return self.num_a // self.num_b

    def submit_answer(self):
        val_str = self.input_box.text.strip()

        if not val_str or val_str == "-":
            self.feedback_msg = "Type an answer first!"
            self.feedback_color = (240, 175, 40)
            return

        user_answer = int(val_str)
        expected = self.compute_expected_answer()
        self.total_attempts += 1

        if user_answer == expected:
            # Increase consecutive correct streak
            self.streak += 1

            # Maximum multiplier is 3x
            self.streak_multiplier = min(self.streak, 3)

            # Add points according to multiplier
            self.score += self.streak_multiplier

            self.feedback_msg = (
                f"CORRECT! +{self.streak_multiplier} "
                f"({self.streak} streak)  "
                f"{self.num_a} {self.operator} {self.num_b} = {expected}"
            )

            self.feedback_color = (80, 230, 110)
            self.generate_new_card()

        else:
            # Wrong answer resets the streak
            self.streak = 0
            self.streak_multiplier = 1

            self.feedback_msg = f"WRONG! Expected {expected}."
            self.feedback_color = (240, 75, 75)
            self.input_box.clear()

    def handle_event(self, event):
        self.input_box.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.submit_answer()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit_btn.collidepoint(event.pos):
                self.submit_answer()

    def update(self):
        elapsed = (pygame.time.get_ticks() - self.timer_start) / 1000
        self.time_remaining = max(0, self.time_limit - elapsed)

        if self.time_remaining <= 0:
            self.total_attempts += 1

            # Timeout resets the streak
            self.streak = 0
            self.streak_multiplier = 1

            self.feedback_msg = "TIME UP! Streak reset."
            self.feedback_color = (240, 180, 70)

            self.generate_new_card()

    def render(self, screen):
        screen.fill((25, 29, 37))

        title_surf = self.font_title.render(
            "Math Flashcards Arena",
            True,
            (245, 245, 245)
        )

        screen.blit(
            title_surf,
            (
                self.width // 2 - title_surf.get_width() // 2,
                18
            )
        )

        score_surf = self.font_hud.render(
            f"Score: {self.score} / {self.total_attempts}",
            True,
            (255, 220, 80)
        )

        screen.blit(
            score_surf,
            (
                self.width // 2 - score_surf.get_width() // 2,
                58
            )
        )

        # Display current streak and multiplier
        streak_surf = self.font_hud.render(
            f"Streak: {self.streak}   Multiplier: {self.streak_multiplier}x",
            True,
            (180, 220, 255)
        )

        screen.blit(
            streak_surf,
            (
                self.width // 2 - streak_surf.get_width() // 2,
                78
            )
        )

        card_rect = pygame.Rect(
            self.width // 2 - 130,
            105,
            260,
            110
        )

        pygame.draw.rect(
            screen,
            (240, 242, 245),
            card_rect,
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            (85, 120, 175),
            card_rect,
            width=3,
            border_radius=12
        )

        card_str = f"{self.num_a}  {self.operator}  {self.num_b}"

        card_surf = self.font_card.render(
            card_str,
            True,
            (25, 30, 42)
        )

        screen.blit(
            card_surf,
            (
                card_rect.centerx - card_surf.get_width() // 2,
                card_rect.centery - card_surf.get_height() // 2
            )
        )

        # Timer bar
        timer_rect = pygame.Rect(
            self.width // 2 - 130,
            222,
            260,
            10
        )

        pygame.draw.rect(
            screen,
            (65, 70, 80),
            timer_rect,
            border_radius=5
        )

        timer_width = int(
            timer_rect.width *
            (self.time_remaining / self.time_limit)
        )

        if timer_width > 0:
            pygame.draw.rect(
                screen,
                (80, 200, 110),
                pygame.Rect(
                    timer_rect.x,
                    timer_rect.y,
                    timer_width,
                    timer_rect.height
                ),
                border_radius=5
            )

        timer_text = self.font_btn.render(
            f"Time: {self.time_remaining:.1f}s",
            True,
            (220, 225, 230)
        )

        screen.blit(
            timer_text,
            (
                self.width // 2 - timer_text.get_width() // 2,
                340
            )
        )

        self.input_box.render(screen)

        pygame.draw.rect(
            screen,
            (45, 140, 80),
            self.submit_btn,
            border_radius=6
        )

        pygame.draw.rect(
            screen,
            (215, 225, 220),
            self.submit_btn,
            width=2,
            border_radius=6
        )

        btn_txt = self.font_btn.render(
            "SUBMIT",
            True,
            (255, 255, 255)
        )

        screen.blit(
            btn_txt,
            (
                self.submit_btn.centerx - btn_txt.get_width() // 2,
                self.submit_btn.centery - btn_txt.get_height() // 2
            )
        )

        msg_surf = self.font_hud.render(
            self.feedback_msg,
            True,
            self.feedback_color
        )

        screen.blit(
            msg_surf,
            (
                self.width // 2 - msg_surf.get_width() // 2,
                295
            )
        )