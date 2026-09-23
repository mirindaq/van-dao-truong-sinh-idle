from app.core.game_rules import GameRules

SPECIES = (
    ("thanh_xa", "Thanh Xà", "pets/thanh_xa"),
    ("hoa_ho", "Hỏa Hồ", "pets/hoa_ho"),
    ("van_tuoc", "Vân Tước", "pets/van_tuoc"),
)


def pet_definitions(rules: GameRules) -> list[dict]:
    return [
        dict(
            key=key,
            name=name,
            asset_key=asset_key,
            combat_bonus=rules.pet_rules[key].combat_bonus,
            cultivation_factor=rules.pet_rules[key].cultivation_factor,
            cultivation_flat_per_minute=rules.pet_rules[key].cultivation_flat_per_minute,
        )
        for key, name, asset_key in SPECIES
    ]
