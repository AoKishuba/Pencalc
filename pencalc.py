#!/usr/bin/env python

"""Calculate required Kinetic Damage to penetrate a given armor configuration

Available functions:
armorcalc(ac, is_structural)
    takes a layer (or multiple layers) of armor and calculates the effective
    AC

kdcalc(ap, shell_angle)
    takes a layer of armor and calculates the KD required to penetrate it at a
    given AP and shell angle

"""

import math

# Store HP and AC for 4-metre beams of various materials.
ARMORSTATS = {
    'WOOD': (864, 8, True),
    'METAL': (1680, 40, True),
    'ALLOY': (1440, 35, True),
    'STONE': (1200, 16, True),
    'LEAD': (1440, 10, True),
    'HA': (6000, 60, True),
    'AIR': (0, 0, False)
}


class ArmorChunk:
    """Store stats for all layers of a chunk of armor."""

    def __init__(self) -> None:
        """Create a new ArmorChunk

        :return: None
        """

        self.layers = []
        self.KD_required = {}

    def add_layer(self, hp: int, ac: int, is_structural: bool = True) -> None:
        """Add a layer to the armor chunk

        :param hp: int
                   armor health.
        :param ac: int
                   armor class (called 'Armor' ingame).
        :param is_structural: bool
                              whether the armor contributes to layering.
        :return: None.
        """

        new_layer = {
            'hp': hp,
            'ac': ac,
            'is_structural': is_structural,
        }
        self.layers.append(new_layer)

    def armorcalc(self) -> None:
        """Calculate the effective AC for each layer of the chunk.
        Armor layering only applies if both layers are structural.  Call
        this before calling kdcalc.

        :return: None
        """

        for L in range(0, len(self.layers) - 1):
            current_layer = self.layers[L]
            next_layer = self.layers[L + 1]
            armor_boost = next_layer['ac'] * 0.2

            if (current_layer['is_structural'] and
                    next_layer['is_structural']):
                current_layer['ac'] += armor_boost

    def kdcalc(self, shell_angle: int = 0) -> None:
        """Calculate the KD required to penetrate the armor chunk at
        every useful AP value.  Call this only after first calling
        armorcalc.

        :param shell_angle: int
                            angle at which the shell strikes the armor,
                            in degrees.  0 is a perpendicular hit; 90 is
                            parallel.
        :return: None
        """

        # Calculate maximum useful AP.
        layer_ac = []
        for L in range(0, len(self.layers) - 1):
            layer_ac.append(self.layers[L]['ac'])

        max_ap = max(layer_ac)

        # Calculate required KD for each potential AP.
        shell_ap = 0.1
        while shell_ap <= max_ap:
            chunk_effective_hp = 0
            for L in range(0, len(self.layers) - 1):
                ac_multiplier = (self.layers[L]['ac'] / shell_ap)
                angle_multiplier = (1 - math.cos(shell_angle))
                layer_hp = (self.layers[L]['hp']
                            * ac_multiplier
                            * angle_multiplier)
                chunk_effective_hp += layer_hp
                chunk_effective_hp = round(chunk_effective_hp)
            self.KD_required[shell_ap] = chunk_effective_hp
            shell_ap += 0.1
            shell_ap = round(shell_ap, 1)

    def print_chunk(self) -> None:
        """Print the list of KD required for each AP value.

        :return: None
        """
        for ap in self.KD_required.keys():
            print(ap, self.KD_required[ap])


if __name__ == '__main__':
    """Gather armor configuration and shot angle from user input, then 
    calculate required KD at every possible useful AP.

    """

    test_chunk = ArmorChunk()
    while input("Do you want to add more layers?  y/n\n").upper() == "Y":
        layer_material = input("Enter layer material (not case-sensitive"
                               "):\nAlloy\nHA\nLead\nMetal\nStone\nWood\n"
                               "Air\n").upper()
        layer_count = int(input("How many consecutive layers of this "
                                "material?\n"))
        for i in range(0, layer_count):
            test_chunk.add_layer(hp=ARMORSTATS[layer_material][0],
                                 ac=ARMORSTATS[layer_material][1],
                                 is_structural=ARMORSTATS[layer_material][2])

    shell_angle = int(input("Enter shell angle in degrees, 0-90.\n"))

    test_chunk.armorcalc()

    test_chunk.kdcalc(shell_angle)
    test_chunk.print_chunk()
