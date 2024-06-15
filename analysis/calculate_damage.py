import random

def calculate_damage(bp, A, D, crit, level, stab, effective):
    crit_boost = 2 if crit else 1
    if A > 255 or D > 255:
        A = A // 4
        D = D // 4
    damage = ((((2*level*crit_boost)//5+2)*bp*A)//D) // 50 + 2
    if stab:
        damage += damage // 2
    rng = random.randint(217,255)
    if effective > 0:
        return (damage * effective * rng) // 255
    else:
        return (damage // (-effective) * rng) // 255

if __name__ == "__main__":
    print(calculate_damage(
        120, 160, 92, True, 70, True, 1
    ))
