#ifndef UTILS_H
#define UTILS_H

#include <vector>

template <typename T>
void chooseKHelper(std::vector<T> &vector, size_t k, size_t start, std::vector<T> &current, std::vector<std::vector<T>> &result) {
    if (current.size() == k) {
        result.push_back(current);
        return;
    }

    for (size_t i = start; i < vector.size(); ++i) {
        current.push_back(vector[i]);
        chooseKHelper(vector, k, i + 1, current, result);
        current.pop_back();
    }
}

template <typename T>
std::vector<std::vector<T>> generateChooseK(std::vector<T> &vector, size_t k) {
    std::vector<std::vector<T>> result;
    std::vector<T> current;
    chooseKHelper(vector, k, 0, current, result);
    return result;
}


template <typename T>
void cartesianProductHelper(const std::vector<std::vector<T>> &groups,
                            size_t index,
                            std::vector<T> &current,
                            std::vector<std::vector<T>> &result) {
    if (index == groups.size()) {
        result.push_back(current);
        return;
    }

    for (const T &elem : groups[index]) {
        current.push_back(elem);
        cartesianProductHelper(groups, index + 1, current, result);
        current.pop_back();
    }
}

template <typename T>
std::vector<std::vector<T>> generateCartesianProduct(const std::vector<std::vector<T>> &groups) {
    std::vector<std::vector<T>> result;
    std::vector<T> current;
    cartesianProductHelper(groups, 0, current, result);
    return result;
}


#endif // UTILS_H