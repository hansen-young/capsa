#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
#include "logic.h"
#include "bot_features.h"

namespace py = pybind11;

PYBIND11_MODULE(c_utils, m) {
    py::class_<GameState>(m, "GameState")
        .def(py::init<>())
        .def("clearLastPlayedCards", &GameState::clearLastPlayedCards)
        .def("clearPlayerPassFlags", &GameState::clearPlayerPassFlags)
        .def("countPlayerCards", &GameState::countPlayerCards)
        .def("numActivePlayers", &GameState::numActivePlayers)
        .def("numPlayersPassed", &GameState::numPlayersPassed)
        .def("update", &GameState::update)
        .def_readwrite("cards", &GameState::cards)
        .def_readwrite("lastMovePlayerId", &GameState::lastMovePlayerId)
        .def_readwrite("lastPlayedCards", &GameState::lastPlayedCards)
        .def_readwrite("activePlayerFlag", &GameState::activePlayerFlag)
        .def_readwrite("playerPassFlag", &GameState::playerPassFlag);

    m.def("valueOfPack", &valueOfPack);
    m.def("generateCandidateMoves", &generateCandidateMoves);
    m.def("copyGameState", &copyGameState, py::return_value_policy::copy);
    m.def("simulateMove", &simulateMove);
    m.def("createBotFeatures1", &createBotFeatures1);
}
