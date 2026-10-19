
lazy import random
lazy from tkinter import simpledialog
lazy import tkinter as tk

NUM_OF_DECKS = 1
DEALER_DELAY = 1000

class EmptyDeckError(Exception):
    pass

class Card:
    def __init__(self,suit:str,value:int):
        self.suit = suit
        self.value = value
        self.color = self.get_color()

    def __repr__(self) -> str:
        to_print = str(self.value)
        match self.value:
            case 11: to_print = "Knight"
            case 12: to_print = "Queen"
            case 13: to_print = "King"
            case 14: to_print = "Ace"
        return f"{to_print} of {self.suit}"
    
    def get_color(self):
        card_color = '#c0201b'
        if self.suit == "spades" or self.suit == "clubs":
            card_color = '#FCFCFC'
        return card_color

class Player:
    def __init__(self,name:str,bank = 1000):
        self.name = name
        self.hand = []
        self.bank_value = bank
        self.current_bet = 0

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

def clear_players_hands(players):
    for player in players:
        player.hand.clear()
    return players

class Game:
    def __init__(self,players,dealer,deck = None):
        self.deck = make_deck(NUM_OF_DECKS) if deck is None else deck
        self.players = clear_players_hands(players)
        self.dealer = dealer

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

    def bet(self,player,bet_amount):
        player.bank -= bet_amount
        player.current_bet = bet_amount

    def dealer_turn(self):
        while self.dealer.get_total_value() < 17:
            self.hit(self.dealer)
        return self.dealer.get_state()

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
        
class BlackjackGUI():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Blackjack")
        self.root.geometry("1000x800+100+100")

    def start_game(self, game):
        self.game = game
        self.create_widgets()
        self.start_round()

    def init_players(self,amount):
        players = []

        for i in range(amount):
            name = simpledialog.askstring(title="Player name",prompt=f"Whats player nr {i + 1}:s name?",parent=self.root)
            if name is None: return None
            players.append(Player(name.strip()))

        return players
    
    def ask_player_amount(self):
        return simpledialog.askinteger(parent=self.root,title="Player amount",prompt="How many players?",minvalue=1,maxvalue=26*NUM_OF_DECKS-1)
    
    def player_hand_frame_maker(self,root,font_text):
        player_frame = tk.Frame(root)

        hand_label = tk.Frame(player_frame)
        hand_label.grid(row=0, column=0)

        name_label = tk.Label(player_frame, font=font_text)
        name_label.place(in_=hand_label,relx=0.5,rely=0.2,anchor="s")
        
        sum_label = tk.Label(player_frame, font=font_text)
        sum_label.grid(row=1, column=0)
        
        return player_frame,name_label,hand_label,sum_label
    
    def create_widgets(self):
        self.game_frame = tk.Frame(self.root)

        self.bank_label = tk.Label(self.game_frame,font=("Arial",13))
        self.bank_label.grid(row = 0,sticky="e")

        self.dealer_frame,self.dealer_name_label,self.dealer_hand_label,self.dealer_sum_label = self.player_hand_frame_maker(self.game_frame,("Arial",12))
        self.dealer_frame.grid(row=1,column=0)

        self.player_frame,self.player_name_label,self.player_hand_label,self.player_sum_label = self.player_hand_frame_maker(self.game_frame,("Arial",12))
        self.player_frame.grid(row=3,column=0)

        self.others_frame = tk.Frame(self.game_frame)
        self.others_frame.grid(row=2, column=0)
        self.other_player_widgets = {}

        for player in self.game.players:
            widgets = self.player_hand_frame_maker(self.others_frame,("Arial", 12))
            self.other_player_widgets[player] = widgets

        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.pack(side="bottom",pady=5)

        self.status_label = tk.Label(self.controls_frame,font=("Arial",12))
        self.status_label.grid(row=0,column=0,columnspan=3)

        self.bet_20_button = tk.Button(self.controls_frame,text="20",command=lambda:self.place_bet(20),width=12)
        self.bet_50_button = tk.Button(self.controls_frame,text="50",command=lambda:self.place_bet(50),width=12)
        self.bet_100_button = tk.Button(self.controls_frame,text="100",command=lambda:self.place_bet(100),width=12)
        self.hit_button = tk.Button(self.controls_frame,text="Hit",command=self.hit,width=12)
        self.hit_button.grid(row=1,column=0)
        self.stand_button = tk.Button(self.controls_frame,text="Stand",command=self.stand,width=12)
        self.stand_button.grid(row=1,column=1)
        self.new_round_button = tk.Button(self.controls_frame,text="New round",command=self.start_round,width=12)
        self.new_round_button.grid(row=1,column=2)
        
        self.game_frame.pack()

    def place_bet(self,bet_amount):
        if self.round_over: return
        player = self.game.players[self.player_index]
        if player.get_state() != "UNDER": return
        if player.bank < bet_amount: return
    
        self.game.bet(player,bet_amount)
       
        self.show_turn()

    def get_unicode_string(self,card:Card):
        suits_unicode = {"spades": 0x1F0A0,"hearts":0x1F0B0,"diamonds": 0x1F0C0,"clubs": 0x1F0D0}

        unicode_suit = suits_unicode[card.suit]
        unicode_value = int(card.value)

        #remappar på unicodevärdena, lite annorlunda än mina kort värden
        match unicode_value:
            case 14: unicode_value = 1
            case 13: unicode_value = 14
            case 12: unicode_value = 13
        
        return chr(unicode_suit + unicode_value)

    def get_unicode_hand(self,hand:list[Card]):
        hand_unicode_string = ""
        for card in hand:
            hand_unicode_string+=self.get_unicode_string(card)
        return hand_unicode_string

    def display_player_turn(self,current_player):
        #display other players hands
        index = 0
        for player, widgets in self.other_player_widgets.items():
            frame, name_label, hand_label, sum_label = widgets
            
            #skip and delete frame of currend player
            if player is current_player:
                frame.grid_remove()
                continue

            name_label.config(text=f"{player.name}s hand")
            self.show_hand(hand_label, player.hand)
            sum_label.config(text=f"Card sum: {player.get_total_value()}")
            frame.grid(row=index // 4, column=index % 4)
            index+=1

        #display dealers hand
        card_back = "\U0001F0A0"
        self.dealer_name_label.config(text="Dealer hand")
        if self.dealer_revealed:
            self.show_hand(self.dealer_hand_label, self.game.dealer.hand)
            self.dealer_sum_label.config(text=f"Card sum: {self.game.dealer.get_total_value()}")
        else:
            self.show_hand(self.dealer_hand_label, self.game.dealer.hand[:1])
            visible_value = self.game.dealer.hand[0].value
            visible_value = 11 if visible_value == 14 else min(visible_value, 10)
            self.dealer_sum_label.config(text=f"Card sum: {visible_value} + ?")

        #display own hand
        self.bank_label.config(text=f"Bank: {current_player.bank_value}")
        self.player_name_label.config(text=f"{current_player.name}s hand")
        self.show_hand(self.player_hand_label, current_player.hand, ("Arial", 170))
        self.player_sum_label.config(text=f"Card sum: {current_player.get_total_value()}")

    def show_hand(self, hand_frame, hand, font_hand=("Arial", 120)):
        # Ta bort korten från förra visningen
        for widget in hand_frame.winfo_children():
            widget.destroy()

        for card in hand:
            tk.Label(hand_frame,text=self.get_unicode_string(card),font=font_hand).pack(side="left")
            

    def start_round(self):
        self.player_index = 0
        self.round_over = False
        self.dealer_revealed = False
        clear_players_hands(self.game.players + [self.game.dealer])
        self.game.deck = make_deck(NUM_OF_DECKS)
        self.new_round_button.config(state="disabled")

        try:
            self.game.give_card(self.game.dealer,2)
            for player in self.game.players:
                self.game.give_card(player,2)
        except EmptyDeckError:
            self.end_round("Not enough cards left. This round is cancelled.")
            return

        self.show_turn()

    def show_turn(self):
        player = self.game.players[self.player_index]
        status = player.get_state()
        self.display_player_turn(player)
        messages = {"UNDER":"Your turn","BUSTED":"Busted!","BLACKJACK":"Blackjack!","TWENTY_ONE":"21!"}
        self.status_label.config(text=f"{player.name}: {messages[status]}")
        self.hit_button.config(state="normal" if status == "UNDER" else "disabled")
        self.stand_button.config(state="normal",text="Stand" if status == "UNDER" else "Next player")

    def hit(self):
        if self.round_over: return
        player = self.game.players[self.player_index]
        if player.get_state() != "UNDER": return

        try:
            self.game.hit(player)
        except EmptyDeckError:
            self.end_round("Not enough cards left, this round is cancelled")
            return
        self.show_turn()

    def stand(self):
        if self.round_over: return
        if self.player_index + 1 < len(self.game.players):
            self.player_index += 1
            self.show_turn()
        else:
            self.dealer_turn()

    def dealer_turn(self):
        if self.round_over: return
        self.dealer_revealed = True
        self.hit_button.config(state="disabled")
        self.stand_button.config(state="disabled")
        self.status_label.config(text="Dealer's turn")
        self.display_player_turn(self.game.players[self.player_index])

        if any(player.get_state() != "BUSTED" for player in self.game.players) and self.game.dealer.get_total_value() < 17:
            self.root.after(DEALER_DELAY,self.dealer_hit)
            return

        winner = self.game.check_winner()
        if winner is None:
            self.end_round("It's a draw!")
        else:
            self.end_round(f"{winner.name} wins!")

    def dealer_hit(self):
        if self.round_over: return
        try:
            self.game.hit(self.game.dealer)
        except EmptyDeckError:
            self.end_round("Not enough cards left. This round is cancelled.")
            return
        self.dealer_turn()

    def end_round(self,text):
        self.round_over = True
        self.status_label.config(text=text)
        self.hit_button.config(state="disabled")
        self.stand_button.config(state="disabled")
        self.new_round_button.config(state="normal")
        if self.game.dealer.hand:
            self.display_player_turn(self.game.players[self.player_index])

    def run(self):
        self.root.mainloop()

def game_runner():

    gui = BlackjackGUI()

    amount = gui.ask_player_amount()
    players = gui.init_players(amount)

    game = Game(players,Player("dealer"))
    gui.start_game(game)
    gui.run()

game_runner()
