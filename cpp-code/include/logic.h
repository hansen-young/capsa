#ifndef LOGIC_H
#define LOGIC_H

#include <algorithm>
#include <array>
#include <iostream>
#include <unordered_map>
#include <numeric>
#include <vector>
#include "utils.h"

#define Card std::pair<int, int>  // <value, suit>

constexpr int CARD_PLAYED = 4;
constexpr Card CARD_NULL = Card(-1, -1);

constexpr int PACK_NULL = 0;
constexpr int PACK_STRAIGHT = 1;
constexpr int PACK_FLUSH = 2;
constexpr int PACK_FULL_HOUSE = 3;
constexpr int PACK_FOUR_OF_A_KIND = 4;
constexpr int PACK_STRAIGHT_FLUSH = 5;


struct GameState {
    std::array<uint8_t, 52> cards;
    // 0 - 3 card is in player's (1 - 4) hand
    // 4     card is played

    int lastMovePlayerId = -1;
    std::vector<Card> lastPlayedCards;
    std::array<bool, 4> activePlayerFlag = {true, true, true, true};
    std::array<bool, 4> playerPassFlag = {false, false, false, false};

    void clearLastPlayedCards();
    void clearPlayerPassFlags();
    int countPlayerCards(size_t playerId);
    int numActivePlayers();
    int numPlayersPassed();
    void update(size_t playerId, std::vector<Card> &playedCards);
};

Card indexToCard(size_t cardIdx);
Card valueOfPair(std::vector<Card> &cards);
Card valueOfTriplet(std::vector<Card> &cards);
Card valueOfStraight(std::vector<Card> &cards);
Card valueOfFlush(std::vector<Card> &cards);
Card valueOfFullHouse(std::vector<Card> &cards);
Card valueOfFourOfAKind(std::vector<Card> &cards);
std::vector<std::vector<Card>> generateCandidateMoves(size_t playerId, GameState state);

#endif // LOGIC_H