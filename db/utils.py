from enum import StrEnum


class StatsEnum(StrEnum):
    HUNTING = "hunting"
    AGILITY = "agility"
    HEARING = "hearing"
    SMELL = "smell"
    SIGHT = "sight"
    SPEED = "speed"
    STAMINA = "stamina"
    STRENGTH = "strength"
    COMBAT = "combat"
    HERBALISM = "herbalism"
    HEALING = "healing"
    FAITH = "faith"


class PreyStats(StrEnum):
    speed = "speed"
    stamina = "stamina"
    sight = "sight"
    hearing = "hearing"
    smell = "smell"
    agility = "agility"
