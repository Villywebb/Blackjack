lazy import random
lazy import time

NUM_OF_DECKS = 1
DEALER_DELAY = 0.8

class EmptyDeckError(Exception):
    pass

class Card:#╔ ╗ ╚ ╝ ═ ║
   
    cardback_ascii = [
                 "╔═════════╗",
                 "║◆ ◇ ◆ ◇ ◆║",
                 "║ ◇ ◆ ◇ ◆ ║",
                 "║◆ ◇ ◆ ◇ ◆║",
                 "║ ◇ ◆ ◇ ◆ ║",
                 "║◆ ◇ ◆ ◇ ◆║",
                 "╚═════════╝"]
    def __init__(self,suit,value):
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

    def get_ascii(self)->list[str]:
        red = "\033[38;2;255;0;0m"
        reset = "\033[0m"
        suits_unicode = {"spades": "\u2660","hearts":f"{red}\u2665{reset}","diamonds":f"{red}\u2666{reset}","clubs":"\u2663"}
        s = suits_unicode[self.suit]
        v = self.get_value_str()

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
    def __init__(self,name:str):
        self.name = name
        self.hand = []

    def get_sorted_card_values(self)->list[int]:
        value_list = []
        for card in self.hand:
            value_list.append(card.value)
        value_list.sort()
        return value_list

    def get_total_value(self):
        total_value = 0
        aces = 0
        for value in self.get_sorted_card_values():
            if value >= 11 and value <= 13: 
                #face card
                value = 10
            elif value == 14:
                #ace
                value = 11
                aces += 1
            total_value += value

        while total_value > 21 and aces > 0:
            total_value -= 10
            aces -= 1
        return total_value
    
    def get_state(self):
        total_value = self.get_total_value()
        if total_value > 21:
            return "BUSTED"
        elif total_value == 21:
            if len(self.hand) == 2:
                return "BLACKJACK"
            return "TWENTY_ONE"
        else: return "UNDER"
    
def make_deck(num_of_decks:int = 1)->list[Card]:
    deck = []
    suits = ["hearts","clubs","spades","diamonds"]
    for _ in range(num_of_decks):
        for value in range(2,15):
            for suit in suits:
                deck.append(Card(suit,value))
    return deck

def print_start():
    message = "Welcome to the Blackjack simulator 1.0!"
    underscore = "═"*len(message)
    print(f"\n{underscore}\n\n{message}\n\n{underscore}\n")

def ask_player_amount():
    while True:
        try:
            amount = int(input("Player amount: "))
            if 1 <= amount:
                return amount
            else:
                print("choose more than 0 players")
        except ValueError:
            print("only ints dude")

def init_players(amount):
    players = []
    for i in range(amount):
        name = input(f"Player nr {i+1}:s name: ").strip()
        players.append(Player(name))
    return players

def ask_user_choice(question:str,letters_options:dict[str,str])->str:
    '''prints a list of options and returns user choice letter
    letter is key, option is value.
    Safe - can only return one of the defined letters'''
    print(f"\n{question}")
    user_input = ""
    while True:
        print()
        for letter,option in letters_options.items():
            print(f"  {letter}) {option}")
        user_input = input("\n  ▶ ").lower()
        for letter in letters_options:
            if user_input == letter:
                return user_input
        print("\nChoose one of the options!\n")
    
def print_player_dealer_hand(player,dealer):
    cards_rows = []
    card_width = len(Card.cardback_ascii[0])+2
    player_hand_width = len(player.hand)*(card_width)
    print("\n\n"+f"{player.name}:s hand".ljust(player_hand_width + 10)+ "Dealers hand")
    player_underscore = "═"*(player_hand_width-2)
    dealer_underscore = "═"*((len(dealer.hand)*card_width) - 2)
    print(player_underscore.ljust(player_hand_width + 10)+dealer_underscore)

    for card in player.hand:
        cards_rows.append(card.get_ascii())
    #space
    cards_rows.append([" "*8]*len(Card.cardback_ascii))
    #dealer cards
    cards_rows.append(dealer.hand[0].get_ascii())
    cards_rows.append(Card.cardback_ascii)
        
    for row_index in range(len(cards_rows[0])):
        for card in cards_rows:
            print(card[row_index], end="  ")
        print()

    print(f"\nCard sum: {player.get_total_value()}".ljust(player_hand_width+11)+f"Card sum: {min(10,dealer.hand[0].value)}")

def print_dealer_hand(dealer):
    cards_rows = []
    for card in dealer.hand:
        cards_rows.append(card.get_ascii())

    underscore = "═"*((len(Card.cardback_ascii[0])+2) * len(dealer.hand))
    print("\n\nDealer's hand")
    print(underscore)

    for row_index in range(len(Card.cardback_ascii)):
        for card_rows in cards_rows:
            print(card_rows[row_index], end="  ")
        print()

    print(f"\nCard sum: {dealer.get_total_value()}")

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
        print("under 21")
      
class Game:
    def __init__(self,players,dealer,deck = make_deck(NUM_OF_DECKS)):
        self.deck = deck
        self.players = self.clear_players_hands(players)
        self.dealer = dealer

    def clear_players_hands(self,players):
        for player in players:
            player.hand.clear()
        return players
    
    def give_card(self,recipient,amount = 1):
        if amount > len(self.deck):
            raise EmptyDeckError("Not enough cards left to finish the round")
        for _ in range(amount):
            random_card = self.deck.pop(random.randrange(len(self.deck)))
            recipient.hand.append(random_card)

    def hit(self,player):
        self.give_card(player)

    def player_turn(self,player):
        print_player_dealer_hand(player,self.dealer)
        state = player.get_state()
        while state == "UNDER":
            #TODO: maybe use lambda function instead?
            user_choice = ask_user_choice(f"{player.name}:s move?",{"h":"Hit","s":"Stand"})
            
            if user_choice == "s":
                return
            
            #user choice must be hit here
            self.hit(player)
            state = player.get_state()
            print_player_dealer_hand(player,self.dealer)

        print_state(player, state)

        input("\nPress Enter to continue")
        return

    def dealer_turn(self):
        
        print_dealer_hand(self.dealer)

        # hit until 17 or over
        while self.dealer.get_total_value() < 17:
            self.hit(self.dealer)
            time.sleep(DEALER_DELAY)
            print_dealer_hand(self.dealer)

        state = self.dealer.get_state()
        print_state(self.dealer,state,is_dealer=True)
        return state

    def check_winner(self):
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
            score = (state == "BLACKJACK", player.get_total_value())
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
    players = init_players(ask_player_amount())
    deck = make_deck()

    while True:

        game = Game(players,Player("The Dealer"),deck)
        
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
            input("Press Enter to start a new round")
            deck = make_deck()
            continue
        time.sleep(DEALER_DELAY)
        if winner is None:
            print("\nIT'S A DRAW")
        else:
            print(f"\n★ ★ ★ THE WINNER IS {winner.name} ★ ★ ★ ")
        input("\nPress Enter to continue")
        
game_runner()
