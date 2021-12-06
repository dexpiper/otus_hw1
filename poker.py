#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------
# Реализуйте функцию best_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. У каждой карты есть масть(suit) и
# ранг(rank)
# Масти: трефы(clubs, C), пики(spades, S), червы(hearts, H), бубны(diamonds, D)
# Ранги: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), валет (jack, J), дама (queen, Q),
# король (king, K), туз (ace, A)
# Например: AS - туз пик (ace of spades), TH - дестяка черв (ten of hearts),
# 3C - тройка треф (three of clubs)

# Задание со *
# Реализуйте функцию best_wild_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. Кроме прочего в данном варианте "рука"
# может включать джокера. Джокеры могут заменить карту любой
# масти и ранга того же цвета, в колоде два джокерва.
# Черный джокер '?B' может быть использован в качестве треф
# или пик любого ранга, красный джокер '?R' - в качестве черв и бубен
# любого ранга.

# Одна функция уже реализована, сигнатуры и описания других даны.
# Вам наверняка пригодится itertools.
# Можно свободно определять свои функции и т.п.
# -----------------
from collections import Counter
from itertools import combinations


class Card:

    # словарь перевода ranks в натуральные числа от 2 до 13
    rankdict = dict(
        zip(
            ([str(el) for el in range(2, 10)] + 'T J Q K A'.split()),
            range(2, 14)
        )
    )

    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit
        self.ranknum = self._rank_as_number()

    def _rank_as_number(self) -> int:
        return Card.rankdict[self.rank]


def get_cards(hand):
    '''
    Возвращает "руку" как набор объектов
    '''
    cards = [Card(rank=card[0], suit=card[1]) for card in hand]
    return cards


def hand_rank(hand):
    """Возвращает значение определяющее ранг 'руки'"""
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):
        return (8, max(ranks))
    elif kind(4, ranks):
        return (7, kind(4, ranks), kind(1, ranks))
    elif kind(3, ranks) and kind(2, ranks):
        return (6, kind(3, ranks), kind(2, ranks))
    elif flush(hand):
        return (5, ranks)
    elif straight(ranks):
        return (4, max(ranks))
    elif kind(3, ranks):
        return (3, kind(3, ranks), ranks)
    elif two_pair(ranks):
        return (2, two_pair(ranks), ranks)
    elif kind(2, ranks):
        return (1, kind(2, ranks), ranks)
    else:
        return (0, ranks)


def card_ranks(hand) -> list[int]:
    """Возвращает список рангов (его числовой эквивалент),
    отсортированный от большего к меньшему"""
    cards = get_cards(hand)
    return sorted([card.ranknum for card in cards], reverse=True)


def flush(hand) -> bool:
    """Возвращает True, если все карты одной масти"""
    cards = get_cards(hand)
    suits = [card.suit for card in cards]
    return True if len(set(suits)) == 1 else False


def straight(ranks) -> bool:
    """Возвращает True, если отсортированные ранги формируют последовательность
    5ти, где у 5ти карт ранги идут по порядку (стрит)"""
    bag = []
    for i, rank in enumerate(sorted(ranks)):
        if i == 0:
            bag.append(rank)
            continue
        if rank - bag[i - 1] == 1:
            bag.append(rank)
        else:
            break
    return False if len(bag) < 5 else True


def kind(n, ranks):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    counter = dict(Counter(ranks))
    for rank, count in counter.items():
        if count == n:
            return rank
    return


def two_pair(ranks):
    """Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""
    first = kind(2, ranks)
    if first:
        [ranks.remove(first) for _ in range(2)]
        second = kind(2, ranks)
        if second:
            return first, second
    return


def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    i = iter(combinations(hand, 5))
    best_rank = 0, 0, 0
    best_combination = None
    for combination in i:
        current_rank = hand_rank(combination)
        if compare(current_rank, best_rank):
            best_rank = current_rank
            best_combination = combination
    return best_combination


def compare(current_rank, best_rank):
    for i, current in enumerate(current_rank):
        try:
            if current > best_rank[i]:
                return True
            elif current < best_rank[i]:
                return False
        except TypeError:
            if all(
                [
                    isinstance(current, list),
                    isinstance(best_rank[i], list)
                ]
            ):
                for j, el in enumerate(current):
                    if el > best_rank[i][j]:
                        return True
                    elif el < best_rank[i][j]:
                        return False
                else:
                    return False
        except IndexError:
            raise


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    return


def jocker_in(hand):
    return any([True if '?' in el else False for el in hand])


def test_best_hand():
    assert (sorted(best_hand("6C 7C 8C 9C TC 5C JS".split()))
            == ['6C', '7C', '8C', '9C', 'TC'])
    assert (sorted(best_hand("TD TC TH 7C 7D 8C 8S".split()))
            == ['8C', '8S', 'TC', 'TD', 'TH'])
    assert (sorted(best_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print('OK')


def test_best_wild_hand():
    print("test_best_wild_hand...")
    assert (sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))
            == ['7C', '8C', '9C', 'JC', 'TC'])
    assert (sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split()))
            == ['7C', 'TC', 'TD', 'TH', 'TS'])
    assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print('OK')


if __name__ == '__main__':
    test_best_hand()
    test_best_wild_hand()
