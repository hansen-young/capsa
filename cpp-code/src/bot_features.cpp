#include "bot_features.h"


std::array<float, 110> createBotFeatures1(size_t playerId, GameState state) {
    /*
    Feature Definitions:
    - 0-103 : Card ownership (2 values per card, 52 cards)
      - 01 : Card in other player's hand
      - 10 : Card in player's hand
      - 11 : Card is played
    - 104-106 : Opponent's hand size
    - 107-109 : Opponent's skip flag
    */

    std::array<float, 110> features; features.fill(0.0f);
    std::array<int, 4> cardCount; cardCount.fill(0);
    size_t fi = 0;
    size_t pi = 0;

    // Card ownership
    for (uint8_t card : state.cards) {
        if (card == CARD_PLAYED) {
            features[fi++] = 1.0f;
            features[fi++] = 1.0f;
        } else if (card == playerId) {
            features[fi++] = 1.0f;
            features[fi++] = 0.0f;
            cardCount[card]++;
        } else {
            features[fi++] = 0.0f;
            features[fi++] = 1.0f;
            cardCount[card]++;
        }
    }

    // Opponent's hand size
    pi = 0; fi = 104;
    for (size_t i = 0; i < 4; ++i) {
        if (i != playerId) { features[fi++] = (float) cardCount[pi] / 13.0f; }
        pi++;
    }

    // Opponent's skip flag
    pi = 0; fi = 107;
    for (size_t i = 0; i < 4; ++i) {
        if (i != playerId) { features[fi++] = state.playerPassFlag[pi] ? 1.0f : 0.0f; }
        pi++;
    }

    return features;
}
