import csv
import math
from enum import Enum


type_conversion = {
        "Normal": 1,
        "Fire": 2,
        "Water": 3,
        "Electric": 4,
        "Grass": 5,
        "Ice": 6,
        "Fighting": 7,
        "Poison": 8,
        "Ground": 9,
        "Flying": 10,
        "Psychic": 11,
        "Bug": 12,
        "Rock": 13,
        "Ghost": 14}

type_chart = {}
with open('analysis/type_chart.csv') as type_file:
    chart = csv.DictReader(type_file)
    for row in chart:
        type_chart[row["Attacking"]] = row

def calculate_type_effectiveness(atk_type: str, type1: str, type2: str) -> int:
    row = type_chart[atk_type]
    combination = float(row[type1])
    if type2 is not None:
        combination *= float(row[type2])
    if combination == 0:
        return 0
    effective = int(math.log2(combination))
    if effective == 0:
        effective +=1 
    else:
        effective *= 2
    return effective


if __name__ == "__main__":
    print(calculate_type_effectiveness("Electric", "Ground", "Flying"))
    print(calculate_type_effectiveness("Electric", "Grass", "Electric"))
    print(calculate_type_effectiveness("Electric", "Grass", "Normal"))
    print(calculate_type_effectiveness("Electric", "Fighting", "Normal"))
    print(calculate_type_effectiveness("Electric", "Grass", "Flying"))
    print(calculate_type_effectiveness("Electric", "Water", None))
    print(calculate_type_effectiveness("Electric", "Water", "Flying"))
