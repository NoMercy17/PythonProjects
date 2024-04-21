import sys, random 

# Set constants
HEARTS=chr(9829) # Character for '♥'
DIAMONDS=chr(9838) # Character for '♦️'
SPADES=chr(9824) # Character for '♠️'
CLUBS=chr(9827) # Character for '♣️'
BACKSIDE='backside'

print("Welcome to BlacJack!")
money=5000

# Get bet function 
def get_bet(maxBet):
    """Ask the player how much money they want to bet for this round"""
    while True:
        print("How much do you bet? (1-{} or QUIT)".format(maxBet))
        bet=input('> ').upper().strip() # strip  any leading/trailing whitespace
        if bet=="QUIT":
            print("Thanks for playing!")
            sys.exit()
        if not bet.isdecimal():
            continue
        bet=int(bet)
        if bet>=1 and bet<=maxBet:
            return bet


# Get deck

def get_deck():
    """Return a list of tuples (rank, suit) for all 52 cards"""
    deck=[]
    for suit in (HEARTS, DIAMONDS, SPADES, CLUBS):
        for rank in range(2,11): #2-10
            # add the numbered cards
            deck.append((str(rank),suit))
        for rank in ('J','Q','K','A'):
            # add the rest of the cards
            deck.append((rank,suit))

    random.shuffle(deck)
    return deck

# Display cards

def display_cards(cards):
    """Display all the cards in the card list"""
    rows=['', '', '', '', '']
    for card in cards:
        rows[0]+=' ___ '
        if card==BACKSIDE:
            rows[1]+='|## | '
            rows[2]+='|###| '
            rows[3]+='|_##| '
        else:
            rank, suit=card
            rows[1]+='|{} |'.format(rank.ljust(2)) # ljust is gonna put space if the value is just 1-9
            rows[2]+='| {} |'.format(suit)
            rows[3]+='|_{}|'.format(rank.rjust(2, '_'))
    for row in rows:
        print(row)


# Get values from players
def get_hand_values(cards):
    """Return the value of cards"""
    total=0
    number_aces=0
    # Adding the non ace cards
    for card in cards:
        rank=card[0]
        if rank=='A':
            number_aces += 1
        elif rank in ('K','Q','J'):
            total+=10
        else:
            total += int(rank)
    total += number_aces # we add the +1, +2 here for A
    for i in range(number_aces):
        # If another 10 can be added without busting
        if total+10 <=21:
            total += 10 # here we add the rest 10 from A
    return total


# Display hands
def display_hands(player_hand, dealer_hand, show_dealer_hand):
    """Show player's and dealer's hand"""
    print() # Black line for separations
    if show_dealer_hand:
        print("DEALER",get_hand_values(dealer_hand))
        display_cards(dealer_hand)
    else:
        print("DEALER: ???")
        # Hide dealer's first card
        display_cards([BACKSIDE]  + dealer_hand[1:]) # we put backside as first and then going til the end
    # Show the player's cards
    print("PLAYER: ",get_hand_values(player_hand))
    display_cards(player_hand)


# Get move

def get_move(player_hand, money):
    """Ask the player for their move, return H, S or D"""
    while True:
        moves=["(H)it", "(S)tand"]
        if len(player_hand)==2 and money > 0:
            moves.append( "(D)ouble down")
        # Ask the player the move, by showing the options
        moves_prompt=', '.join(moves) +' >'
        move=input(moves_prompt).upper()
        if   move in ('H','S'):
            return move
        if move=='D' and "(D)ouble down" in moves: # we need  to check that double is available before playing it
            return move

#main program
while True:
    # Check if player has run out of money
    if money<=0:
        print("It is good that you  weren't playing with real money!")
        print("Thanks for playing!")
        sys.exit() #We terminate the program
    # ASk player to enter their bet
    print("Money: ",money)

    # Get bet
    bet=get_bet(money)

    # Get deck
    deck = get_deck()

    # Give the dealer and player 2 cards from deck
    dealer_hand=[deck.pop(), deck.pop()]
    player_hand=[deck.pop(), deck.pop()]

    # Player's actions
    print("Bet: ",bet)
    while True:
        display_hands(dealer_hand, player_hand, False) # we need False so that the first card is not shown for Deler
        print()
        if get_hand_values(player_hand) > 21:
            break
        # Get player's move
        move=get_move(player_hand, money-bet)
        if move=='D':
            additional_bet=get_bet(min(bet, (money-bet)))
            bet+=additional_bet
            print("Bet increased to {}".format(bet))
            print("Bet: ",bet)
        if move in ('H','P'):
            new_card=deck.pop()
            rank, suit =new_card
            print(f"You drew a {rank} of {suit}.")
            player_hand.append(new_card)
        # Check if player has busted
            if get_hand_values(player_hand) > 21:
                continue
        if move=='S':
            # Stop player's turn 
            break


    # Dealer's actions
    if get_hand_values(dealer_hand) <= 21:
        while get_hand_values(dealer_hand) < 17: 
            # The dealer hits
            print("The dealer hits...")
            dealer_hand.append(deck.pop())
            display_hands(dealer_hand, player_hand, False)
            if get_hand_values(dealer_hand) > 21:
                break
            input("Press enter to continue...")
            print("\n\n")
    display_hands(player_hand, dealer_hand, True)
    player_value=get_hand_values(player_hand)
    dealer_value=get_hand_values(dealer_hand)
    # Handle the player won, lost or draw
    if dealer_value > 21:
        print(f"Dealer bust! You win ${bet}")
        money+=bet
    elif player_value > 21 or dealer_value > player_value:
        print("You lost")
        money-=bet
    elif player_value > dealer_value:
        print(f"You win ${bet}")
        money+=bet
    elif player_value== dealer_value:
        print("It is a draw, the bet is returned to you! ")
    input("Press enter to continue...")
    print('\n')
