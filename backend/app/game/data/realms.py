from app.core.game_rules import GameRules, game_rules


REALM_IDENTITIES = (
    ("mortal", "Phàm Nhân", 0),
    ("qi_refining", "Luyện Khí", 1),
    ("foundation_establishment", "Trúc Cơ", 2),
    ("golden_core", "Kim Đan", 3),
    ("nascent_soul", "Nguyên Anh", 4),
    ("soul_formation", "Hóa Thần", 5),
    ("void_refinement", "Luyện Hư", 6),
    ("body_integration", "Hợp Thể", 7),
    ("mahayana", "Đại Thừa", 8),
    ("tribulation", "Độ Kiếp", 9),
    ("human_immortal", "Nhân Tiên", 10),
)


def realm_definitions(rules: GameRules = game_rules) -> list[dict]:
    return [{"key": key, "name": name, "rank_order": rank, **rules.realm_rules[key].model_dump()}
            for key, name, rank in REALM_IDENTITIES]


REALM_DEFINITIONS = realm_definitions()


def required_exp_for_stage(base_required_exp: int, growth_factor: float, stage: int) -> int:
    return int(base_required_exp * (growth_factor ** max(stage - 1, 0)))
