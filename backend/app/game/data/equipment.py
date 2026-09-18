SLOTS = ('weapon', 'head', 'body', 'feet', 'ring', 'amulet')

EQUIPMENT_DEFINITIONS = [
    dict(key='items/bamboo_sword', name='Thanh Trúc Kiếm', category='equipment',
         description='Kiếm trúc nhẹ, cộng 5 chiến lực khi trang bị.',
         asset_key='items/bamboo_sword', equipment_slot='weapon', combat_bonus=5),
    dict(key='items/cloth_robe', name='Vải Thô Đạo Bào', category='equipment',
         description='Đạo bào giản dị, cộng 3 chiến lực khi trang bị.',
         asset_key='items/cloth_robe', equipment_slot='body', combat_bonus=3),
    dict(key='items/wood_amulet', name='Thanh Mộc Ngọc Bội', category='equipment',
         description='Ngọc bội mộc sắc, cộng 2 chiến lực khi trang bị.',
         asset_key='items/wood_amulet', equipment_slot='amulet', combat_bonus=2),
]
