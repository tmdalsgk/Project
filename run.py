"""
Pygame presentation layer for Minesweeper.

This module owns:
- Renderer: all drawing of cells, header, and result overlays
- InputController: translate mouse input to board actions and UI feedback
- Game: orchestration of loop, timing, state transitions, and composition

The logic lives in components.Board; this module should not implement rules.
"""

import sys
import random  #추가 
import os  #추가
import pygame

import config
from components import Board
from pygame.locals import Rect


class Renderer:
    """Draws the Minesweeper UI.

    Knows how to draw individual cells with flags/numbers, header info,
    and end-of-game overlays with a semi-transparent background.
    """

    def __init__(self, screen: pygame.Surface, board: Board):
        self.screen = screen
        self.board = board
        self.font = pygame.font.Font(config.font_name, config.font_size)
        self.header_font = pygame.font.Font(config.font_name, config.header_font_size)
        self.result_font = pygame.font.Font(config.font_name, config.result_font_size)

    def cell_rect(self, col: int, row: int) -> Rect:
        """Return the rectangle in pixels for the given grid cell."""
        x = config.margin_left + col * config.cell_size
        y = config.margin_top + row * config.cell_size
        return Rect(x, y, config.cell_size, config.cell_size)

    def draw_cell(self, col: int, row: int, highlighted: bool) -> None:
        """Draw a single cell, respecting revealed/flagged state and highlight."""
        cell = self.board.cells[self.board.index(col, row)]
        rect = self.cell_rect(col, row)
        if cell.state.is_revealed:
            pygame.draw.rect(self.screen, config.color_cell_revealed, rect)
            if cell.state.is_mine:
                pygame.draw.circle(self.screen, config.color_cell_mine, rect.center, rect.width // 4)
            elif cell.state.adjacent > 0:
                color = config.number_colors.get(cell.state.adjacent, config.color_text)
                label = self.font.render(str(cell.state.adjacent), True, color)
                label_rect = label.get_rect(center=rect.center)
                self.screen.blit(label, label_rect)
        else:
            base_color = config.color_highlight if highlighted else config.color_cell_hidden
            pygame.draw.rect(self.screen, base_color, rect)
            if cell.state.is_flagged:
                flag_w = max(6, rect.width // 3)
                flag_h = max(8, rect.height // 2)
                pole_x = rect.left + rect.width // 3
                pole_y = rect.top + 4
                pygame.draw.line(self.screen, config.color_flag, (pole_x, pole_y), (pole_x, pole_y + flag_h), 2)
                pygame.draw.polygon(
                    self.screen,
                    config.color_flag,
                    [
                        (pole_x + 2, pole_y),
                        (pole_x + 2 + flag_w, pole_y + flag_h // 3),
                        (pole_x + 2, pole_y + flag_h // 2),
                    ],
                )
        pygame.draw.rect(self.screen, config.color_grid, rect, 1)

    def draw_header(self, remaining_mines: int, time_text: str) -> None:
        """Draw the header bar containing remaining mines and elapsed time."""
        pygame.draw.rect(
            self.screen,
            config.color_header,
            Rect(0, 0, config.width, config.margin_top - 4),
        )
        left_text = f"Mines: {remaining_mines}"
        right_text = f"Time: {time_text}"
        left_label = self.header_font.render(left_text, True, config.color_header_text)
        right_label = self.header_font.render(right_text, True, config.color_header_text)
        self.screen.blit(left_label, (10, 12))
        self.screen.blit(right_label, (config.width - right_label.get_width() - 10, 12))

    def draw_result_overlay(self, text: str | None) -> None:
        """Draw a semi-transparent overlay with centered result text, if any."""
        if not text:
            return
        overlay = pygame.Surface((config.width, config.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, config.result_overlay_alpha))
        self.screen.blit(overlay, (0, 0))

        # 줄바꿈 기준으로 텍스트 나누기
        lines = text.split('\n')
        line_surfaces = []
        total_height = 0

        for line in lines:
            surf = self.result_font.render(line, True, config.color_result)
            line_surfaces.append(surf)
            # 전체 문구의 높이를 계산
            total_height += surf.get_height() + 10

        # 여러 줄을 중앙에 순서대로 배치
        start_y = (config.height - total_height) // 2
        for surf in line_surfaces:
            rect = surf.get_rect(center=(config.width // 2, start_y + surf.get_height() // 2))
            self.screen.blit(surf, rect)
            start_y += surf.get_height() + 10


class InputController:
    """Translates input events into game and board actions."""

    def __init__(self, game: "Game"):
        self.game = game

    def pos_to_grid(self, x: int, y: int):
        """Convert pixel coordinates to (col,row) grid indices or (-1,-1) if out of bounds."""
        if not (config.margin_left <= x < config.width - config.margin_right):
            return -1, -1
        if not (config.margin_top <= y < config.height - config.margin_bottom):
            return -1, -1
        col = (x - config.margin_left) // config.cell_size
        row = (y - config.margin_top) // config.cell_size
        if 0 <= col < self.game.board.cols and 0 <= row < self.game.board.rows:
            return int(col), int(row)
        return -1, -1

    def handle_mouse(self, pos, button) -> None:
        col, row = self.pos_to_grid(pos[0], pos[1])
        if col == -1:
            return

        game = self.game

        # LEFT CLICK = reveal
        if button == config.mouse_left:
            game.highlight_targets.clear()

            if not game.started:
                game.started = True
                game.start_ticks_ms = pygame.time.get_ticks()

            if not game.board.game_over and not game.board.win:
                game.board.reveal(col, row)

        # RIGHT CLICK = toggle flag
        elif button == config.mouse_right:
            game.highlight_targets.clear()
            if not game.board.game_over and not game.board.win:
                game.board.toggle_flag(col, row)

        # MIDDLE CLICK = highlight neighbors
        elif button == config.mouse_middle:
            neighbors = game.board.neighbors(col, row)
            game.highlight_targets = {
                (nc, nr)
                for (nc, nr) in neighbors
                if not game.board.cells[game.board.index(nc, nr)].state.is_revealed
            }
            game.highlight_until_ms = pygame.time.get_ticks() + config.highlight_duration_ms

class Game:
    """Main application object orchestrating loop and high-level state."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(config.title)
        self.screen = pygame.display.set_mode(config.display_dimension)
        self.clock = pygame.time.Clock()
        self.board = Board(config.cols, config.rows, config.num_mines)
        self.renderer = Renderer(self.screen, self.board)
        self.input = InputController(self)
        self.highlight_targets = set()
        self.highlight_until_ms = 0
        self.started = False
        self.start_ticks_ms = 0
        self.end_ticks_ms = 0
        # 게임 시작 시 기존 최고 기록 로드
        self.high_score = self.load_high_score()

    def load_high_score(self) -> float:
        """파일에서 최고 기록(초)을 불러옴"""
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r") as f:
                try:
                    return float(f.read())
                except:
                    return float('inf')
        return float('inf')

    def save_high_score(self, score: float):
        """새로운 최고 기록을 파일에 저장"""
        with open("highscore.txt", "w") as f:
            f.write(f"{score:.2f}")
        self.high_score = score

    def change_difficulty(self, level: str):
        """난이도에 따라 설정을 변경하고 게임을 리셋"""
        if level == 'easy':
            config.cols, config.rows, config.num_mines = 10, 10, 10
        elif level == 'medium':
            config.cols, config.rows, config.num_mines = 16, 16, 40
        elif level == 'hard':
            config.cols, config.rows, config.num_mines = 30, 20, 99

        # 화면 크기 재계산 및 재설정
        config.width = config.margin_left + config.cols * config.cell_size + config.margin_right
        config.height = config.margin_top + config.rows * config.cell_size + config.margin_bottom
        config.display_dimension = (config.width, config.height)
        
        self.screen = pygame.display.set_mode(config.display_dimension)
        self.reset()

    def give_hint(self):
        """지뢰가 없고 아직 열리지 않은 칸 중 하나를 임의로 확인"""
        if self.board.game_over or self.board.win:
            return

        # 아직 열리지 않았고 지뢰가 아닌 칸들의 좌표 리스트 생성
        unrevealed_safe_cells = [
            (c, r) for r in range(self.board.rows)
            for c in range(self.board.cols)
            if not self.board.cells[self.board.index(c, r)].state.is_revealed 
            and not self.board.cells[self.board.index(c, r)].state.is_mine
        ]

        if unrevealed_safe_cells:
            # 리스트에서 무작위로 하나 선택
            c, r = random.choice(unrevealed_safe_cells)
            
            # 게임이 아직 시작 전이라면 시작 처리
            if not self.started:
                self.started = True
                self.start_ticks_ms = pygame.time.get_ticks()
            
            # 해당 칸 오픈
            self.board.reveal(c, r)

    def reset(self):
        """Reset the game state and start a new board."""
        self.board = Board(config.cols, config.rows, config.num_mines)
        self.renderer.board = self.board
        self.highlight_targets.clear()
        self.highlight_until_ms = 0
        self.started = False
        self.start_ticks_ms = 0
        self.end_ticks_ms = 0

    def _elapsed_ms(self) -> int:
        """Return elapsed time in milliseconds (stops when game ends)."""
        if not self.started:
            return 0
        if self.end_ticks_ms:
            return self.end_ticks_ms - self.start_ticks_ms
        return pygame.time.get_ticks() - self.start_ticks_ms

    def _format_time(self, ms: int) -> str:
        """밀리초를 소수점 둘째 자리까지의 초(s) 단위 문자열로 변환"""
        seconds = ms / 1000.0
        return f"{seconds:.2f}s"

    def _result_text(self) -> str | None:
        """결과 레이블에 하이 스코어 정보를 포함하여 반환"""
        if self.board.game_over:
            return "GAME OVER"
        if self.board.win:
            current_time = self._elapsed_ms() / 1000.0  # 초 단위로 변환
            
            # 신기록 달성 여부 확인
            if current_time < self.high_score:
                self.save_high_score(current_time)
                return f"NEW RECORD!\n{current_time:.2f}s"
            else:
                return f"GAME CLEAR!\nBEST: {self.high_score:.2f}s"
        return None

    def draw(self):
        """Render one frame: header, grid, result overlay."""
        if pygame.time.get_ticks() > self.highlight_until_ms and self.highlight_targets:
            self.highlight_targets.clear()
        self.screen.fill(config.color_bg)
        remaining = max(0, config.num_mines - self.board.flagged_count())
        time_text = self._format_time(self._elapsed_ms())
        self.renderer.draw_header(remaining, time_text)
        now = pygame.time.get_ticks()
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                highlighted = (now <= self.highlight_until_ms) and ((c, r) in self.highlight_targets)
                self.renderer.draw_cell(c, r, highlighted)
        self.renderer.draw_result_overlay(self._result_text())
        pygame.display.flip()

    def run_step(self) -> bool:
        """Process inputs, update time, draw, and tick the clock once."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset()
                # 난이도 조절 키 추가
                elif event.key == pygame.K_1:
                    self.change_difficulty('easy')
                elif event.key == pygame.K_2:
                    self.change_difficulty('medium')
                elif event.key == pygame.K_3:
                    self.change_difficulty('hard')
                # 힌트 키(H) 추가
                elif event.key == pygame.K_h:
                    self.give_hint()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.input.handle_mouse(event.pos, event.button)
        if (self.board.game_over or self.board.win) and self.started and not self.end_ticks_ms:
            self.end_ticks_ms = pygame.time.get_ticks()
        self.draw()
        self.clock.tick(config.fps)
        return True


def main() -> int:
    """Application entrypoint: run the main loop until quit."""
    game = Game()
    running = True
    while running:
        running = game.run_step()
    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())