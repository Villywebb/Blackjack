lazy import random

NUM_OF_DECKS = 1

class EmptyDeckError(Exception):
    pass

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
        user_input = input("\nOption: ").lower()
        for letter in letters_options:
            if user_input == letter:
                return user_input
        print("Choose one of the options!\n")

def whitespace_generator(left_string:str,right_string:str,whitespace = 35)->str:
    "Generates normalized whitespace between two strings"
    #removes newline chars before count -1 gives the last element of 
    #the split i.e. the actual string
    temp_left = left_string.split("\n")[-1]
    spacer = ""
    for _ in range(whitespace-len(temp_left)):
        spacer += " "
    return f"{left_string}{spacer}{right_string}"
    
def print_player_dealer_hand(player,dealer):
    print(whitespace_generator(f"\n\n{player.name}:s cards","Dealer card"))
    print(whitespace_generator("---------------","---------------"))
    count = 0
    for card in player.hand:
        #print dealer card only on first row
        if count == 0:
            print(whitespace_generator(str(card),dealer.hand[0]))
        else: print(card)
        count+=1
    sum = player.get_total_value()
    print(whitespace_generator(f"\nCard sum: {sum}",f"Card value: {str(dealer.hand[0].value)}"))

def print_dealer_hand(dealer):
    print(f"\n\nThe Dealers cards\n---------------")
    for card in dealer.hand:
        print(card)

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
        state = player.get_state()
        return state

    def player_turn(self,player):
        print_player_dealer_hand(player,self.dealer)
        state = player.get_state()
        while state == "UNDER":
            user_choice = ask_user_choice("Choose your option",{"h":"Hit","s":"Stand"})
            
            if user_choice == "s":
                return
            #user choice must be hit here

            state = self.hit(player)
            print_player_dealer_hand(player,self.dealer)

        match(state):
            case "BUSTED":
                print("\nBUSTED")
            case "BLACKJACK": 
                print("\nBLACKJACK!!")
            case "TWENTY_ONE":
                print("\n21!")

        input("\nPress Enter to continue")
        return

    def dealer_turn(self):
        while True:
            print_dealer_hand(self.dealer)
            sum = self.dealer.get_total_value()
            status = self.dealer.get_state()
            print(f"Card sum: {sum}\nStatus: {status}")
            if status == "UNDER":
                if sum < 17:
                    status = self.hit(self.dealer)
                else:
                    return status
            else:
                return status

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

        if winner is None:
            print("DRAW")
        else:
            print(f"THE WINNER IS: {winner.name}")

game_runner()
