lazy import random
import time
class Card:
    def __init__(self,suit,value):
        self.suit = suit
        self.value = value
        
    def print_card(self):
        to_print = str(self.value)
        match self.value:
            case 11: to_print = "Knight"
            case 12: to_print = "Queen"
            case 13: to_print = "King"
            case 14: to_print = "Ace"

        print(f"{to_print} of {self.suit}")

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
    
def draw_card()->Card:
    suit = ""
    match random.randint(1,4):
        case 1: suit = "hearts"
        case 2: suit = "clubs"
        case 3: suit = "spades"
        case 4: suit = "diamonds"

    value = random.randint(2,13)

    return Card(suit,value)

def give_card(recipient,amount = 1):
    for _ in range(amount):
        random_card = draw_card()
        recipient.hand.append(random_card)

def print_start():
    print("Welcome to Blackjack!")

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
            #klätt kort
            value = 10
        elif value == 14:
            #ess
            if total_value + 11 > 21:
                value = 1
            else: value = 11
        total_value += value
    
    if total_value > 21:
        return total_value,"BUSTED"
    elif total_value == 21:
        return total_value,"BLACKJACK"
    else: return total_value,"UNDER"

def print_player_hand(player):
    print(f"\n\n{player.name}:s cards")
    print("-----------------")
    for card in player.hand:
        card.print_card()
    sum,unused = check_value(player)
    print(f"\nCard sum: {sum}")    

def hit(player):
    give_card(player)
    print_player_hand(player)
    unused,state = check_value(player)
    return state
    
def stand(player):
    pass

def house_turn():
    pass

def player_turn(player):
    print_player_hand(player)
    while True:
        user_choice = ask_user_choice("Choose your option",{"h":"Hit","s":"Stand"})
        match(user_choice):
            case "h":
                match(hit(player)):

                    case "BUSTED":
                        print("Busted :(")
                        input("Press Space to continue...")
                        break
                    case "BLACKJACK": 
                        print("BLACKJACK!!!") 
                        input("Press Space to continue...")
                        break
                    case "UNDER": continue
            case "s":
                print_player_hand(player)
                break
    
def runner():
    print_start()
    players = init_players(ask_player_amount())
    while True:
        for player in players:
            #initial deal
            give_card(player,2)
            #game turn
            if player.name == "house":
                house_turn()
            else: player_turn(player)

runner()