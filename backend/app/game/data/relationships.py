from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class DialogueChoice:
    key: str
    text: str
    response: str
    affinity_delta: int


@dataclass(frozen=True)
class DialoguePrompt:
    key: str
    version: int
    text: str
    choices: tuple[DialogueChoice, DialogueChoice, DialogueChoice]

    def snapshot_choices(self) -> list[dict[str, str | int]]:
        return [asdict(choice) for choice in self.choices]


PROMPTS = {
    "xie_wuchen": DialoguePrompt(
        key="xie_wuchen_sword_path",
        version=1,
        text="Tạ Vô Trần nhìn về phía kiếm phong: “Đạo hữu cho rằng kiếm tu quý nhất điều gì?”",
        choices=(
            DialogueChoice("resolve", "Một lòng không đổi.", "Ánh mắt hắn dịu đi: “Đạo tâm kiên định, lời này rất hợp ý ta.”", 8),
            DialogueChoice("mercy", "Biết khi nào nên thu kiếm.", "Hắn im lặng hồi lâu rồi khẽ gật đầu.", 5),
            DialogueChoice("power", "Sức mạnh áp đảo tất cả.", "Tạ Vô Trần cau mày: “Kiếm không có tâm chỉ là hung khí.”", -4),
        ),
    ),
    "luo_qinghan": DialoguePrompt(
        key="luo_qinghan_moonlit_road",
        version=1,
        text="Lạc Thanh Hàn hỏi nhỏ: “Nếu đường phía trước chìm trong sương lạnh, đạo hữu sẽ làm gì?”",
        choices=(
            DialogueChoice("together", "Cùng người tìm đường.", "Nàng thoáng mỉm cười: “Vậy thì con đường ấy bớt lạnh rồi.”", 8),
            DialogueChoice("patient", "Dừng lại quan sát thiên cơ.", "Nàng gật đầu, tán thành sự thận trọng của bạn.", 5),
            DialogueChoice("alone", "Tự mình đi trước.", "Ánh mắt nàng trở nên xa cách: “Đạo hữu quả thật quen độc hành.”", -3),
        ),
    ),
    "wandering_cultivator": DialoguePrompt(
        key="wanderer_place_to_stand",
        version=1,
        text="Vị tán tu cười khổ: “Giữa tiên lộ rộng lớn, người vô danh dựa vào đâu để đứng vững?”",
        choices=(
            DialogueChoice("kindness", "Dựa vào người từng chìa tay giúp mình.", "Vị tán tu ôm quyền, nét mặt chân thành hơn trước.", 8),
            DialogueChoice("patience", "Dựa vào từng bước tích lũy.", "Người ấy cười: “Một lời giản dị mà rất thật.”", 5),
            DialogueChoice("fortune", "Chỉ có cơ duyên quyết định.", "Vị tán tu thở dài: “Có lẽ đạo hữu chưa từng thiếu đường lui.”", -3),
        ),
    ),
}


def prompt_for(npc_key: str, activity: str) -> DialoguePrompt:
    prompt = PROMPTS[npc_key]
    if activity == "injured":
        return DialoguePrompt(
            key=prompt.key,
            version=prompt.version,
            text=f"Dù đang dưỡng thương, {prompt.text[0].lower() + prompt.text[1:]}",
            choices=prompt.choices,
        )
    if activity == "exploring":
        return DialoguePrompt(
            key=prompt.key,
            version=prompt.version,
            text=f"Trong lúc dừng chân trên đường thám du, {prompt.text[0].lower() + prompt.text[1:]}",
            choices=prompt.choices,
        )
    return prompt


def address_for(affinity: int) -> str:
    if affinity >= 70:
        return "Tri kỷ"
    if affinity >= 30:
        return "Bằng hữu"
    return "Đạo hữu"

