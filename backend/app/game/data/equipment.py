from app.core.game_rules import GameRules, game_rules

SLOTS = ('weapon', 'head', 'body', 'feet', 'ring', 'amulet')

def equipment_definitions(rules: GameRules = game_rules) -> list[dict]:
    return [
        dict(key='items/bamboo_sword', name='Thanh Trúc Kiếm', category='equipment',
             description=f'Kiếm trúc nhẹ, cộng {rules.equipment_bonuses["items/bamboo_sword"]} chiến lực khi trang bị.',
             asset_key='items/bamboo_sword', equipment_slot='weapon', combat_bonus=rules.equipment_bonuses['items/bamboo_sword']),
        dict(key='items/cloth_robe', name='Vải Thô Đạo Bào', category='equipment',
             description=f'Đạo bào giản dị, cộng {rules.equipment_bonuses["items/cloth_robe"]} chiến lực khi trang bị.',
             asset_key='items/cloth_robe', equipment_slot='body', combat_bonus=rules.equipment_bonuses['items/cloth_robe']),
        dict(key='items/wood_amulet', name='Thanh Mộc Ngọc Bội', category='equipment',
             description=f'Ngọc bội mộc sắc, cộng {rules.equipment_bonuses["items/wood_amulet"]} chiến lực khi trang bị.',
             asset_key='items/wood_amulet', equipment_slot='amulet', combat_bonus=rules.equipment_bonuses['items/wood_amulet']),
        dict(key='items/spirit_vein_sword', name='Linh Mạch Kiếm', category='equipment',
             description=f'Kiếm lấy từ linh mạch, cộng {rules.equipment_bonuses["items/spirit_vein_sword"]} chiến lực khi trang bị.',
             asset_key='items/spirit_vein_sword', equipment_slot='weapon', combat_bonus=rules.equipment_bonuses['items/spirit_vein_sword']),
    ]


EQUIPMENT_DEFINITIONS = equipment_definitions()
