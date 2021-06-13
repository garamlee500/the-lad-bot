class XpCalculator:
    def __init__(self):
        self.xp_levels = [0,100]


        # Calculate all xp levels up to max
        while self.xp_levels[-1] < 9.3e18:
            current_level = (len(self.xp_levels) - 1)
            current_level_squared = current_level ** 2

            # Formula is 5 * (lvl ^ 2) + (50 * lvl) + 100 - xp
            self.xp_levels.append(5 * current_level_squared + 50 * current_level + 100 + self.xp_levels[-1])


    def calculate_current_level(self, current_xp):

        current_level_number = 0

        # Search through list with a given xp to find level number
        for i in range(len(self.xp_levels)):
            # Increment level number
            current_level_number = i

            # If the level above it has more xp than the actual level - stop searching
            if self.xp_levels[i + 1] > current_xp:
                break

        return current_level_number
