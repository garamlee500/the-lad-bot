import math
import cmath
class XpCalculator:

    # https://github.com/NKrvavica/fqs/blob/master/fqs.py
    # Credit to github.com/Nkravica
    # This code is identical to single_cubic_one()
    def solve_cubic(self, a0, b0, c0, d0):

        a, b, c = b0 / a0, c0 / a0, d0 / a0

        third = 1. / 3.
        a13 = a * third
        a2 = a13 * a13

        f = third * b - a2
        g = a13 * (2 * a2 - b) + c
        h = 0.25 * g * g + f * f * f

        def cubic_root(x):
            if x.real >= 0:
                return x ** third
            else:
                return -(-x) ** third

        if f == g == h == 0:
            return -cubic_root(c)

        elif h <= 0:
            j = math.sqrt(-f)
            k = math.acos(-0.5 * g / (j * j * j))
            m = math.cos(third * k)
            return 2 * j * m - a13

        else:
            sqrt_h = cmath.sqrt(h)
            S = cubic_root(-0.5 * g + sqrt_h)
            U = cubic_root(-0.5 * g - sqrt_h)
            S_plus_U = S + U
            return S_plus_U - a13


    def calculate_current_level(self, current_xp):

        # Normally cubic is in form
        # xp_formula = xp
        # Take away xp from both sides and solve

        # Convert complex to real solution (there is always only 1 solution so this approach is fine
        # .real just converts complex to float as there are no imaginary parts of the single solution

        # If level is a float, give level under it as there are no decimal levels
        return math.floor(self.solve_cubic(5/3, 22.5, 455/6, current_xp * -1).real)

    def calculate_xp_for_level(self, level):
        # Adaptation of MEE6 formula, returns same xp numbers
        # Can calculate xp levels with just a given level number
        level_cubed = level ** 3
        level_squared = level ** 2

        # The formula for xp is 5/3 x^3 + 45/2 x^2 + 455/6 x
        xp = ((10) * level_cubed + (135) * level_squared + (455) * level)/6

        # Round answer to negate rounding errors
        return round(xp)