import contextlib
import io
import unittest
from unittest.mock import patch

import blackjack as bj


def hand(player, *values):
    player.hand = [bj.Card('spades', value) for value in values]
    return player


class BlackjackTests(unittest.TestCase):
    def setUp(self):
        self.player = bj.Player(100, 'Player')
        self.dealer = bj.Player(0, 'Dealer')
        self.game = bj.Game([self.player], self.dealer, bj.make_deck())

    def settle(self, cards, dealer_cards, expected):
        hand(self.player, *cards)
        hand(self.dealer, *dealer_cards)
        self.game.place_bet(self.player, 10)
        self.assertEqual(self.game.check_winner()[self.player], expected[0])
        self.assertEqual(self.player.bank, expected[1])
        self.assertEqual(self.player.insats, 0)
        self.game.check_winner()
        self.assertEqual(self.player.bank, expected[1])

    def test_settlement(self):
        cases = [
            ((10, 9), (10, 8), ('WIN', 110)),
            ((10, 8), (10, 9), ('LOSS', 90)),
            ((10, 9), (10, 9), ('PUSH', 100)),
            ((14, 13), (10, 9), ('WIN', 115)),
            ((14, 13), (14, 12), ('PUSH', 100)),
            ((7, 7, 7), (14, 13), ('LOSS', 90)),
            ((14, 13), (7, 7, 7), ('WIN', 115)),
            ((10, 9, 5), (10, 9, 5), ('LOSS', 90)),
            ((10, 8), (10, 9, 5), ('WIN', 110)),
        ]
        for cards, dealer_cards, expected in cases:
            with self.subTest(cards=cards, dealer=dealer_cards):
                self.setUp()
                self.settle(cards, dealer_cards, expected)

    def test_players_settle_independently(self):
        other = hand(bj.Player(100, 'Other'), 10, 8)
        self.game.players.append(other)
        hand(self.player, 10, 10)
        hand(self.dealer, 10, 7)
        for player in self.game.players:
            self.game.place_bet(player, 10)
        self.assertEqual(list(self.game.check_winner().values()), ['WIN', 'WIN'])
        self.assertEqual([p.bank for p in self.game.players], [110, 110])

    def test_invalid_and_duplicate_bets(self):
        for amount in (-10, 0, 101):
            with self.assertRaises(ValueError):
                self.game.place_bet(self.player, amount)
            self.assertEqual(self.player.bank, 100)
        self.game.place_bet(self.player, 10)
        with self.assertRaises(ValueError):
            self.game.place_bet(self.player, 10)
        self.assertEqual(self.player.bank, 90)

    def test_refund_once(self):
        self.game.place_bet(self.player, 100)
        self.game.refund_bets()
        self.game.refund_bets()
        self.assertEqual(self.player.bank, 100)
        self.assertEqual(self.player.insats, 0)

    def test_aces_and_natural_blackjack(self):
        self.assertEqual(hand(self.player, 14, 14, 9).get_hand_value(), 21)
        self.assertEqual(self.player.get_state(), 'TWENTY_ONE')
        self.assertEqual(hand(self.player, 14, 13).get_state(), 'BLACKJACK')

    def test_deck_and_atomic_dealing(self):
        self.assertEqual(len(bj.make_deck(2)), 104)
        self.game.deck = [bj.Card('hearts', 2)]
        with self.assertRaises(bj.EmptyDeckError):
            self.game.give_card(self.player, 2)
        self.assertEqual(len(self.game.deck), 1)
        self.assertEqual(self.player.hand, [])

    def test_dealer_stands_on_soft_17(self):
        hand(self.dealer, 14, 6)
        self.game.dealer_turn()
        self.assertEqual(len(self.dealer.hand), 2)

    def test_initial_bank_validation(self):
        with patch('builtins.input', side_effect=['Test', 'bad', '0', '-1', '100']):
            self.assertEqual(bj.prompt_players(1)[0].bank, 100)

    def test_complete_console_round(self):
        deck = [bj.Card('spades', value) for value in (10, 7, 14, 13)]
        with patch.object(bj, 'make_deck', return_value=deck), patch.object(bj.random, 'randrange', return_value=0), patch('builtins.input', side_effect=['1', 'Test', '100', '10', '', 'n']):
            bj.game_runner()

    def test_cancelled_round_refunds_and_can_restart(self):
        player = bj.Player(100, 'Test')
        empty, full = [], [bj.Card('spades', v) for v in (10, 7, 14, 13)]
        with patch.object(bj, 'prompt_players', return_value=[player]), patch.object(bj, 'ask_player_count', return_value=1), patch.object(bj, 'make_deck', side_effect=[empty, full]), patch.object(bj.random, 'randrange', return_value=0), patch('builtins.input', side_effect=['10', '', '10', '', 'n']):
            bj.game_runner()
        self.assertEqual(player.bank, 115)

    def test_zero_bank_exits(self):
        with patch.object(bj, 'prompt_players', return_value=[bj.Player(0, 'Test')]), patch.object(bj, 'ask_player_count', return_value=1):
            bj.game_runner()


if __name__ == '__main__':
    with contextlib.redirect_stdout(io.StringIO()):
        unittest.main()
