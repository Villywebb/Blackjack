#!/usr/bin/env python3
import random
import time

"""TODO: implement bank and betting. implement split and double. implement correct winner-function.
implement quit alternative. maybe rename game class to "round" or turn or something.
maybe we need to start paying Vilmer.
"""

#can you pull this adam

NUM_OF_DECKS = 1
DEALER_DELAY = 1 #seconds

class EmptyDeckError(Exception):
    pass

class Card:
    cardback_ascii = [
                 "╔═════════╗",
                 "║◆ ◇ ◆ ◇ ◆║",
                 "║ ◇ ◆ ◇ ◆ ║",
                 "║◆ ◇ ◆ ◇ ◆║",
                 "║ ◇ ◆ ◇ ◆ ║",
                 "║◆ ◇ ◆ ◇ ◆║",
                 "╚═════════╝"]
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def get_value_str(self) -> str:
        to_print = str(self.value)
        match self.value:
            case 11: to_print = "J"
            case 12: to_print = "Q"
            case 13: to_print = "K"
            case 14: to_print = "A"
        return to_print

    def get_ascii(self) -> list[str]:
        #color the text red
        red = "\033[38;2;255;0;0m"
        #reset to og color
        reset = "\033[0m"
        suits_unicode = {"spades": "\u2660", "hearts": f"{red}\u2665{reset}", "diamonds": f"{red}\u2666{reset}", "clubs": "\u2663"}
        s = suits_unicode[self.suit]
        v = self.get_value_str()

        #Nice card!
        return [
        "╔═════════╗",
       f"║{v:<2}       ║",
        "║         ║",
       f"║    {s}    ║",
        "║         ║",
       f"║       {v:>2}║",
        "╚═════════╝",
    ]

class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand: list[Card] = []

    def get_hand_value(self) -> int:
        total_value = 0
        aces = 0
        for card in self.hand:
            value = card.value
            if value != 14:
                value = min(10, value)
            else: # is ace here
                value = 11
                aces += 1
            total_value += value
        #make 11 valued aces valued 1 if value is over 21
        while total_value > 21 and aces > 0:
            total_value -= 10
            aces -= 1
        return total_value
    
    def get_state(self) -> str:
        total_value = self.get_hand_value()
        if total_value > 21:
            return "BUSTED"
        elif total_value == 21:
            if len(self.hand) == 2:
                return "BLACKJACK"
            return "TWENTY_ONE"
        else: return "UNDER"
    
def print_start():
    message =r"""
 ________  ___       ________  ________  ___  __          ___  ________  ________  ___  __       
|\   __  \|\  \     |\   __  \|\   ____\|\  \|\  \       |\  \|\   __  \|\   ____\|\  \|\  \     
\ \  \|\ /\ \  \    \ \  \|\  \ \  \___|\ \  \/  /|_     \ \  \ \  \|\  \ \  \___|\ \  \/  /|_   
 \ \   __  \ \  \    \ \   __  \ \  \    \ \   ___  \  __ \ \  \ \   __  \ \  \    \ \   ___  \  
  \ \  \|\  \ \  \____\ \  \ \  \ \  \____\ \  \\ \  \|\  \\_\  \ \  \ \  \ \  \____\ \  \\ \  \ 
   \ \_______\ \_______\ \__\ \__\ \_______\ \__\\ \__\ \________\ \__\ \__\ \_______\ \__\\ \__\
    \|_______|\|_______|\|__|\|__|\|_______|\|__| \|__|\|________|\|__|\|__|\|_______|\|__| \|__|
"""
    print(message)                                  
    message1 = "Welcome to the BLACKJACK simulator 1.0!"
    underscore = "═"*len(message1)
    print(f"\n{underscore}\n\n{message1}\n\n{underscore}\n")

def ask_player_count(max_players: int):
    while True:
        try:
            amount = int(input("Player amount: "))
            if 1 <= amount <= max_players:
                return amount
            else:
                print(f"Choose between 1 players and {max_players}!")
        except ValueError:
            print("only ints dude")

def prompt_players(amount) -> list[Player]:
    players = []
    for i in range(amount):
        name = input(f"Player nr {i+1}:s name: ").strip()
        if name == "":
            name = f"Player{i+1}"
        players.append(Player(name))
    return players

def ask_user_choice(question: str, letters_options: dict[str, str]) -> str:
    '''prints a list of options and returns user choice letter
    letter is key, option is value.
    Safe - can only return one of the defined letters'''
    print(f"\n{question}")
    user_input = ""
    while True:
        print()
        for letter, option in letters_options.items():
            print(f"  {letter}) {option}")
        user_input = input("\n  ▶ ").strip().lower()
        if user_input in letters_options:
            return user_input
        print("\nChoose one of the options!\n")

def print_rows(cards_rows: list[list[str]]):
    """for every row, prints every cards corresponding row"""
    for row_index in range(len(cards_rows[0])):
        for card in cards_rows:
            print(card[row_index], end="  ")
        print()
    
def print_player_dealer_hand(player, dealer):
    cards_rows = []
    card_width = len(Card.cardback_ascii[0]) + 2
    player_hand_width = len(player.hand) * (card_width)

    print("\n\n"+f"{player.name}:s hand".ljust(player_hand_width + 10)+ "Dealer's hand")

    player_underscore = "═" * (player_hand_width - 2)
    dealer_underscore = "═" * ((len(dealer.hand) * card_width) - 2)
    print(player_underscore.ljust(player_hand_width + 10) + dealer_underscore)

    for card in player.hand:
        cards_rows.append(card.get_ascii())
    #space
    cards_rows.append([" "*8] * len(Card.cardback_ascii))
    #dealer cards
    cards_rows.append(dealer.hand[0].get_ascii())
    cards_rows.append(Card.cardback_ascii)

    print_rows(cards_rows)

    print(f"\nCard sum: {player.get_hand_value()}".ljust(player_hand_width+11) + f"Card sum: {"11" if dealer.hand[0].value == 14 else min(10,dealer.hand[0].value)}")

def print_dealer_hand(dealer):
    cards_rows = []
    for card in dealer.hand:
        cards_rows.append(card.get_ascii())

    underscore = "═" * ((len(Card.cardback_ascii[0])+2) * len(dealer.hand))
    print("\n\nDealer's hand")
    print(underscore)

    print_rows(cards_rows)

    print(f"\nCard sum: {dealer.get_hand_value()}")

def print_state(player, state,is_dealer = False):
    print(f"\n{player.name} got", end = " ")
    match(state):
        case "BUSTED":
            print("BUSTED")
        case "BLACKJACK": 
            print("BLACKJACK!")
        case "TWENTY_ONE":
            print("21!")
    if is_dealer and state == "UNDER":
        print(f"{player.get_hand_value()}")

def make_deck(num_of_decks: int = 1) -> list[Card]:
    deck = []
    suits = ["hearts", "clubs", "spades", "diamonds"]
    for _ in range(num_of_decks):
        for value in range(2, 15):
            for suit in suits:
                deck.append(Card(suit, value))
    return deck

def wait_for_user(message: str):
    input(message)

def clear_players_hands(players) -> list[Player]:
    for player in players:
        player.hand.clear()
    return players
      
class Game:
    def __init__(self, players: list[Player], dealer: Player, deck: list[Card]):
        self.deck = deck
        self.players = players
        self.dealer = dealer

    def give_card(self, recipient, amount = 1):
        if amount > len(self.deck):
            raise EmptyDeckError("Not enough cards left to finish the round")
        for _ in range(amount):
            random_card = self.deck.pop(random.randrange(len(self.deck)))
            recipient.hand.append(random_card)

    def hit(self, player):
        self.give_card(player)

    def player_turn(self, player):
        print_player_dealer_hand(player, self.dealer)
        state = player.get_state()
        while state == "UNDER":
            #TODO: maybe use lambda function instead? if we implement split and double aswell
            user_choice = ask_user_choice(f"{player.name}:s move?",{"h":"Hit", "s":"Stand"})
            
            if user_choice == "s":
                return
            
            #user choice must be hit here
            self.hit(player)
            state = player.get_state()
            print_player_dealer_hand(player, self.dealer)

        print_state(player, state)

        wait_for_user("\nPress Enter to continue")
        return

    def dealer_turn(self):
        print_dealer_hand(self.dealer)

        # hit until 17 or over
        while self.dealer.get_hand_value() < 17:
            self.hit(self.dealer)
            time.sleep(DEALER_DELAY)
            print_dealer_hand(self.dealer)

        state = self.dealer.get_state()
        print_state(self.dealer, state, is_dealer=True)
        return state

    def check_winner(self) -> Player | None:
        """returns winning player if there is one, else none if its a draw"""

        """TODO: remake winning system to a induvidual check against the dealer,
        so it matches correct blackjack rules"""

        #busted players have already lost, even if the dealer also busts
        if all(player.get_state() == "BUSTED" for player in self.players):
            return self.dealer

        best_score = (False, 0) #true is bigger than false
        winners = []
        for player in self.players + [self.dealer]:
            state = player.get_state()
            if state == "BUSTED":
                continue
            #a two card blackjack beats other hands worth 21
            score = (state == "BLACKJACK", player.get_hand_value())
            if score > best_score:
                best_score = score
                winners = [player]
            elif score == best_score: #lika
                winners.append(player)
        #if draw return none
        if len(winners) == 1:
            return winners[0]
        return None 
        
def game_runner():
    print_start()
    max_amount_players = (52 * NUM_OF_DECKS - 2) // 2
    players = prompt_players(ask_player_count(max_amount_players))
    deck = make_deck(NUM_OF_DECKS)

    while True:

        game = Game(clear_players_hands(players), Player("The Dealer"), deck)
        
        try:
            game.give_card(game.dealer,2)
            for player in game.players:
                game.give_card(player,2)
            for player in game.players:
                game.player_turn(player)

            #if both players didnt bust
            if any(player.get_state() != "BUSTED" for player in game.players):
                game.dealer_turn()

            winner = game.check_winner()

        except EmptyDeckError as error:
            print(f"\n{error} This round is cancelled")
            wait_for_user("\nPress Enter to start a new round")
            deck = make_deck(NUM_OF_DECKS)
            continue
        if winner is None:
            print("\nIT'S A DRAW")
        else:
            print(r"""
 ______ __  __  ______                             
/\__  _/\ \_\ \/\  ___\                            
\/_/\ \\ \  __ \ \  __\                            
   \ \_\\ \_\ \_\ \_____\                          
 __ \/_/__/___/___/_____/__   __  ______  ______   
/\ \  _ \ \/\ \/\ "-.\ \/\ "-.\ \/\  ___\/\  == \  
\ \ \/ ".\ \ \ \ \ \-.  \ \ \-.  \ \  __\\ \  __<  
 \ \__/".~\_\ \_\ \_\\"\_\ \_\\"\_\ \_____\ \_\ \_\
  \/_/   \/_/\/_/\/_/ \/_/\/_/ \/_/\/_____/\/_/ /_/
""")
           
            print(f"\n★ ★ ★ THE WINNER IS {winner.name} ★ ★ ★ ")
        wait_for_user("\nPress Enter to continue")
        
game_runner()
