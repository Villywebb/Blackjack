lazy import random

NUM_OF_DECKS = 1

class Card:
    def __init__(self,suit,value):
        self.suit = suit
        self.value = value

    def __repr__(self) -> str:
        to_print = str(self.value)
        match self.value:
            case 11: to_print = "Knight"
            case 12: to_print = "Queen"
            case 13: to_print = "King"
            case 14: to_print = "Ace"
        return f"{to_print} of {self.suit}"

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
    
def make_deck(num_of_decks = 1)->list[Card]:
    deck = []
    suits = ["hearts","clubs","spades","diamonds"]
    for _ in range(num_of_decks):
        for value in range(2,15):
            for suit in suits:
                deck.append(Card(suit,value))
    return deck

def print_start():
    print("Welcome to the Blackjack simulator 1.0!")

def ask_player_amount():
    while True:
        try:
            return int(input("Player amount: "))
        except ValueError:
            print("only ints dude")

def init_players(amount):
    players = []
    for i in range(amount):
        name = Player(input(f"Player nr {i+1}:s name: ")) 
        if name != "house":
            players.append(name)
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
        user_input = input("\nOption: ").lower()
        for letter in letters_options:
            if user_input == letter:
                return user_input
        print("Choose one of the options!\n")

def check_value(player):
    total_value = 0
    for value in player.get_sorted_card_values():
        if value >= 11 and value <= 13: 
            #suited card
            value = 10
        elif value == 14:
            #ace
            if total_value + 11 > 21:
                value = 1
            else: value = 11
        total_value += value
    
    if total_value > 21:
        return total_value,"BUSTED"
    elif total_value == 21:
        return total_value,"BLACKJACK"
    else: return total_value,"UNDER"

def print_player_dealer_hand(player,dealer):
    print(f"\n\n{player.name}:s cards                       Dealers card")
    print("--------------                  --------------")
    count = 0
    for card in player.hand:
        #print dealer card only on first row
        if count == 0:
            print(f"{card}                   {dealer.hand[0]}")
        else: print(card)
        count+=1
    sum,_ = check_value(player)
    print(f"\nCard sum: {sum}                  Card value: {str(dealer.hand[0].value)}")    

class Game:
    def __init__(self,players,dealer):
        self.deck = make_deck(NUM_OF_DECKS)
        self.players = players
        self.dealer = dealer
    
    def give_card(self,recipient,amount = 1):
        for _ in range(amount):
            random_card = self.deck.pop(random.randint(0,len(self.deck)-1))
            recipient.hand.append(random_card)

    def hit(self,player):
        self.give_card(player)
        _,state = check_value(player)
        return state

    def player_turn(self,player):
        print_player_dealer_hand(player,self.dealer)
        while True:
            user_choice = ask_user_choice("Choose your option",{"h":"Hit","s":"Stand"})
            
            if user_choice == "s":
                return
            #user choice must be hit here

            state = self.hit(player)
            print_player_dealer_hand(player,self.dealer)

            match(state):
                case "BUSTED":
                    print("Busted :(")
                case "BLACKJACK": 
                    print("BLACKJACK!!!") 
                case "UNDER":
                    continue

            #bust or blackjack here, under continues
            input("Press Space to continue...")

def game_runner():
    print_start()
    players = init_players(ask_player_amount())
    dealer = Player("dealer")
    game = Game(players,dealer)
    while True:

        game.give_card(game.dealer,2)

        for player in game.players:

            game.give_card(player,2)

            game.player_turn(player)

game_runner()