from dataclasses import dataclass

from app.core.game_rules import GameRules, game_rules
from app.game.data.items import HERB_KEY


LINH_MACH_WEAPON = "items/spirit_vein_sword"
COMMON_WEAPON = "items/bamboo_sword"


@dataclass(frozen=True)
class JourneyDefinition:
    key: str
    name: str
    minutes: int
    enemy: str
    item_key: str
    item_quantity: int


def journey_definitions(rules: GameRules = game_rules) -> dict[str, JourneyDefinition]:
    return {
        "hau_son": JourneyDefinition("hau_son", "Hậu Sơn", rules.journey_hau_son_minutes, "Sơn Miêu", HERB_KEY, rules.journey_material_quantity),
        "ngoai_vi": JourneyDefinition("ngoai_vi", "Ngoại Vi", rules.journey_ngoai_vi_minutes, "Độc Phong", COMMON_WEAPON, 1),
        "linh_mach": JourneyDefinition("linh_mach", "Linh Mạch", rules.journey_linh_mach_minutes, "Linh Xà", LINH_MACH_WEAPON, 1),
    }
