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

    GameState() = default;
    GameState(const GameState &other)
        : cards(other.cards),
          lastMovePlayerId(other.lastMovePlayerId),
          lastPlayedCards(other.lastPlayedCards),
          activePlayerFlag(other.activePlayerFlag),
          playerPassFlag(other.playerPassFlag) {}
    
    GameState &operator=(const GameState &other) {
        if (this != &other) {
            cards = other.cards;
            lastMovePlayerId = other.lastMovePlayerId;
            lastPlayedCards = other.lastPlayedCards;
            activePlayerFlag = other.activePlayerFlag;
            playerPassFlag = other.playerPassFlag;
        }
        return *this;
    }

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
std::pair<int, Card> valueOfPack(std::vector<Card> &cards);


void generateNOfAKind(size_t n, std::unordered_map<int, std::vector<Card>> &cardValueGroup, std::vector<std::vector<Card>> &result);
void generateMovesPass(std::vector<Card> &cards, std::vector<Card> &lastPlayedCards, std::vector<std::vector<Card>> &moves);
void generateMovesSingle(std::vector<Card> &cards, std::vector<Card> &lastPlayedCards, std::vector<std::vector<Card>> &moves);
void generateMovesPair(std::vector<Card> &cards, 
                       std::vector<Card> &lastPlayedCards, 
                       std::unordered_map<int, std::vector<Card>> &cardValueGroup,
                       std::vector<std::vector<Card>> &moves);
void generateMovesStraight(int lastPlayedPackType, 
                           Card &lastPlayedPackValue, 
                           std::unordered_map<int, std::vector<Card>> &cardValueGroup,
                           std::vector<std::vector<Card>> &moves);
void generateMovesFlush(int lastPlayedPackType,
                        Card &lastPlayedPackValue, 
                        std::unordered_map<int, std::vector<Card>> &cardSuitGroup,
                        std::vector<std::vector<Card>> &moves);
void generateMovesFullHouse(int lastPlayedPackType,
                            Card &lastPlayedPackValue,
                            std::unordered_map<int, std::vector<Card>> &cardValueGroup,
                            std::vector<std::vector<Card>> &moves);
void generateFourOfAKind(int lastPlayedPackType,
                         Card &lastPlayedPackValue,
                         std::unordered_map<int, std::vector<Card>> &cardValueGroup,
                         std::vector<std::vector<Card>> &moves);
void generateMovesPack(std::vector<Card> &cards,
                       std::vector<Card> &lastPlayedCards,
                       std::unordered_map<int, std::vector<Card>> &cardValueGroup,
                       std::unordered_map<int, std::vector<Card>> &cardSuitGroup,
                       std::vector<std::vector<Card>> &moves);

std::vector<Card> getPlayerCardsInHand(size_t playerId, GameState state);
std::unordered_map<int, std::vector<Card>> groupCardsByValue(std::vector<Card> &cards);
std::unordered_map<int, std::vector<Card>> groupCardsBySuit(std::vector<Card> &cards);

std::vector<std::vector<Card>> generateCandidateMoves(size_t playerId, GameState state);
GameState copyGameState(const GameState &state);
GameState simulateMove(size_t playerId, GameState state, std::vector<Card> &playedCards);

#endif // LOGIC_H