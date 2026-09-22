import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.core.game_rules import game_rules
from app.game.data.relationships import DialogueChoice, DialoguePrompt
from app.models.item import EquippedItem, OwnedItem
from app.models.player import Player
from app.models.relationship import NpcInteractionReceipt, NpcRelationship
from app.models.world import WorldNpc
from app.schemas.relationship import InteractionRequest
from app.services.game_state_service import GameError
from app.services.relationship_service import RelationshipService
from tests.test_game_api import game  # noqa: F401


async def test_relationship_happy_path_persists_prompt_receipt_and_profile(game):
    client, sessions = game
    await client.post("/game/new", json={"name": "Quan Sơn"})
    profile = (await client.get("/relationships/npcs/xie_wuchen")).json()
    assert profile["affinity"] == 0
    assert profile["address"] == "Đạo hữu"
    assert profile["prompt"] is None
    prompted = (await client.post("/relationships/npcs/xie_wuchen/prompt")).json()
    assert len(prompted["prompt"]["choices"]) == 3
    request_id = uuid4()
    choice = prompted["prompt"]["choices"][0]
    payload = {
        "request_id": str(request_id),
        "prompt_key": prompted["prompt"]["key"],
        "prompt_version": prompted["prompt"]["version"],
        "choice_key": choice["key"],
    }
    response = await client.post(
        "/relationships/npcs/xie_wuchen/interactions", json=payload
    )
    assert response.status_code == 200
    result = response.json()
    assert result["profile"]["affinity"] == 8
    assert result["profile"]["prompt"] is None
    assert result["interaction"]["prompt_text"] == prompted["prompt"]["text"]
    assert result["interaction"]["choice_text"] == choice["text"]
    reloaded = (await client.get("/relationships/npcs/xie_wuchen")).json()
    assert reloaded["history"] == [result["interaction"]]
    async with sessions() as session:
        assert await session.scalar(select(func.count()).select_from(NpcRelationship)) == 1
        assert await session.scalar(select(func.count()).select_from(NpcInteractionReceipt)) == 1


async def test_relationship_request_replay_and_conflict(game):
    client, _ = game
    await client.post("/game/new", json={"name": "Quan Sơn"})
    prompted = (await client.post("/relationships/npcs/luo_qinghan/prompt")).json()
    payload = {
        "request_id": str(uuid4()),
        "prompt_key": prompted["prompt"]["key"],
        "prompt_version": prompted["prompt"]["version"],
        "choice_key": prompted["prompt"]["choices"][0]["key"],
    }
    first = await client.post("/relationships/npcs/luo_qinghan/interactions", json=payload)
    replay = await client.post("/relationships/npcs/luo_qinghan/interactions", json=payload)
    assert replay.status_code == 200
    assert replay.json()["interaction"] == first.json()["interaction"]
    conflict = await client.post(
        "/relationships/npcs/luo_qinghan/interactions",
        json={**payload, "choice_key": prompted["prompt"]["choices"][1]["key"]},
    )
    assert conflict.status_code == 409
    assert conflict.json()["detail"] == "interaction_request_conflict"


async def test_relationship_concurrent_tabs_apply_one_delta(game):
    client, sessions = game
    await client.post("/game/new", json={"name": "Quan Sơn"})
    prompted = (await client.post("/relationships/npcs/wandering_cultivator/prompt")).json()
    prompt = prompted["prompt"]
    first_payload = {
        "request_id": str(uuid4()),
        "prompt_key": prompt["key"],
        "prompt_version": prompt["version"],
        "choice_key": prompt["choices"][0]["key"],
    }
    second_payload = {**first_payload, "request_id": str(uuid4())}
    responses = await asyncio.gather(
        client.post(
            "/relationships/npcs/wandering_cultivator/interactions", json=first_payload
        ),
        client.post(
            "/relationships/npcs/wandering_cultivator/interactions", json=second_payload
        ),
    )
    assert sorted(response.status_code for response in responses) == [200, 409]
    async with sessions() as session:
        relationship = await session.scalar(select(NpcRelationship))
        assert relationship.affinity == 8
        assert await session.scalar(select(func.count()).select_from(NpcInteractionReceipt)) == 1


async def test_relationship_cooldown_uses_server_time_and_backward_clock(game):
    client, sessions = game
    await client.post("/game/new", json={"name": "Quan Sơn"})
    start = datetime(2026, 9, 21, tzinfo=timezone.utc)
    rules = game_rules.model_copy(update={"relationship_cooldown_hours": 1})
    async with sessions() as session:
        service = RelationshipService(session, now=start, rules=rules)
        prompted = await service.open_prompt("xie_wuchen")
        choice = prompted.prompt.choices[0]
        result = await service.interact(
            "xie_wuchen",
            InteractionRequest(
                request_id=uuid4(),
                prompt_key=prompted.prompt.key,
                prompt_version=prompted.prompt.version,
                choice_key=choice.key,
            ),
        )
        assert result.profile.next_available_at == start + timedelta(hours=1)
    for current in (start - timedelta(hours=2), start + timedelta(minutes=59, seconds=59)):
        async with sessions() as session:
            with pytest.raises(GameError, match="interaction_cooldown"):
                await RelationshipService(session, now=current, rules=rules).open_prompt(
                    "xie_wuchen"
                )
    async with sessions() as session:
        available = await RelationshipService(
            session, now=start + timedelta(hours=1), rules=rules
        ).open_prompt("xie_wuchen")
        assert available.prompt is not None


async def test_pending_prompt_and_receipt_keep_old_content_version(monkeypatch, game):
    client, sessions = game
    await client.post("/game/new", json={"name": "Quan Sơn"})
    start = datetime(2026, 9, 21, tzinfo=timezone.utc)
    async with sessions() as session:
        original = await RelationshipService(session, now=start).open_prompt("luo_qinghan")
    replacement = DialoguePrompt(
        key="luo_qinghan_new_path",
        version=2,
        text="Nội dung mới",
        choices=(
            DialogueChoice("one", "Một", "Mới một", 1),
            DialogueChoice("two", "Hai", "Mới hai", 2),
            DialogueChoice("three", "Ba", "Mới ba", 3),
        ),
    )
    monkeypatch.setattr(
        "app.services.relationship_service.prompt_for", lambda *_: replacement
    )
    async with sessions() as session:
        pending = await RelationshipService(session, now=start).open_prompt("luo_qinghan")
        assert pending.prompt == original.prompt
        request = InteractionRequest(
            request_id=uuid4(),
            prompt_key=pending.prompt.key,
            prompt_version=pending.prompt.version,
            choice_key=pending.prompt.choices[0].key,
        )
        committed = await RelationshipService(session, now=start).interact(
            "luo_qinghan", request
        )
        assert committed.interaction.prompt_key == original.prompt.key
        assert committed.interaction.prompt_version == 1
        assert committed.interaction.prompt_text == original.prompt.text
    async with sessions() as session:
        replay = await RelationshipService(session).get_interaction(request.request_id)
        assert replay.interaction == committed.interaction


async def test_relationship_failure_rolls_back_prompt_affinity_and_cooldown(monkeypatch, game):
    client, sessions = game
    await client.post("/game/new", json={"name": "Quan Sơn"})
    now = datetime(2026, 9, 21, tzinfo=timezone.utc)
    async with sessions() as session:
        prompted = await RelationshipService(session, now=now).open_prompt("xie_wuchen")
    request = InteractionRequest(
        request_id=uuid4(),
        prompt_key=prompted.prompt.key,
        prompt_version=prompted.prompt.version,
        choice_key=prompted.prompt.choices[0].key,
    )
    async with sessions() as session:
        service = RelationshipService(session, now=now)

        async def fail_after_flush(*_):
            raise RuntimeError("response failed")

        monkeypatch.setattr(service, "_profile", fail_after_flush)
        with pytest.raises(RuntimeError, match="response failed"):
            await service.interact("xie_wuchen", request)
        await session.rollback()
    async with sessions() as session:
        relationship = await session.scalar(select(NpcRelationship))
        assert relationship.affinity == 0
        assert relationship.active_prompt_key == prompted.prompt.key
        assert relationship.next_available_at is None
        assert await session.scalar(select(func.count()).select_from(NpcInteractionReceipt)) == 0


@pytest.mark.parametrize("activity,phrase", [("injured", "dưỡng thương"), ("exploring", "thám du")])
async def test_relationship_prompt_reflects_world_activity(activity, phrase, game):
    client, sessions = game
    await client.post("/game/new", json={"name": "Quan Sơn"})
    await client.get("/world/state")
    async with sessions() as session:
        npc = await session.scalar(select(WorldNpc).where(WorldNpc.key == "xie_wuchen"))
        npc.activity = activity
        await session.commit()
    async with sessions() as session:
        profile = await RelationshipService(session).open_prompt("xie_wuchen")
        assert phrase in profile.prompt.text


async def test_relationship_lost_reply_recovers_same_receipt_and_history(game):
    client, _ = game
    await client.post("/game/new", json={"name": "Quan Sơn"})
    prompted = (await client.post("/relationships/npcs/xie_wuchen/prompt")).json()
    request_id = uuid4()
    payload = {
        "request_id": str(request_id),
        "prompt_key": prompted["prompt"]["key"],
        "prompt_version": prompted["prompt"]["version"],
        "choice_key": prompted["prompt"]["choices"][1]["key"],
    }
    committed = (
        await client.post("/relationships/npcs/xie_wuchen/interactions", json=payload)
    ).json()
    recovered = (await client.get(f"/relationships/interactions/{request_id}")).json()
    assert recovered == committed
    profile = (await client.get("/relationships/npcs/xie_wuchen")).json()
    assert profile["history"][0] == committed["interaction"]
    missing = await client.get(f"/relationships/interactions/{uuid4()}")
    assert missing.status_code == 404
    assert missing.json()["detail"] == "interaction_not_found"


async def test_relationship_changes_only_affinity_and_content(game):
    client, sessions = game
    await client.post("/game/new", json={"name": "Quan Sơn"})
    await client.get("/world/state")
    prompted = (await client.post("/relationships/npcs/luo_qinghan/prompt")).json()

    async def gameplay_snapshot():
        async with sessions() as session:
            player = await session.scalar(select(Player))
            inventory = list(
                (
                    await session.execute(
                        select(OwnedItem.item_key, OwnedItem.quantity).order_by(
                            OwnedItem.item_key
                        )
                    )
                ).all()
            )
            equipment = list(
                (
                    await session.execute(
                        select(EquippedItem.slot, EquippedItem.item_key).order_by(
                            EquippedItem.slot
                        )
                    )
                ).all()
            )
            npcs = list(
                (
                    await session.execute(
                        select(
                            WorldNpc.key,
                            WorldNpc.realm_key,
                            WorldNpc.stage,
                            WorldNpc.cultivation_exp,
                            WorldNpc.activity,
                            WorldNpc.location,
                            WorldNpc.injured_until,
                        ).order_by(WorldNpc.key)
                    )
                ).all()
            )
            return (
                player.realm_id,
                player.stage,
                player.cultivation_exp,
                player.spirit_stones,
                player.combat_power,
                player.equipment_pack_claimed,
                inventory,
                equipment,
                npcs,
            )

    before = await gameplay_snapshot()
    response = await client.post(
        "/relationships/npcs/luo_qinghan/interactions",
        json={
            "request_id": str(uuid4()),
            "prompt_key": prompted["prompt"]["key"],
            "prompt_version": prompted["prompt"]["version"],
            "choice_key": prompted["prompt"]["choices"][0]["key"],
        },
    )
    assert response.status_code == 200
    assert await gameplay_snapshot() == before


async def test_relationship_rejects_missing_npc_stale_prompt_and_invalid_choice(game):
    client, _ = game
    await client.post("/game/new", json={"name": "Quan Sơn"})
    assert (await client.get("/relationships/npcs/not_real")).status_code == 404
    prompted = (await client.post("/relationships/npcs/xie_wuchen/prompt")).json()
    base = {
        "request_id": str(uuid4()),
        "prompt_key": prompted["prompt"]["key"],
        "prompt_version": prompted["prompt"]["version"],
    }
    stale = await client.post(
        "/relationships/npcs/xie_wuchen/interactions",
        json={**base, "prompt_version": 999, "choice_key": "resolve"},
    )
    assert stale.status_code == 409 and stale.json()["detail"] == "prompt_conflict"
    invalid = await client.post(
        "/relationships/npcs/xie_wuchen/interactions",
        json={**base, "request_id": str(uuid4()), "choice_key": "not_real"},
    )
    assert invalid.status_code == 409 and invalid.json()["detail"] == "invalid_choice"
