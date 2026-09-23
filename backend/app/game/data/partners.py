from app.core.game_rules import GameRules

PARTNERS = (
    ("luo_qinghan", "Lạc Thanh Hàn"),
    ("xie_wuchen", "Tạ Vô Trần"),
    ("wandering_cultivator", "Vị tán tu"),
)


def partner_stack(rules: GameRules, active_count: int) -> tuple[int, float, float]:
    if active_count <= 0:
        return 0, 1, 0
    return (
        rules.dao_partner_combat * active_count,
        rules.dao_partner_factor ** active_count,
        rules.dao_partner_flat * active_count,
    )
