#!/usr/bin/env python
# coding: utf-8
import os
__all__ = ["isotope_difference_table"]


isotope_difference_table = list()

with open('AtomicWeightsAndIsotopicCompNIST2019.txt', "r") as file:
    content = file.readlines()
    isotope_number = []
    isotope_mass_full = []
    isotope_mass = []
    atomic_symbol = []
    mass_number = []
    isotope_name = []
    n = 0
    o = n+1
    p = n+2
    m = n+3
    while n < len(content):
        isotope_number.append(content[n])
        isotope_mass_full.append(content[m])
        atomic_symbol.append(content[o])
        mass_number.append(content[p])
        n = n+8
        o = n+1
        p = n+2
        m = n+3
    isotope_number = [w.replace("Atomic Number = ", "")
                      for w in isotope_number]
    isotope_number = [w.replace("\n", "") for w in isotope_number]
    isotope_mass_full = [w.replace("Relative Atomic Mass = ", "")
                         for w in isotope_mass_full]
    atomic_symbol = [w.replace("Atomic Symbol = ", "") for w in atomic_symbol]
    atomic_symbol = [w.replace("\n", "") for w in atomic_symbol]
    mass_number = [w.replace("Mass Number = ", "") for w in mass_number]
    mass_number = [w.replace("\n", "") for w in mass_number]

    isotope_mass_full = [g.split("(", 1) for g in isotope_mass_full]
    n = 0
    while n < len(isotope_mass_full):
        isotope_mass.append(isotope_mass_full[n][0])
        n = n+1

    for i, b in enumerate(isotope_mass):
        isotope_mass[i] = float(isotope_mass[i])
        isotope_number[i] = int(isotope_number[i])

    for i in range(0, len(isotope_mass)):
        isotope_name.append(mass_number[i] + atomic_symbol[i])

    isotope_table = list(zip(isotope_number, isotope_mass, isotope_name))

    isotope_difference_name = []
    isotope_difference_value = []
    for i in range(0, len(isotope_table)):
        for j in range(0, len(isotope_table)):
            calc = isotope_table[i][1] - isotope_table[j][1]
            if calc > 0.1:
                isotope_difference_name.append(
                    isotope_table[i][2] + '-' + isotope_table[j][2])
                isotope_difference_value.append(calc)

    isotope_difference_table = list(
        zip(isotope_difference_name, isotope_difference_value))


def find_split(requested_split=1.003355, tolerance=0.0001):
    """ Find a mass gap between two isotopes.

    Args:
        requested_split (float): the gap between isotopes' masses
        tolerance (float): the tolerance to find the candidates

    Returns:
        A list of candidates and min index
    """
    candidates = list()
    min_idx = 0

    for name, value in isotope_difference_table:
        if value - tolerance < requested_split < value + tolerance:
            candidates.append((name, value - requested_split))

    if len(candidates) > 0:
        # look for min value
        minval = abs(candidates[0][1])
        min_idx = 0
        if len(candidates) > 1:
            for i, (_, value) in enumerate(candidates[1:]):
                if abs(value) < minval:
                    minval = abs(value)
                    min_idx = i+1

    return candidates, min_idx
