#include "logic.h"


void GameState::clearLastPlayedCards() { lastPlayedCards.clear(); }

void GameState::clearPlayerPassFlags() { 
    for (size_t i = 0; i < 4; ++i) {
        playerPassFlag[i] = !activePlayerFlag[i];
    }
}

int GameState::countPlayerCards(size_t playerId) {
    if (playerId < 0 || playerId > 3) { return 0; }
    return std::count(cards.begin(), cards.end(), playerId);
}

int GameState::numActivePlayers() {
    return std::accumulate(activePlayerFlag.begin(), activePlayerFlag.end(), 0);
}

int GameState::numPlayersPassed() {
    return std::accumulate(playerPassFlag.begin(), playerPassFlag.end(), 0);
}

void GameState::update(size_t playerId, std::vector<Card> &playedCards) {
    if (playedCards.empty()) { this->playerPassFlag[playerId] = true; }
    else{
        this->lastMovePlayerId = playerId;
        this->lastPlayedCards = playedCards;

        for (Card &card : playedCards) {
            this->cards[card.first % 13 + card.second * 13] = CARD_PLAYED;
        }

        if (countPlayerCards(playerId) == 0) {
            this->activePlayerFlag[playerId] = false;
            this->playerPassFlag[playerId] = true;
        }
    }
}


Card indexToCard(size_t cardIdx) {
    if (cardIdx < 0 || cardIdx > 51) { return CARD_NULL; }

    // nb: A and 2 are the highest cards unless they are 
    //     played as a low straight
    int value = cardIdx % 13;
    int suit = cardIdx / 13;
    if (value < 2) { value += 13; }

    return Card(value, suit);
}

Card valueOfPair(std::vector<Card> &cards) {
    if (cards.size() != 2) { return CARD_NULL; }
    return cards[0] > cards[1] ? cards[0] : cards[1];
}

Card valueOfTriplet(std::vector<Card> &cards) {
    if (cards.size() != 3) { return CARD_NULL; }

    for (int i = 1; i < 3; ++i) {
        if (cards[i].first != cards[i-1].first) { 
            return CARD_NULL; 
        }
    }

    return cards[2];
}

Card valueOfStraight(std::vector<Card> &cards) {
    if (cards.size() != 5) { return CARD_NULL; }
    std::sort(cards.begin(), cards.end());

    // Check for high straight
    for (size_t i = 1; i < 5; ++i) {
        if (cards[i].first != cards[i-1].first + 1) { break; }
        if (i == 4) { return cards[4]; }
    }

    // Check for low straight
    std::vector<Card> cardsCopy(cards);
    for (size_t i = 0; i < 5; ++i) {
        if (cardsCopy[i].first >= 13) { cardsCopy[i].first -= 13; }
    }
    std::sort(cardsCopy.begin(), cardsCopy.end());

    for (size_t i = 1; i < 5; ++i){
        if (cardsCopy[i].first != cardsCopy[i-1].first + 1) { break; }
        if (i == 4) { return cardsCopy[4]; }
    }
    
    return CARD_NULL;
}

Card valueOfFlush(std::vector<Card> &cards) {
    if (cards.size() != 5) { return CARD_NULL; }
    std::sort(cards.begin(), cards.end());

    for (size_t i = 1; i < 5; ++i) {
        if (cards[i].second != cards[i-1].second) { 
            return CARD_NULL; 
        }
    }

    return cards[4];
}

Card valueOfFullHouse(std::vector<Card> &cards) {
    if (cards.size() != 5) { return CARD_NULL; }
    std::sort(cards.begin(), cards.end());

    std::vector<Card> t1 = {cards[0], cards[1], cards[2]};
    bool c1 = cards[3].first == cards[4].first;

    std::vector<Card> t2 = {cards[2], cards[3], cards[4]};
    bool c2 = cards[0].first == cards[1].first;

    return std::max(
        c1 ? valueOfTriplet(t1) : CARD_NULL, 
        c2 ? valueOfTriplet(t2) : CARD_NULL
    );
}

Card valueOfFourOfAKind(std::vector<Card> &cards) {
    if (cards.size() != 5) { return CARD_NULL; }
    std::sort(cards.begin(), cards.end());

    // Check in {cards[0], cards[1], cards[2], cards[3]} 
    for (size_t i = 1; i < 4; ++i) {
        if (cards[i].first != cards[i-1].first) { break; }
        if (i == 3) { return cards[3]; }
    }

    // Check in {cards[1], cards[2], cards[3], cards[4]}
    for (size_t i = 2; i < 5; ++i) {
        if (cards[i].first != cards[i-1].first) { break; }
        if (i == 4) { return cards[4]; }
    }

    return CARD_NULL;
}

std::pair<int, Card> valueOfPack(std::vector<Card> &cards) {
    if (cards.size() != 5) { return {PACK_NULL, CARD_NULL}; }

    Card straight = valueOfStraight(cards);
    Card flush = valueOfFlush(cards);
    if (straight != CARD_NULL && flush != CARD_NULL) { return {PACK_STRAIGHT_FLUSH, straight}; }
    if (straight != CARD_NULL) { return {PACK_STRAIGHT, straight}; }
    if (flush != CARD_NULL) { return {PACK_FLUSH, flush}; }

    Card fourOfAKind = valueOfFourOfAKind(cards);
    if (fourOfAKind != CARD_NULL) { return {PACK_FOUR_OF_A_KIND, fourOfAKind}; }

    Card fullHouse = valueOfFullHouse(cards);
    if (fullHouse != CARD_NULL) { return {PACK_FULL_HOUSE, fullHouse}; }

    return {PACK_NULL, CARD_NULL};
}


void generateNOfAKind(
    size_t n,
    std::unordered_map<int, std::vector<Card>> &cardValueGroup, 
    std::vector<std::vector<Card>> &result
) {
    if (n == 0) { return; } 

    for (auto &valueGroup : cardValueGroup) {
        if (valueGroup.second.size() < n) { continue; }

        std::vector<std::vector<Card>> c = generateChooseK(valueGroup.second, n);
        result.insert(result.end(), c.begin(), c.end());
    }
}

void generateMovesPass(std::vector<Card> &cards, std::vector<Card> &lastPlayedCards, std::vector<std::vector<Card>> &moves) {
    if (lastPlayedCards.empty()) { return; }
    moves.push_back({});
}

void generateMovesSingle(std::vector<Card> &cards, std::vector<Card> &lastPlayedCards, std::vector<std::vector<Card>> &moves) {
    if (lastPlayedCards.size() > 1) { return; }
    Card lastPlayed = lastPlayedCards.empty() ? CARD_NULL : lastPlayedCards[0];

    for (Card &card : cards) {
        if (card > lastPlayed) {
            moves.push_back({card});
        }
    }
}

void generateMovesPair(
    std::vector<Card> &cards,
    std::vector<Card> &lastPlayedCards, 
    std::unordered_map<int, std::vector<Card>> &cardValueGroup,
    std::vector<std::vector<Card>> &moves
) {
    if (lastPlayedCards.size() != 2 && !lastPlayedCards.empty()) { return; }
    Card lastPlayed = lastPlayedCards.empty()? CARD_NULL : valueOfPair(lastPlayedCards);
    
    for (auto &valueGroup : cardValueGroup) {
        if (valueGroup.second.size() < 2) { continue; }
        if (valueGroup.first < lastPlayed.first) { continue; }

        std::vector<std::vector<Card>> c = generateChooseK(valueGroup.second, 2);
        moves.insert(moves.end(), c.begin(), c.end());
    }
}

void generateMovesStraight(
    int lastPlayedPackType,
    Card &lastPlayedPackValue,
    std::unordered_map<int, std::vector<Card>> &cardValueGroup,
    std::vector<std::vector<Card>> &moves
) {
    if (lastPlayedPackType > PACK_STRAIGHT) { return; }

    // nb: temporary map 0 (Ace) -> 13 (High Ace) and 1 (2) -> 14 (High 2)
    if (cardValueGroup.find(13) != cardValueGroup.end()) { 
        for (Card &card : cardValueGroup[13]) { cardValueGroup[0].push_back({0, card.second}); } 
    }
    if (cardValueGroup.find(14) != cardValueGroup.end()) { 
        for (Card &card : cardValueGroup[14]) { cardValueGroup[1].push_back({1, card.second}); }
    }

    std::vector<std::vector<Card>> straightValueGroup;

    for (size_t start = 0; start <= 10; ++start) {
        straightValueGroup.clear();

        // find 5 consecutive value group
        for (size_t v = start; v < start + 5; ++v) {
            if (cardValueGroup.find(v) != cardValueGroup.end()) {
                straightValueGroup.push_back(cardValueGroup[v]);
            } else {
                straightValueGroup.clear();
                break;
            }
        }

        // generate straight by computing the cartesian product
        if (straightValueGroup.size() == 5) {
            std::vector<std::vector<Card>> straights = generateCartesianProduct(straightValueGroup);

            for (std::vector<Card> &straight : straights) {
                Card straightValue = *std::max_element(straight.begin(), straight.end());
                if (straightValue > lastPlayedPackValue) { moves.push_back(straight); }
            }
        }
    }

    // remove temporary map
    if (cardValueGroup.find(0) != cardValueGroup.end()) { cardValueGroup.erase(0); }
    if (cardValueGroup.find(1) != cardValueGroup.end()) { cardValueGroup.erase(1); }
}

void generateMovesFlush(
    int lastPlayedPackType,
    Card &lastPlayedPackValue, 
    std::unordered_map<int, std::vector<Card>> &cardSuitGroup,
    std::vector<std::vector<Card>> &moves
) {
    // nb: straight flush will also be generated in this function
    std::pair<int, Card> lastPlayed = {lastPlayedPackType, lastPlayedPackValue};

    for (auto &suitGroup : cardSuitGroup) {
        if (suitGroup.second.size() < 5) { continue; }

        std::vector<std::vector<Card>> flushes = generateChooseK(suitGroup.second, 5);

        // case: last played is straight (or lower), we can play any flush
        if (lastPlayedPackType < PACK_FLUSH) {
            moves.insert(moves.end(), flushes.begin(), flushes.end());
            continue;
        }

        // case: last played is a flush with the same suit, we can only play flush of higher value 
        for (auto &flush : flushes) {
            auto packValue = valueOfPack(flush);
            if (packValue > lastPlayed) { moves.push_back(flush); }
        }
    }
}

void generateMovesFullHouse(
    int lastPlayedPackType,
    Card &lastPlayedPackValue,
    std::unordered_map<int, std::vector<Card>> &cardValueGroup,
    std::vector<std::vector<Card>> &moves
) {
    if (lastPlayedPackType > PACK_FULL_HOUSE) { return; }

    std::vector<std::vector<Card>> pairs;
    std::vector<std::vector<Card>> triplets;
    generateNOfAKind(2, cardValueGroup, pairs);
    generateNOfAKind(3, cardValueGroup, triplets);

    for (std::vector<Card> &triplet : triplets) {
        // case: last played is full house, we must have higher triplet
        if (lastPlayedPackType == PACK_FULL_HOUSE && triplet[0] < lastPlayedPackValue) { continue; } 

        for (std::vector<Card> &pair : pairs) {
            if (triplet[0].first != pair[0].first) {
                std::vector<Card> fullHouse(triplet);
                fullHouse.insert(fullHouse.end(), pair.begin(), pair.end());
                moves.push_back(fullHouse);
            }
        }
    }
}

void generateFourOfAKind(
    int lastPlayedPackType,
    Card &lastPlayedPackValue,
    std::unordered_map<int, std::vector<Card>> &cardValueGroup,
    std::vector<std::vector<Card>> &moves
) {
    if (lastPlayedPackType > PACK_FOUR_OF_A_KIND) { return; }

    for (auto &vGroupOuter : cardValueGroup) {
        if (vGroupOuter.second.size() != 4) { continue; }
        if (lastPlayedPackType == PACK_FOUR_OF_A_KIND && vGroupOuter.first < lastPlayedPackValue.first) { continue; }

        for (auto &vGroupInner : cardValueGroup) {
            if (vGroupInner.first == vGroupOuter.first) { continue; }

            for (Card &card : vGroupInner.second) {
                std::vector<Card> fourOfAKind(vGroupOuter.second);
                fourOfAKind.push_back(card);
                moves.push_back(fourOfAKind);
            }
        }
    }
}

void removeDuplicateMoves(std::vector<std::vector<Card>> &moves) {
    std::sort(moves.begin(), moves.end());
    moves.erase(std::unique(moves.begin(), moves.end()), moves.end());
}

void generateMovesPack(
    std::vector<Card> &cards,
    std::vector<Card> &lastPlayedCards,
    std::unordered_map<int, std::vector<Card>> &cardValueGroup,
    std::unordered_map<int, std::vector<Card>> &cardSuitGroup,
    std::vector<std::vector<Card>> &moves
) {
    auto lastPlayedPack = valueOfPack(lastPlayedCards);
    auto lastPlayedPackType = lastPlayedPack.first;
    auto lastPlayedPackValue = lastPlayedPack.second;
    if (lastPlayedPackType == PACK_NULL && !lastPlayedCards.empty()) { return; }

    generateMovesStraight(lastPlayedPackType, lastPlayedPackValue, cardValueGroup, moves);
    generateMovesFlush(lastPlayedPackType, lastPlayedPackValue, cardSuitGroup, moves);
    generateMovesFullHouse(lastPlayedPackType, lastPlayedPackValue, cardValueGroup, moves);
    generateFourOfAKind(lastPlayedPackType, lastPlayedPackValue, cardValueGroup, moves);

    // removeDuplicateMoves(moves);
}


std::vector<Card> getPlayerCardsInHand(size_t playerId, GameState state) {
    std::vector<Card> playerHand;
    if (playerId < 0 || playerId > 3) { return playerHand; }

    for (size_t i = 0; i < 52; ++i) {
        if (state.cards[i] == playerId) {
            playerHand.push_back(indexToCard(i));
        }
    }

    return playerHand;
}

std::unordered_map<int, std::vector<Card>> groupCardsByValue(std::vector<Card> &cards) {
    std::unordered_map<int, std::vector<Card>> valueGroup;

    for (Card &card : cards) {
        if (card.first < 0) { continue; }
        valueGroup[card.first].push_back(card);  // (Ace) [13], (2) [14] 
    }

    return valueGroup;
}

std::unordered_map<int, std::vector<Card>> groupCardsBySuit(std::vector<Card> &cards) {
    std::unordered_map<int, std::vector<Card>> suitGroup;

    for (Card &card : cards) {
        if (card.second < 0) { continue; }
        suitGroup[card.second].push_back(card);
    }

    return suitGroup;
}

std::vector<std::vector<Card>> generateCandidateMoves(size_t playerId, GameState state){
    std::vector<std::vector<Card>> moves;
    std::vector<Card> cardsInHand = getPlayerCardsInHand(playerId, state);

    std::unordered_map<int, std::vector<Card>> cardValueGroup = groupCardsByValue(cardsInHand);
    std::unordered_map<int, std::vector<Card>> cardSuitGroup = groupCardsBySuit(cardsInHand);

    generateMovesPass(cardsInHand, state.lastPlayedCards, moves);
    generateMovesSingle(cardsInHand, state.lastPlayedCards, moves);
    generateMovesPair(cardsInHand, state.lastPlayedCards, cardValueGroup, moves);
    generateMovesPack(cardsInHand, state.lastPlayedCards, cardValueGroup, cardSuitGroup, moves);

    return moves;
}