from app.core.game_rules import GameRules, game_rules


PILL_KEY = "items/qi_gathering_pill"
MANUAL_KEY = "manual/qing_mu_jue"

def item_definitions(rules: GameRules = game_rules) -> list[dict]:
    return [
        dict(key=PILL_KEY, name="Tụ Khí Đan", category="pill", asset_key=PILL_KEY,
             description=f"Dùng tối đa 1 viên khi đột phá. Tăng {rules.breakthrough_pill_bonus * 100:g} điểm phần trăm cơ hội, tối đa {rules.breakthrough_supported_cap * 100:g}%; tiêu hao cả khi thất bại."),
        dict(key=MANUAL_KEY, name="Thanh Mộc Quyết", category="manual", asset_key=MANUAL_KEY,
             description="Công pháp tìm thấy trong động phủ. Vật phẩm sở hữu, không tiêu hao; chưa có hiệu ứng cộng thêm."),
    ]


ITEM_DEFINITIONS = item_definitions()
