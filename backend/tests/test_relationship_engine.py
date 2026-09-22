from app.game.data.relationships import address_for, prompt_for


def test_relationship_catalog_has_three_stable_choices_and_content_only_addresses():
    for npc_key in ("xie_wuchen", "luo_qinghan", "wandering_cultivator"):
        prompt = prompt_for(npc_key, "cultivating")
        assert prompt.version == 1
        assert len(prompt.choices) == 3
        assert len({choice.key for choice in prompt.choices}) == 3
    assert address_for(0) == "Đạo hữu"
    assert address_for(30) == "Bằng hữu"
    assert address_for(70) == "Tri kỷ"


def test_relationship_catalog_reflects_npc_activity_without_changing_identity():
    base = prompt_for("xie_wuchen", "cultivating")
    injured = prompt_for("xie_wuchen", "injured")
    exploring = prompt_for("xie_wuchen", "exploring")
    assert (injured.key, injured.version, injured.choices) == (
        base.key,
        base.version,
        base.choices,
    )
    assert (exploring.key, exploring.version, exploring.choices) == (
        base.key,
        base.version,
        base.choices,
    )
    assert "dưỡng thương" in injured.text
    assert "thám du" in exploring.text

