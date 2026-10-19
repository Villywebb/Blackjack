"""Nattklöver: fristående blackjack med Tkinter. Kör med python3 ai_blackjack.py."""

from dataclasses import dataclass, field
import random
import math
import tkinter as tk
from tkinter import font as tkfont


SUIT_SYMBOLS = {"spades": "♠", "hearts": "♥", "diamonds": "♦", "clubs": "♣"}
RANK_LABELS = ("", "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")


@dataclass(frozen=True, slots=True)
class Card:
    suit: str
    rank: int

    def __post_init__(self):
        if self.suit not in SUIT_SYMBOLS or type(self.rank) is not int or not 1 <= self.rank <= 13:
            raise ValueError("A card needs a valid suit and a rank from 1 to 13.")

    @property
    def label(self) -> str:
        return f"{RANK_LABELS[self.rank]}{SUIT_SYMBOLS[self.suit]}"


@dataclass
class Hand:
    cards: list[Card] = field(default_factory=list)

    def _score(self) -> tuple[int, bool]:
        low_total = sum(min(card.rank, 10) for card in self.cards)
        soft = any(card.rank == 1 for card in self.cards) and low_total + 10 <= 21
        return low_total + (10 if soft else 0), soft

    @property
    def total(self) -> int:
        return self._score()[0]

    @property
    def soft(self) -> bool:
        return self._score()[1]

    @property
    def blackjack(self) -> bool:
        return len(self.cards) == 2 and self.total == 21

    @property
    def busted(self) -> bool:
        return self.total > 21


class Game:
    def __init__(self, bank: int = 1000, bet: int = 50, decks: int = 6):
        if type(bank) is not int or bank < 0:
            raise ValueError("The bankroll must be a nonnegative whole number.")
        if type(decks) is not int or decks < 1:
            raise ValueError("Use at least one deck.")
        self._check_bet(bet)
        self.bank = bank
        self.bet = bet
        self.decks = decks
        self.wager = 0
        self.player = Hand()
        self.dealer = Hand()
        self.phase = "betting"
        self.outcome = ""
        self.profit = 0
        self.rounds = 0
        self.wins = 0
        self.blackjacks = 0
        self.shoe: list[Card] = []
        self._refill_shoe()

    @staticmethod
    def _check_bet(bet: int) -> None:
        if type(bet) is not int or bet <= 0 or bet % 10:
            raise ValueError("Choose a positive bet in multiples of 10.")

    def _require_phase(self, phase: str) -> None:
        if self.phase != phase:
            raise ValueError("That action is not available right now.")

    def _refill_shoe(self) -> None:
        self.shoe = [Card(suit, rank) for _ in range(self.decks)
                     for suit in SUIT_SYMBOLS for rank in range(1, 14)]
        random.shuffle(self.shoe)

    @property
    def ready(self) -> bool:
        return self.phase in ("betting", "done") and self.bank >= 10

    @property
    def can_double(self) -> bool:
        return self.phase == "player" and len(self.player.cards) == 2 and self.bank >= self.bet

    def start_round(self, bet: int | None = None) -> None:
        if self.phase not in ("betting", "done"):
            raise ValueError("Finish the current round before starting another.")
        bet = self.bet if bet is None else bet
        self._check_bet(bet)
        if bet > self.bank:
            raise ValueError("The bet is larger than the available bankroll.")
        if len(self.shoe) < 52:
            self._refill_shoe()
        self.bet = bet
        self.wager = bet
        self.bank -= bet
        self.player = Hand()
        self.dealer = Hand()
        self.outcome = ""
        self.profit = 0
        self.phase = "dealing"

    def draw_to(self, hand: Hand) -> Card:
        if self.phase not in ("dealing", "player", "dealer"):
            raise ValueError("Cards can only be drawn during an active round.")
        if hand is not self.player and hand is not self.dealer:
            raise ValueError("Choose the player or dealer hand for this round.")
        if not self.shoe:
            raise ValueError("The shoe is empty.")
        card = self.shoe.pop()
        hand.cards.append(card)
        return card

    def begin_player(self) -> None:
        self._require_phase("dealing")
        if len(self.player.cards) != 2 or len(self.dealer.cards) != 2:
            raise ValueError("Deal two cards to each hand first.")
        if self.player.blackjack and self.dealer.blackjack:
            self._finish("push", 0)
        elif self.dealer.blackjack:
            self._finish("loss", -self.wager)
        elif self.player.blackjack:
            self._finish("blackjack", self.wager * 3 // 2)
        else:
            self.phase = "player"

    def hit(self) -> None:
        self._require_phase("player")
        self.draw_to(self.player)
        if self.player.busted:
            self._finish("loss", -self.wager)
        elif self.player.total == 21:
            self.phase = "dealer"

    def stand(self) -> None:
        self._require_phase("player")
        self.phase = "dealer"

    def double(self) -> None:
        if not self.can_double:
            raise ValueError("Double requires two cards and enough bankroll for another bet.")
        self.draw_to(self.player)
        self.bank -= self.bet
        self.wager += self.bet
        if self.player.busted:
            self._finish("loss", -self.wager)
        else:
            self.phase = "dealer"

    def dealer_step(self) -> None:
        self._require_phase("dealer")
        if self.dealer.total < 17:
            self.draw_to(self.dealer)
        if self.dealer.total >= 17:
            self._settle()

    def _settle(self) -> None:
        if self.player.busted:
            self._finish("loss", -self.wager)
        elif self.dealer.busted or self.player.total > self.dealer.total:
            self._finish("win", self.wager)
        elif self.player.total < self.dealer.total:
            self._finish("loss", -self.wager)
        else:
            self._finish("push", 0)

    def _finish(self, outcome: str, profit: int) -> None:
        if self.phase == "done":
            return
        self.outcome = outcome
        self.profit = profit
        self.bank += self.wager + profit
        self.rounds += 1
        self.wins += int(profit > 0)
        self.blackjacks += int(self.player.blackjack)
        self.phase = "done"

BG = "#0c201e"
PANEL = "#142e29"
FELT = "#123d36"
EDGE = "#2a5146"
GOLD = "#d5b773"
CREAM = "#f6f0de"
MUTED = "#9bb5a7"
RED = "#b74743"
INK = "#20342e"


def number(value):
    return f"{value:,}".replace(",", " ")


def rounded(canvas, x1, y1, x2, y2, radius=12, **options):
    radius = max(1, min(radius, (x2 - x1) / 2, (y2 - y1) / 2))
    points = [x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
              x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
              x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1]
    return canvas.create_polygon(points, smooth=True, splinesteps=20, **options)


class Button(tk.Canvas):
    """A small keyboard-accessible button that looks the same on every platform."""

    def __init__(self, parent, text, command, width=134, height=46, primary=False):
        super().__init__(parent, width=width, height=height, bg=PANEL,
                         highlightthickness=0, bd=0, takefocus=True)
        self.text, self.command, self.primary = text, command, primary
        self.enabled, self.hover, self.selected = True, False, False
        self.bind("<Configure>", lambda event: self.draw())
        self.bind("<Enter>", lambda event: self.enter(True))
        self.bind("<Leave>", lambda event: self.enter(False))
        self.bind("<ButtonRelease-1>", self.click)
        self.bind("<Return>", self.invoke)
        self.bind("<space>", self.invoke)
        self.bind("<FocusIn>", lambda event: self.draw())
        self.bind("<FocusOut>", lambda event: self.draw())

    def enter(self, inside):
        self.hover = inside
        self.draw()

    def click(self, event):
        if 0 <= event.x < self.winfo_width() and 0 <= event.y < self.winfo_height():
            if self.enabled:
                self.focus_set()
            self.invoke()

    def invoke(self, event=None):
        if self.enabled:
            self.command()
        return "break"

    def update_state(self, enabled=True, text=None, selected=False):
        self.enabled, self.selected = enabled, selected
        if text is not None:
            self.text = text
        self.configure(cursor="hand2" if enabled else "arrow", takefocus=enabled)
        self.draw()

    def draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        fill = GOLD if self.primary else ("#24483e" if self.hover else "#1b3932")
        outline = GOLD if self.selected or self.focus_get() == self else EDGE
        color = BG if self.primary else CREAM
        if not self.enabled:
            fill, outline, color = "#172f29", "#234037", "#607a6b"
        elif self.primary and self.hover:
            fill = "#e4ca92"
        rounded(self, 1, 1, max(2, w - 1), max(2, h - 1), 10,
                fill=fill, outline=outline, width=1.5)
        self.create_text(w / 2, h / 2, text=self.text, fill=color,
                         font=("Helvetica", 13 if h > 40 else 11, "bold"))


class BlackjackApp:
    DEAL_MS = 190
    DEALER_MS = 580

    def __init__(self, root):
        self.root, self.game = root, Game()
        self.bet = 50
        self.shown_bank = self.game.bank
        self.busy, self.closed = False, False
        self.revealed, self.motion, self.flip = False, None, None
        self.jobs = set()
        self.message = "Ditt bord. Din nästa hand."
        self.detail = "Välj din insats och dela korten."
        self.message_color = CREAM
        self.root.title("Nattklöver · Blackjack")
        self.root.geometry("1100x820")
        self.root.minsize(940, 720)
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        tkfont.nametofont("TkDefaultFont").configure(family="Helvetica", size=12)
        self.build_ui()
        for key, action in (("h", self.hit), ("s", self.stand),
                            ("d", self.double), ("<Return>", self.deal)):
            self.root.bind(key, lambda event, callback=action: callback())
        self.refresh()

    def build_ui(self):
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True, padx=28, pady=22)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)
        header = tk.Frame(outer, bg=BG)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        header.columnconfigure(1, weight=1)
        logo = tk.Canvas(header, width=48, height=48, bg=BG, highlightthickness=0)
        logo.grid(row=0, column=0, rowspan=2, padx=(0, 12))
        logo.create_oval(2, 2, 46, 46, fill=PANEL, outline=GOLD)
        logo.create_text(24, 24, text="♣", fill=GOLD, font=("Georgia", 30))
        tk.Label(header, text="NATTKLÖVER", fg=CREAM, bg=BG,
                 font=("Helvetica", 23, "bold")).grid(row=0, column=1, sticky="w")
        tk.Label(header, text="BLACKJACK  /  ETT BORD FÖR DIG", fg=MUTED, bg=BG,
                 font=("Helvetica", 9)).grid(row=1, column=1, sticky="w")
        self.bank_text = tk.StringVar()
        self.stats_text = tk.StringVar(value="Händer 0  ·  Vinster 0")
        tk.Label(header, textvariable=self.bank_text, fg=GOLD, bg=BG,
                 font=("Helvetica", 24, "bold")).grid(row=0, column=2, sticky="e")
        tk.Label(header, textvariable=self.stats_text, fg=MUTED, bg=BG,
                 font=("Helvetica", 10)).grid(row=1, column=2, sticky="e")

        self.board = tk.Canvas(outer, bg=FELT, highlightbackground=EDGE,
                               highlightthickness=1, bd=0)
        self.board.grid(row=1, column=0, sticky="nsew")
        self.board.bind("<Configure>", lambda event: self.draw_board())

        controls = tk.Frame(outer, bg=PANEL, padx=18, pady=14)
        controls.grid(row=2, column=0, sticky="ew", pady=(14, 0))
        controls.columnconfigure(0, weight=1)
        wagers = tk.Frame(controls, bg=PANEL)
        wagers.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        wagers.columnconfigure(8, weight=1)
        tk.Label(wagers, text="INSATS", fg=MUTED, bg=PANEL,
                 font=("Helvetica", 9, "bold")).grid(row=0, column=0, sticky="w")
        self.bet_text = tk.StringVar()
        tk.Label(wagers, textvariable=self.bet_text, fg=CREAM, bg=PANEL,
                 font=("Helvetica", 21, "bold"), width=6, anchor="w").grid(
                     row=1, column=0, sticky="w", padx=(0, 18))
        self.chips = {}
        for column, value in enumerate((10, 20, 50, 100), start=1):
            button = Button(wagers, str(value), lambda amount=value: self.set_bet(amount), 48, 36)
            button.grid(row=0, column=column, rowspan=2, padx=3)
            self.chips[value] = button
        self.minus = Button(wagers, "−", lambda: self.set_bet(self.bet - 10), 38, 36)
        self.minus.grid(row=0, column=5, rowspan=2, padx=(12, 3))
        self.plus = Button(wagers, "+", lambda: self.set_bet(self.bet + 10), 38, 36)
        self.plus.grid(row=0, column=6, rowspan=2, padx=3)
        self.maximum = Button(wagers, "Max", self.max_bet, 52, 36)
        self.maximum.grid(row=0, column=7, rowspan=2, padx=3)
        self.reset_button = Button(wagers, "Ny bank", self.reset_bank, 108, 36)
        self.reset_button.grid(row=0, column=9, rowspan=2, sticky="e")

        actions = tk.Frame(controls, bg=PANEL)
        actions.grid(row=1, column=0, sticky="ew")
        actions.columnconfigure(3, weight=1)
        self.hit_button = Button(actions, "Ta kort", self.hit)
        self.stand_button = Button(actions, "Stanna", self.stand)
        self.double_button = Button(actions, "Dubbla", self.double)
        for column, button in enumerate((self.hit_button, self.stand_button, self.double_button)):
            button.grid(row=0, column=column, padx=(0, 8))
        self.deal_button = Button(actions, "Dela kort", self.deal, 210, primary=True)
        self.deal_button.grid(row=0, column=3, sticky="e")
        tk.Label(outer, text="H  Ta kort     S  Stanna     D  Dubbla     Enter  Dela     ·     Blackjack 3:2  /  Dealern stannar på alla 17",
                 bg=BG, fg=MUTED, font=("Helvetica", 9)).grid(row=3, column=0, pady=(12, 0))

    def later(self, delay, callback):
        def run():
            self.jobs.discard(job)
            if not self.closed:
                callback()
        job = self.root.after(delay, run)
        self.jobs.add(job)

    def cancel_jobs(self):
        for job in self.jobs:
            self.root.after_cancel(job)
        self.jobs.clear()

    def set_bet(self, amount):
        if not self.busy and self.game.phase in ("betting", "done"):
            self.bet = max(10, min(amount, self.game.bank // 10 * 10)) if self.game.bank >= 10 else 0
            self.refresh()

    def max_bet(self):
        self.set_bet(self.game.bank // 10 * 10)

    def refresh(self):
        idle = not self.busy and self.game.phase in ("betting", "done")
        playing = not self.busy and self.game.phase == "player"
        if idle:
            self.bet = min(self.bet, self.game.bank // 10 * 10)
        self.bank_text.set(f"{number(self.shown_bank)} marker")
        self.bet_text.set(number(self.bet if idle else self.game.wager))
        for value, button in self.chips.items():
            button.update_state(idle and value <= self.game.bank, selected=self.bet == value)
        self.minus.update_state(idle and self.bet > 10)
        self.plus.update_state(idle and self.bet + 10 <= self.game.bank)
        self.maximum.update_state(idle and self.game.bank >= 10)
        self.reset_button.update_state(idle)
        self.hit_button.update_state(playing)
        self.stand_button.update_state(playing)
        self.double_button.update_state(playing and self.game.can_double)
        self.deal_button.update_state(idle and self.game.ready and self.bet >= 10,
                                      "Spela igen" if self.game.rounds else "Dela kort")
        self.draw_board()

    def deal(self):
        if self.busy or not self.game.ready or self.bet < 10:
            return
        self.cancel_jobs()
        self.game.start_round(self.bet)
        self.busy, self.revealed = True, False
        self.shown_bank = self.game.bank
        self.message, self.detail, self.message_color = "Korten är på väg.", "En ny hand. Nya möjligheter.", CREAM
        self.refresh()
        self.deal_initial(0)

    def deal_initial(self, index):
        if index == 4:
            self.game.begin_player()
            if self.game.phase == "done":
                self.reveal(self.finish)
            else:
                self.player_ready()
            return
        name = "player" if index % 2 == 0 else "dealer"
        self.game.draw_to(getattr(self.game, name))
        self.animate_card(name, lambda: self.later(100, lambda: self.deal_initial(index + 1)))

    def player_ready(self):
        self.busy = False
        self.message, self.detail, self.message_color = "Din tur.", "Ta ett kort, stanna eller dubbla din insats.", CREAM
        self.refresh()

    def hit(self):
        if self.busy or self.game.phase != "player":
            return
        self.busy = True
        self.game.hit()
        self.refresh()
        self.animate_card("player", self.after_player)

    def stand(self):
        if not self.busy and self.game.phase == "player":
            self.game.stand()
            self.dealer_turn()

    def double(self):
        if self.busy or not self.game.can_double:
            return
        self.busy = True
        self.game.double()
        self.shown_bank = self.game.bank
        self.message, self.detail = "Dubbelt upp.", "Ett sista kort till din hand."
        self.refresh()
        self.animate_card("player", self.after_player)

    def after_player(self):
        if self.game.phase == "player":
            self.player_ready()
        elif self.game.phase == "dealer":
            self.dealer_turn()
        else:
            self.finish()

    def dealer_turn(self):
        self.busy = True
        self.message, self.detail = "Dealerns tur.", "Dealern drar till 17 och stannar även på mjuk 17."
        self.refresh()
        self.reveal(lambda: self.later(self.DEALER_MS, self.dealer_step))

    def dealer_step(self):
        count = len(self.game.dealer.cards)
        self.game.dealer_step()
        if len(self.game.dealer.cards) > count:
            self.animate_card("dealer", lambda: self.later(
                self.DEALER_MS, self.finish if self.game.phase == "done" else self.dealer_step))
        else:
            self.finish()

    def finish(self):
        self.busy = False
        self.shown_bank = self.game.bank
        titles = {"blackjack": "Blackjack!", "win": "Den handen är din.",
                  "loss": "Du sprack." if self.game.player.busted else "Dealern tar handen.",
                  "push": "Lika. Insatsen tillbaka."}
        self.message = titles[self.game.outcome]
        self.message_color = GOLD if self.game.profit > 0 else ("#e4a99a" if self.game.profit < 0 else CREAM)
        profit = self.game.profit
        self.detail = (f"+{number(profit)} marker" if profit > 0 else
                       f"−{number(-profit)} marker" if profit < 0 else "±0 marker")
        if self.game.outcome == "blackjack":
            self.detail += "  ·  Blackjack betalar 3:2"
        if self.game.bank < 10:
            self.detail += "  ·  Välj Ny bank för att börja om."
        self.stats_text.set(f"Händer {self.game.rounds}  ·  Vinster {self.game.wins}")
        self.refresh()

    def reset_bank(self):
        if self.busy or self.game.phase not in ("betting", "done"):
            return
        self.cancel_jobs()
        self.game, self.bet, self.shown_bank = Game(), 50, 1000
        self.revealed, self.motion, self.flip = False, None, None
        self.message, self.detail, self.message_color = "Nytt bord. Ny chans.", "Du börjar med 1 000 marker.", CREAM
        self.stats_text.set("Händer 0  ·  Vinster 0")
        self.refresh()

    def animate_card(self, name, callback):
        for_frame = {"index": 0}
        def step():
            progress = for_frame["index"] / 12
            self.motion = (name, progress)
            self.draw_board()
            if for_frame["index"] == 12:
                self.motion = None
                self.draw_board()
                callback()
            else:
                for_frame["index"] += 1
                self.later(self.DEAL_MS // 12, step)
        step()

    def reveal(self, callback):
        if self.revealed:
            callback()
            return
        def step(frame=0):
            self.flip = frame / 12
            self.draw_board()
            if frame == 12:
                self.flip, self.revealed = None, True
                self.draw_board()
                callback()
            else:
                self.later(20, lambda: step(frame + 1))
        step()

    def card_layout(self, name):
        w, h = self.board.winfo_width(), self.board.winfo_height()
        card_h = max(84, min(146, (h - 172) / 2))
        card_w = card_h * .69
        cards = getattr(self.game, name).cards
        count = max(2, len(cards))
        gap = min(card_w + 12, (max(200, w - 150) - card_w) / max(1, count - 1))
        left = (w - card_w - (count - 1) * gap) / 2
        top = 46 if name == "dealer" else h - card_h - 27
        return left, top, card_w, card_h, gap

    def draw_board(self):
        c = self.board
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 100 or h < 100:
            return
        c.create_rectangle(10, 10, w - 10, h - 10, outline="#205047")
        c.create_arc(w * .12, -h * .8, w * .88, h * .94, start=194, extent=152,
                     style="arc", outline="#1b4c41", width=1)
        c.create_text(25, 27, text="BLACKJACK  3 : 2", anchor="w",
                      fill="#719581", font=("Helvetica", 9, "bold"))
        c.create_text(w - 25, 27, text="6 KORTLEKAR", anchor="e",
                      fill="#719581", font=("Helvetica", 9))
        for name in ("dealer", "player"):
            left, top, cw, ch, gap = self.card_layout(name)
            hand = getattr(self.game, name)
            visible = Hand(hand.cards[:-1]) if self.motion and self.motion[0] == name else hand
            score = "?" if name == "dealer" and not self.revealed else str(visible.total)
            if not visible.cards:
                score = "—"
            elif (name == "player" or self.revealed) and visible.blackjack:
                score = "BLACKJACK"
            elif (name == "player" or self.revealed) and visible.busted:
                score += " · SPRUCKEN"
            title = "DEALERN" if name == "dealer" else "DIN HAND"
            c.create_text(w / 2, top - 20, text=f"{title}   ·   {score}",
                          fill=MUTED if name == "dealer" else GOLD, font=("Helvetica", 11, "bold"))
            if not hand.cards:
                for index in range(2):
                    x = left + index * gap
                    rounded(c, x, top, x + cw, top + ch, 8, fill="#133930", outline="#34604d")
                    c.create_text(x + cw / 2, top + ch / 2, text="♣", fill="#2a5745", font=("Georgia", 32))
            for index, card in enumerate(hand.cards):
                if self.motion and self.motion[0] == name and index == len(hand.cards) - 1:
                    continue
                x, hidden = left + index * gap, name == "dealer" and index == 1 and not self.revealed
                scale = 1
                if name == "dealer" and index == 1 and self.flip is not None:
                    scale = max(.025, abs(math.cos(math.pi * self.flip)))
                    hidden = self.flip < .5
                self.draw_card(card, x + cw * (1 - scale) / 2, top, cw * scale, ch, hidden)
        _, dy, _, dh, _ = self.card_layout("dealer")
        _, py, _, _, _ = self.card_layout("player")
        middle = (dy + dh + py - 36) / 2
        c.create_text(w / 2, middle - 3, text=self.message, fill=self.message_color,
                      font=("Helvetica", 22, "bold"), width=w - 100)
        c.create_text(w / 2, middle + 27, text=self.detail, fill=MUTED,
                      font=("Helvetica", 11), width=w - 100)
        if self.motion:
            name, progress = self.motion
            left, top, cw, ch, gap = self.card_layout(name)
            hand = getattr(self.game, name)
            target = left + (len(hand.cards) - 1) * gap
            ease = 1 - (1 - progress) ** 3
            x, y = (w - 85) * (1 - ease) + target * ease, 30 * (1 - ease) + top * ease
            hidden = name == "dealer" and len(hand.cards) == 2 and not self.revealed
            self.draw_card(hand.cards[-1], x, y, cw, ch, hidden)

    def draw_card(self, card, x, y, w, h, hidden=False):
        c = self.board
        rounded(c, x + 3, y + 4, x + w + 3, y + h + 4, 8, fill="#0d2b25", outline="")
        rounded(c, x, y, x + w, y + h, 8, fill="#193c39" if hidden else CREAM,
                outline=CREAM, width=1)
        if w < h * .28:
            return
        scale = min(1, w / (h * .69))
        if hidden:
            rounded(c, x + 5, y + 5, x + w - 5, y + h - 5, 5, fill="", outline="#a9905f")
            for row in range(12, int(h) - 8, 13):
                for col in range(12, int(w) - 8, 13):
                    c.create_polygon(x + col, y + row - 3, x + col + 3, y + row,
                                     x + col, y + row + 3, x + col - 3, y + row,
                                     outline="#476356", fill="")
            c.create_oval(x + w * .22, y + h * .31, x + w * .78, y + h * .69,
                          fill="#193c39", outline=GOLD)
            c.create_text(x + w / 2, y + h / 2, text="♣", fill=GOLD, font=("Georgia", max(10, int(w * .38))))
            return
        color = RED if card.suit in ("hearts", "diamonds") else INK
        rank, suit = RANK_LABELS[card.rank], SUIT_SYMBOLS[card.suit]
        size = max(4, int(h * .105 * scale))
        for px, py, angle in ((x + w * .14, y + h * .12, 0),
                              (x + w * .86, y + h * .88, 180)):
            c.create_text(px, py, text=rank, fill=color, font=("Georgia", size, "bold"), angle=angle)
            c.create_text(px, py + (h * .12 if angle == 0 else -h * .12), text=suit,
                          fill=color, font=("Georgia", size), angle=angle)
        if card.rank > 10:
            rounded(c, x + w * .29, y + h * .22, x + w * .71, y + h * .78, 4,
                    fill="#ece2cc", outline="#d7cbb0")
            c.create_text(x + w / 2, y + h * .44, text=rank, fill=color,
                          font=("Georgia", max(6, int(h * .24 * scale)), "bold"))
            c.create_text(x + w / 2, y + h * .64, text=suit, fill=color,
                          font=("Georgia", max(6, int(h * .17 * scale))))
            return
        pips = {
            1: [(.5, .5)], 2: [(.5, .3), (.5, .7)],
            3: [(.5, .28), (.5, .5), (.5, .72)],
            4: [(a, b) for a in (.34, .66) for b in (.3, .7)],
            5: [(a, b) for a in (.34, .66) for b in (.3, .7)] + [(.5, .5)],
            6: [(a, b) for a in (.34, .66) for b in (.28, .5, .72)],
            7: [(a, b) for a in (.34, .66) for b in (.28, .5, .72)] + [(.5, .39)],
            8: [(a, b) for a in (.34, .66) for b in (.25, .5, .75)] + [(.5, .37), (.5, .63)],
            9: [(a, b) for a in (.32, .5, .68) for b in (.28, .5, .72)],
            10: [(a, b) for a in (.34, .66) for b in (.24, .41, .59, .76)] + [(.5, .33), (.5, .67)]
        }
        for px, py in pips[card.rank]:
            c.create_text(x + w * px, y + h * py, text=suit, fill=color,
                          font=("Georgia", max(6, int(h * (.3 if card.rank == 1 else .14) * scale))))

    def close(self):
        self.closed = True
        self.cancel_jobs()
        self.root.destroy()


def main():
    root = tk.Tk()
    BlackjackApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
