lazy import random

class Card():

    def __init__(self,suit,value):
        self.suit = suit
        self.value = value
        

    def draw(self):
        print(f"{self.suit} {self.value}")

class Player():

    hand = []

    def __init__(self,name:str):
        self.name = name

def draw_card()->tuple:

    suit = random.randint(1,4)
    value = random.randint(2,14)

    return Card(suit,value)

def give_card(recipient,amount = 1):

    random_card = draw_card()
    recipient.hand.append(random_card)

def print_start():
    # print("Welcome to Blackjack!")


def runner():
    give_card()

    

vilmer = Player("vilmer")
print("Welcome to Blackajck! Draw 1 card please")
for value in range(1, 14):
    print(value)