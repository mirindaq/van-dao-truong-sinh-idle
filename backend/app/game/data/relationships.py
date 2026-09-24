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
    "ye_qingzhu": DialoguePrompt(
        key="ye_qingzhu_gentle_remedy",
        version=1,
        text="Diệp Thanh Trúc nâng một nhánh linh thảo: “Thuốc cứu người quý ở dược lực hay tấm lòng?”",
        choices=(
            DialogueChoice("heart", "Tấm lòng đặt người bệnh lên trước.", "Nàng mỉm cười: “Đạo hữu hiểu điều quan trọng nhất của y đạo.”", 8),
            DialogueChoice("balance", "Cả hai phải cân bằng.", "Nàng gật đầu, cẩn thận cất nhánh linh thảo đi.", 5),
            DialogueChoice("power", "Dược lực đủ mạnh là được.", "Diệp Thanh Trúc khẽ lắc đầu: “Thuốc mạnh mà dùng sai cũng thành độc.”", -3),
        ),
    ),
    "hong_lian": DialoguePrompt(
        key="hong_lian_alchemy_flame",
        version=1,
        text="Hồng Liên nhìn lửa trong đan lô: “Khi một mẻ đan sắp hỏng, đạo hữu sẽ làm gì?”",
        choices=(
            DialogueChoice("stay", "Ở lại cùng nàng cứu mẻ đan.", "Ánh lửa phản chiếu nụ cười rực rỡ của nàng.", 8),
            DialogueChoice("observe", "Bình tâm tìm nguyên nhân.", "Nàng khoanh tay: “Ít nhất đạo hữu không hoảng loạn.”", 5),
            DialogueChoice("leave", "Bỏ lò, giữ lấy linh dược còn lại.", "Hồng Liên hừ nhẹ: “Chưa cháy hết đã muốn chạy rồi sao?”", -4),
        ),
    ),
    "bai_yue": DialoguePrompt(
        key="bai_yue_still_water",
        version=1,
        text="Bạch Nguyệt hỏi bên dòng suối: “Nước mềm yếu, vì sao vẫn xuyên được đá?”",
        choices=(
            DialogueChoice("endure", "Vì kiên trì không ngừng nghỉ.", "Nàng nhìn bạn thật lâu rồi khẽ mỉm cười.", 8),
            DialogueChoice("adapt", "Vì biết thuận theo địa thế.", "Bạch Nguyệt gật đầu: “Biết biến đổi cũng là một loại đạo.”", 5),
            DialogueChoice("force", "Chỉ cần dòng đủ mạnh.", "Mặt nước trước nàng gợn lên rồi nhanh chóng lặng xuống.", -3),
        ),
    ),
    "lei_ziyan": DialoguePrompt(
        key="lei_ziyan_thunder_oath",
        version=1,
        text="Lôi Tử Yên chống trường thương: “Nếu thiên kiếp giáng xuống, đạo hữu sẽ đứng ở đâu?”",
        choices=(
            DialogueChoice("beside", "Đứng bên cạnh nàng.", "Nàng bật cười: “Vậy đừng để ta phải chờ.”", 8),
            DialogueChoice("front", "Đứng phía trước che chắn.", "Nàng nhướng mày, nhưng ánh mắt đã bớt sắc lạnh.", 5),
            DialogueChoice("away", "Tìm nơi an toàn quan sát.", "Lôi Tử Yên xoay thương: “Kẻ sợ sấm khó đi cùng ta.”", -4),
        ),
    ),
    "yun_ruoli": DialoguePrompt(
        key="yun_ruoli_free_wind",
        version=1,
        text="Vân Nhược Ly nhìn mây trôi: “Nếu không còn con đường nào trên bản đồ, đạo hữu sẽ đi đâu?”",
        choices=(
            DialogueChoice("together", "Cùng nàng tìm một con đường mới.", "Nàng đưa tay đón gió: “Vậy chuyến đi này sẽ không cô độc.”", 8),
            DialogueChoice("home", "Quay về chuẩn bị kỹ hơn.", "Nàng cười nhẹ: “Cẩn trọng cũng không phải điều xấu.”", 5),
            DialogueChoice("wait", "Đợi người khác mở đường.", "Vân Nhược Ly quay đi: “Gió không chờ người do dự.”", -3),
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
