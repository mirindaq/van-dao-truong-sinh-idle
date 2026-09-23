from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.game_rules import GameRules, game_rules
from app.game.breakthrough import BreakthroughEngine
from app.game.cultivation import CultivationEngine, CultivationInput
from app.game.data.alchemy import alchemy_definitions
from app.game.data.equipment import equipment_definitions, pack_definitions
from app.game.data.items import HERB_KEY, MANUAL_KEY, PILL_KEY, item_definitions
from app.game.data.partners import PARTNERS, partner_stack
from app.game.data.pets import pet_definitions
from app.game.data.realms import realm_definitions, required_exp_for_stage
from app.game.random_service import RandomService
from app.models.alchemy import AlchemyReceipt
from app.models.partner import DaoPartner
from app.models.relationship import NpcRelationship
from app.models.item import Item, OwnedItem
from app.models.spirit_pet import SpiritPetBond, SpiritPetReceipt
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.equipment_repository import EquipmentRepository
from app.models.player import Player
from app.models.realm import Realm
from app.models.spiritual_root import SpiritualRoot
from app.repositories.game_log_repository import GameLogRepository
from app.repositories.player_repository import PlayerRepository
from app.repositories.realm_repository import RealmRepository
from app.schemas.game_state import (
    BreakthroughRead, BreakthroughRequest, BreakthroughResult, BreakthroughSelection, CultivationRead,
    GameLogRead, GameStateRead, InventoryRead, OfflineRead, PlayerRead, RealmRead, SpiritualRootRead,
    AlchemyCatalogRead, AlchemyRecipeRead, CraftReceiptRead, CraftRequest, CraftResponse,
    DaoPartnerRead, PartnerRosterRead,
    EquipRequest, EquippedRead, PetBondRequest, PetBondResponse, PetCatalogRead, PetReceiptRead,
    PetSpeciesRead, SpiritPetRead,
)

INITIAL_ROOT_IDENTITY = {
    "key": "wood_common", "name": "Mộc Linh Căn", "elements": ["wood"],
    "quality": "common",
}


def _server_now() -> datetime:
    from app.services.exploration_service import server_now
    return server_now()


class GameError(Exception):
    def __init__(self, code: str, status: int = 409):
        self.code = code
        self.status = status


class GameStateService:
    def __init__(self, session: AsyncSession, rng: RandomService | None = None, rules: GameRules = game_rules) -> None:
        self.session = session
        self.rules = rules
        self.realm_definitions = realm_definitions(rules)
        self.item_definitions = item_definitions(rules)
        self.equipment_definitions = equipment_definitions(rules)
        self.pack_definitions = pack_definitions(rules)
        self.players = PlayerRepository(session)
        self.realms = RealmRepository(session)
        self.logs = GameLogRepository(session)
        self.inventory = InventoryRepository(session)
        self.equipment = EquipmentRepository(session)
        self.cultivation_engine = CultivationEngine()
        self.breakthrough_engine = BreakthroughEngine(rules)
        self.rng = rng or RandomService()

    async def _load(self) -> Player:
        await self.players.lock_save()
        player = await self.players.get_first()
        if player is None:
            raise GameError("no_save", 404)
        await self._ensure_seed_data()
        return player

    async def get_state(self) -> GameStateRead:
        player = await self._load()
        await self._apply_progress(player)
        state = await self._state(player)
        await self.session.commit()
        return state

    async def new_game(self, name: str) -> GameStateRead:
        await self.players.lock_save()
        if await self.players.get_first() is not None:
            raise GameError("save_exists")
        await self._ensure_seed_data()
        realm = await self.realms.get_realm_by_key(self.rules.starting_realm_key)
        root = await self.realms.get_root_by_key(self.rules.starting_root_key)
        if realm is None or root is None:
            raise RuntimeError("Seed data missing")
        player = await self.players.add(Player(
            name=name, realm=realm, spiritual_root=root, stage=self.rules.starting_stage, cultivation_exp=0,
            spirit_stones=self.rules.starting_spirit_stones, combat_power=self.rules.starting_combat_power,
            manual_key="manual/qing_mu_jue", current_activity="cultivating",
            last_cultivation_at=datetime.now(timezone.utc),
        ))
        await self.inventory.grant_initial(
            player.id,
            self.item_definitions,
            self.rules.starting_pills,
            self.rules.starting_manuals,
        )
        await self.logs.create("player", "Bạn tìm thấy động phủ bỏ hoang dưới chân Thanh Vân Sơn.")
        await self.logs.create(
            "player",
            f"Di vật còn lại gồm {self.rules.starting_manuals} Thanh Mộc Quyết, "
            f"{self.rules.starting_spirit_stones} Linh Thạch và "
            f"{self.rules.starting_pills} Tụ Khí Đan.",
        )
        state = await self._state(player)
        await self.session.commit()
        return state

    async def acknowledge_offline(self, report_id: int) -> None:
        await self._load()
        report = await self.logs.pending_offline()
        if report is not None and report.id == report_id:
            report.log_metadata = {**report.log_metadata, "pending": False}
        await self.session.commit()

    async def claim_equipment_pack(self) -> GameStateRead:
        player = await self._load()
        if not player.equipment_pack_claimed:
            await self.equipment.claim(
                player.id,
                self.pack_definitions,
                self.rules.equipment_pack_quantity,
            )
            player.equipment_pack_claimed = True
            await self.logs.create('equipment', 'Đã nhận gói trang bị: Thanh Trúc Kiếm, Vải Thô Đạo Bào và Thanh Mộc Ngọc Bội.')
        await self._apply_progress(player)
        state = await self._state(player)
        await self.session.commit()
        return state

    async def equip(self, request: EquipRequest) -> GameStateRead:
        player = await self._load()
        if request.item_key is not None:
            owned = await self.inventory.get(player.id, request.item_key)
            if owned is None or owned.quantity < 1:
                raise GameError('item_not_owned')
            if owned.item.category != 'equipment' or owned.item.equipment_slot != request.slot:
                raise GameError('invalid_equipment')
            if any(row.item_key == request.item_key and row.slot != request.slot for row in await self.equipment.list(player.id)):
                raise GameError('invalid_equipment')
        await self.equipment.set_slot(player.id, request.slot, request.item_key)
        await self._apply_progress(player)
        state = await self._state(player)
        await self.session.commit()
        return state

    async def preview(self, selection: BreakthroughSelection | None = None) -> BreakthroughRead:
        player = await self._load()
        await self._apply_progress(player)
        preview = await self._preview(player, selection)
        await self.session.commit()
        return preview

    async def attempt(self, request: BreakthroughRequest) -> BreakthroughResult:
        player = await self._load()
        receipt = await self.logs.attempt_receipt(str(request.request_id), player.id)
        if receipt is not None:
            fingerprint = receipt.log_metadata.get("request")
            if (fingerprint is not None and fingerprint != request.model_dump(mode="json")) or (fingerprint is None and request.quantity):
                raise GameError("request_conflict")
            result = BreakthroughResult.model_validate({
                **receipt.log_metadata["result"],
                "rules_version": receipt.log_metadata.get("rules_version", 1),
                "rules_fingerprint": receipt.log_metadata.get("rules_fingerprint", "legacy"),
            })
            await self.session.commit()
            return result
        stored_preview = await self.logs.preview_record(player.id, request.quantity)
        if (stored_preview is None or stored_preview.log_metadata["token"] != request.revision
                or stored_preview.log_metadata["snapshot"] != await self._snapshot(player, request)):
            raise GameError("stale_preview")
        await self._apply_progress(player)
        preview = await self._preview(player, request)
        if preview.target is None:
            raise GameError("max_realm")
        if not preview.available:
            raise GameError("insufficient_cultivation")
        pill = await self.inventory.get(player.id, PILL_KEY)
        if request.quantity and (pill is None or pill.quantity < 1):
            raise GameError("insufficient_items")
        odds = self.breakthrough_engine.preview(
            major=player.stage == player.realm.max_stage,
            root_modifier=player.spiritual_root.breakthrough_modifier,
            required_exp=preview.required_exp,
            use_pill=bool(request.quantity),
        )
        source = self._realm_read(player)
        success = self.breakthrough_engine.attempt(odds, self.rng)
        if request.quantity:
            pill.quantity -= 1
        lost = 0.0
        if success:
            target_realm = await self.realms.get_realm_by_key(preview.target.key)
            if target_realm is None:
                raise GameError("realm_unavailable")
            player.realm = target_realm
            player.stage = preview.target.stage
            player.cultivation_exp -= preview.required_exp
            player.combat_power = round(player.combat_power * self.rules.breakthrough_combat_multiplier) + self.rules.breakthrough_combat_flat
            message = f"Đột phá thành công: {target_realm.name} tầng {player.stage}."
        else:
            lost = min(player.cultivation_exp, odds.failure_loss)
            player.cultivation_exp -= lost
            message = f"Đột phá thất bại. Tổn thất {lost:g} tu vi. Hãy tĩnh tâm tu luyện."
        result = BreakthroughResult(
            success=success, message=message, cultivation_lost=lost, realm=self._realm_read(player),
            item_key=request.item_key, items_consumed=request.quantity, final_chance=odds.total,
            created_at=datetime.now(timezone.utc),
            rules_version=self.rules.rules_version, rules_fingerprint=self.rules.fingerprint,
        )
        player.last_cultivation_at = max(datetime.now(timezone.utc), player.last_cultivation_at + timedelta(microseconds=1))
        log = await self.logs.create("breakthrough", message)
        log.log_metadata = {
            "player_id": player.id, "request_id": str(request.request_id),
            "source": source.model_dump(mode="json"), "target": preview.target.model_dump(mode="json"),
            "request": request.model_dump(mode="json"), "result": result.model_dump(mode="json"),
            "rules_version": self.rules.rules_version, "rules_fingerprint": self.rules.fingerprint,
        }
        if request.quantity:
            log.message += " Đã dùng 1 Tụ Khí Đan."
        await self.session.commit()
        return result

    async def list_pets(self) -> PetCatalogRead:
        player = await self._load()
        await self._apply_progress(player)
        bond = await self._bond(player.id)
        await self.session.commit()
        return PetCatalogRead(species=self._species(), spirit_pet=self._spirit_pet(bond))

    async def bond_pet(self, request: PetBondRequest) -> PetBondResponse:
        player = await self._load()
        receipt = await self._pet_receipt(player.id, request.request_id)
        if receipt is not None:
            if receipt.pet_key != request.pet_key:
                raise GameError("pet_request_conflict")
            await self._apply_progress(player)
            state = await self._state(player)
            await self.session.commit()
            return PetBondResponse(state=state, receipt=self._receipt_read(receipt))
        if request.pet_key not in self.rules.pet_rules:
            raise GameError("unknown_pet")
        if await self._bond(player.id) is not None:
            raise GameError("pet_already_bonded")
        await self._apply_progress(player)
        now = _server_now()
        bond = SpiritPetBond(
            player_id=player.id, pet_key=request.pet_key, active=True,
            request_id=str(request.request_id), bonded_at=now, state_changed_at=now,
        )
        receipt = SpiritPetReceipt(
            player_id=player.id, request_id=str(request.request_id),
            pet_key=request.pet_key, created_at=now,
        )
        self.session.add(bond)
        self.session.add(receipt)
        await self.session.flush()
        state = await self._state(player)
        await self.session.commit()
        return PetBondResponse(state=state, receipt=self._receipt_read(receipt))

    async def rest_pet(self) -> GameStateRead:
        return await self._set_pet_active(False)

    async def recall_pet(self) -> GameStateRead:
        return await self._set_pet_active(True)

    async def list_partners(self) -> PartnerRosterRead:
        player = await self._load()
        partners = await self._partner_roster(player.id)
        await self.session.commit()
        return PartnerRosterRead(partners=partners)

    async def bond_partner(self, npc_key: str) -> GameStateRead:
        player = await self._load()
        self._known_partner(npc_key)
        affinity = await self._affinity(player.id, npc_key, lock=True)
        existing = await self._dao_partner(player.id, npc_key)
        if existing is not None and existing.active:
            state = await self._state(player)
            await self.session.commit()
            return state
        if affinity < self.rules.dao_partner_affinity:
            raise GameError("partner_not_ready")
        await self._apply_progress(player)
        now = _server_now()
        if existing is None:
            self.session.add(DaoPartner(
                player_id=player.id, npc_key=npc_key, active=True, bonded_at=now, dismissed_at=None,
            ))
        else:
            existing.active = True
            existing.dismissed_at = None
        await self.session.flush()
        state = await self._state(player)
        await self.session.commit()
        return state

    async def dismiss_partner(self, npc_key: str) -> GameStateRead:
        player = await self._load()
        self._known_partner(npc_key)
        existing = await self._dao_partner(player.id, npc_key)
        if existing is None or not existing.active:
            raise GameError("partner_not_bonded")
        await self._apply_progress(player)
        existing.active = False
        existing.dismissed_at = _server_now()
        state = await self._state(player)
        await self.session.commit()
        return state

    def _known_partner(self, npc_key: str) -> None:
        if npc_key not in {key for key, _name in PARTNERS}:
            raise GameError("unknown_partner")

    async def _affinity(self, player_id: int, npc_key: str, lock: bool = False) -> int:
        query = select(NpcRelationship).where(
            NpcRelationship.player_id == player_id, NpcRelationship.npc_key == npc_key,
        )
        relationship = await self.session.scalar(query.with_for_update() if lock else query)
        return relationship.affinity if relationship is not None else 0

    async def _dao_partner(self, player_id: int, npc_key: str) -> DaoPartner | None:
        return await self.session.scalar(select(DaoPartner).where(
            DaoPartner.player_id == player_id, DaoPartner.npc_key == npc_key,
        ))

    async def _active_partner_count(self, player_id: int) -> int:
        rows = await self.session.scalars(select(DaoPartner).where(
            DaoPartner.player_id == player_id, DaoPartner.active.is_(True),
        ))
        return len(list(rows))

    async def _partner_roster(self, player_id: int) -> list[DaoPartnerRead]:
        roster = []
        for key, name in PARTNERS:
            bond = await self._dao_partner(player_id, key)
            roster.append(DaoPartnerRead(
                npc_key=key, name=name, affinity=await self._affinity(player_id, key),
                active=bool(bond and bond.active),
            ))
        return roster

    async def list_alchemy(self) -> AlchemyCatalogRead:
        player = await self._load()
        await self._apply_progress(player)
        inventory = await self.inventory.list(player.id)
        await self.session.commit()
        return AlchemyCatalogRead(
            recipes=[AlchemyRecipeRead.model_validate(recipe) for recipe in alchemy_definitions(self.rules)],
            herb_quantity=self._quantity(inventory, HERB_KEY),
            pill_quantity=self._quantity(inventory, PILL_KEY),
        )

    async def craft(self, request: CraftRequest) -> CraftResponse:
        player = await self._load()
        receipt = await self._alchemy_receipt(player.id, request.request_id)
        if receipt is not None:
            if receipt.recipe_key != request.recipe_key or receipt.ingredient_quantity != request.ingredient_quantity:
                raise GameError("alchemy_request_conflict")
            state = await self._state(player)
            await self.session.commit()
            return CraftResponse(state=state, receipt=self._craft_receipt_read(receipt))
        recipe = self.rules.alchemy_recipes.get(request.recipe_key)
        if recipe is None or request.ingredient_quantity != recipe.ingredient_quantity:
            raise GameError("alchemy_request_conflict" if recipe is not None else "unknown_recipe")
        herb = await self.inventory.get(player.id, recipe.ingredient_key)
        if herb is None or herb.quantity < recipe.ingredient_quantity:
            raise GameError("insufficient_herbs")
        pill = await self.inventory.get(player.id, recipe.result_key)
        if pill is None:
            pill = OwnedItem(player_id=player.id, item_key=recipe.result_key, quantity=0)
            self.session.add(pill)
        herb.quantity -= recipe.ingredient_quantity
        pill.quantity += recipe.result_quantity
        receipt = AlchemyReceipt(
            player_id=player.id, request_id=str(request.request_id), recipe_key=request.recipe_key,
            ingredient_key=recipe.ingredient_key, ingredient_quantity=recipe.ingredient_quantity,
            result_key=recipe.result_key, result_quantity=recipe.result_quantity, created_at=_server_now(),
        )
        self.session.add(receipt)
        await self.session.flush()
        state = await self._state(player)
        await self.session.commit()
        return CraftResponse(state=state, receipt=self._craft_receipt_read(receipt))

    @staticmethod
    def _quantity(inventory, key: str) -> int:
        owned = next((item for item in inventory if item.item_key == key), None)
        return owned.quantity if owned is not None else 0

    def _craft_receipt_read(self, receipt: AlchemyReceipt) -> CraftReceiptRead:
        return CraftReceiptRead(
            request_id=receipt.request_id, recipe_key=receipt.recipe_key,
            ingredient_key=receipt.ingredient_key, ingredient_quantity=receipt.ingredient_quantity,
            result_key=receipt.result_key, result_quantity=receipt.result_quantity,
        )

    async def _alchemy_receipt(self, player_id: int, request_id) -> AlchemyReceipt | None:
        return await self.session.scalar(select(AlchemyReceipt).where(
            AlchemyReceipt.player_id == player_id,
            AlchemyReceipt.request_id == str(request_id),
        ))

    async def _set_pet_active(self, active: bool) -> GameStateRead:
        player = await self._load()
        bond = await self._bond(player.id)
        if bond is None:
            raise GameError("no_pet")
        if bond.active != active:
            await self._apply_progress(player)
            bond.active = active
            bond.state_changed_at = _server_now()
        state = await self._state(player)
        await self.session.commit()
        return state

    def pet_combat_bonus(self, bond: SpiritPetBond | None) -> int:
        if bond is None or not bond.active:
            return 0
        return self.rules.pet_rules[bond.pet_key].combat_bonus

    def _pet_cultivation(self, bond: SpiritPetBond | None) -> tuple[float, float]:
        if bond is None or not bond.active:
            return 1, 0
        rule = self.rules.pet_rules[bond.pet_key]
        return rule.cultivation_factor, rule.cultivation_flat_per_minute

    def _species(self) -> list[PetSpeciesRead]:
        return [PetSpeciesRead.model_validate(pet) for pet in pet_definitions(self.rules)]

    def _spirit_pet(self, bond: SpiritPetBond | None) -> SpiritPetRead | None:
        if bond is None:
            return None
        species = next(pet for pet in self._species() if pet.key == bond.pet_key)
        return SpiritPetRead(key=bond.pet_key, name=species.name, active=bond.active)

    def _receipt_read(self, receipt: SpiritPetReceipt) -> PetReceiptRead:
        return PetReceiptRead(request_id=receipt.request_id, pet_key=receipt.pet_key)

    async def _bond(self, player_id: int) -> SpiritPetBond | None:
        return await self.session.scalar(select(SpiritPetBond).where(SpiritPetBond.player_id == player_id))

    async def _pet_receipt(self, player_id: int, request_id) -> SpiritPetReceipt | None:
        return await self.session.scalar(select(SpiritPetReceipt).where(
            SpiritPetReceipt.player_id == player_id,
            SpiritPetReceipt.request_id == str(request_id),
        ))

    async def _apply_progress(self, player: Player) -> None:
        now = datetime.now(timezone.utc)
        bond = await self._bond(player.id)
        factor, flat = self._pet_cultivation(bond)
        _, partner_factor, partner_flat = partner_stack(self.rules, await self._active_partner_count(player.id))
        progress = self.cultivation_engine.apply_offline_progress(CultivationInput(
            cultivation_exp=player.cultivation_exp, last_cultivation_at=player.last_cultivation_at,
            current_time=now, base_rate_per_minute=self._base_rate_per_minute(player),
            root_modifier=player.spiritual_root.cultivation_modifier,
            pet_factor=factor, pet_flat_per_minute=flat,
            partner_factor=partner_factor, partner_flat_per_minute=partner_flat,
        ))
        player.cultivation_exp = progress.cultivation_exp
        # Preserve fractional seconds and never move a future timestamp backwards.
        player.last_cultivation_at += timedelta(seconds=progress.elapsed_seconds)
        if progress.elapsed_seconds >= self.rules.offline_report_min_seconds and progress.earned_exp > 0:
            report = await self.logs.pending_offline()
            previous = report.log_metadata if report else {}
            if report is None:
                report = await self.logs.create("cultivation", "Bế quan kết thúc.")
            report.log_metadata = {
                "pending": True,
                "elapsed_seconds": previous.get("elapsed_seconds", 0) + progress.elapsed_seconds,
                "earned_exp": previous.get("earned_exp", 0) + progress.earned_exp,
                "rules_version": self.rules.rules_version,
                "rules_fingerprint": self.rules.fingerprint,
            }
            report.message = f"Bế quan kết thúc. Nhận {report.log_metadata['earned_exp']:.2f} tu vi."

    async def _snapshot(self, player: Player, selection: BreakthroughSelection) -> dict:
        pill = await self.inventory.get(player.id, PILL_KEY)
        return dict(player_id=player.id, realm_id=player.realm_id, stage=player.stage,
                    cultivation=player.cultivation_exp, timestamp=player.last_cultivation_at.isoformat(),
                    pills=pill.quantity if pill else 0, item_key=selection.item_key,
                    quantity=selection.quantity, root_modifier=player.spiritual_root.breakthrough_modifier)

    async def _preview(self, player: Player, selection: BreakthroughSelection | None = None) -> BreakthroughRead:
        selection = selection or BreakthroughSelection()
        required = required_exp_for_stage(player.realm.base_required_exp, player.realm.growth_factor, player.stage)
        target = None
        if player.stage < player.realm.max_stage:
            target = self._realm_read(player).model_copy(update={"stage": player.stage + 1})
        else:
            definition = next((r for r in self.realm_definitions if r["rank_order"] == player.realm.rank_order + 1), None)
            if definition:
                realm = await self.realms.get_realm_by_key(definition["key"])
                if realm:
                    target = RealmRead(key=realm.key, name=realm.name, stage=1, max_stage=realm.max_stage)
        odds = self.breakthrough_engine.preview(
            major=player.stage == player.realm.max_stage,
            root_modifier=player.spiritual_root.breakthrough_modifier, required_exp=required,
            use_pill=bool(selection.quantity),
        )
        snapshot = await self._snapshot(player, selection)
        record = await self.logs.preview_record(player.id, selection.quantity)
        if record is None:
            record = await self.logs.create("breakthrough_preview", "")
        if record.log_metadata.get("snapshot") != snapshot:
            record.log_metadata = dict(player_id=player.id, quantity=selection.quantity,
                                       token=str(uuid4()), snapshot=snapshot)
        return BreakthroughRead(
            available=target is not None and player.cultivation_exp >= required,
            target=target, required_exp=required, base_chance=odds.base,
            root_bonus=odds.root_bonus, final_chance=odds.total,
            failure_loss=odds.failure_loss, revision=record.log_metadata["token"],
            item_key=selection.item_key, quantity=selection.quantity, item_bonus=odds.item_bonus,
            pills_owned=snapshot["pills"],
        )

    async def _state(self, player: Player) -> GameStateRead:
        inventory = [InventoryRead(
            key=owned.item_key, name=owned.item.name, category=owned.item.category,
            description=owned.item.description, asset_key=owned.item.asset_key, quantity=owned.quantity,
            equipment_slot=owned.item.equipment_slot, combat_bonus=owned.item.combat_bonus,
        ) for owned in await self.inventory.list(player.id)]
        pills = next((item.quantity for item in inventory if item.key == PILL_KEY), 0)
        equipment = [EquippedRead(slot=row.slot, item_key=row.item_key) for row in await self.equipment.list(player.id)]
        equipped_keys = {row.item_key for row in equipment}
        equipment_bonus = sum(item.combat_bonus for item in inventory if item.key in equipped_keys and item.quantity > 0)
        bond = await self._bond(player.id)
        pet_bonus = self.pet_combat_bonus(bond)
        spirit_pet = self._spirit_pet(bond)
        preview = await self._preview(player)
        base = self._base_rate_per_minute(player)
        root_rate = base * player.spiritual_root.cultivation_modifier
        factor, flat = self._pet_cultivation(bond)
        partners = await self._partner_roster(player.id)
        active_partners = [partner for partner in partners if partner.active]
        partner_bonus, partner_factor, partner_flat = partner_stack(self.rules, len(active_partners))
        rate = root_rate * factor * partner_factor + flat + partner_flat
        report = await self.logs.pending_offline()
        return GameStateRead(
            rules_version=self.rules.rules_version,
            rules_fingerprint=self.rules.fingerprint,
            player=PlayerRead(
                id=player.id, name=player.name, spirit_stones=player.spirit_stones,
                qi_gathering_pills=pills,
                combat_power=player.combat_power + equipment_bonus + pet_bonus + partner_bonus,
                base_combat_power=player.combat_power, equipment_bonus=equipment_bonus,
                pet_bonus=pet_bonus, partner_bonus=partner_bonus,
                manual_key=player.manual_key, current_activity=player.current_activity,
            ),
            inventory=inventory,
            equipment=equipment, equipment_pack_claimed=player.equipment_pack_claimed,
            realm=self._realm_read(player),
            spiritual_root=SpiritualRootRead.model_validate(player.spiritual_root, from_attributes=True),
            cultivation=CultivationRead(
                current_exp=player.cultivation_exp, required_exp=preview.required_exp,
                rate_per_minute=rate, base_rate_per_minute=base, root_bonus_per_minute=root_rate - base,
                pet_factor=factor, pet_flat_per_minute=flat,
                partner_factor=partner_factor, partner_flat_per_minute=partner_flat,
                seconds_until_next_stage=self.cultivation_engine.seconds_until_next_stage(player.cultivation_exp, preview.required_exp, rate),
                last_cultivation_at=player.last_cultivation_at,
            ),
            active_pet=spirit_pet.name if spirit_pet is not None and spirit_pet.active else None,
            spirit_pet=spirit_pet,
            dao_partner=", ".join(partner.name for partner in active_partners) or None,
            dao_partners=partners,
            recent_logs=[GameLogRead.model_validate(log, from_attributes=True) for log in await self.logs.recent()],
            server_time=_server_now(), breakthrough=preview,
            offline_report=OfflineRead(id=report.id, **report.log_metadata) if report else None,
        )

    async def _ensure_seed_data(self) -> None:
        for definition in self.realm_definitions:
            await self.realms.sync_realm(definition)
        root_rule = self.rules.root_rules[self.rules.starting_root_key]
        root_definition = {**INITIAL_ROOT_IDENTITY, "key": self.rules.starting_root_key, **root_rule.model_dump()}
        await self.realms.sync_root(root_definition)
        for definition in (*self.item_definitions, *self.equipment_definitions):
            item = await self.session.get(Item, definition["key"])
            if item is None:
                self.session.add(Item(**definition))
            else:
                for field in ("name", "category", "description", "asset_key", "equipment_slot", "combat_bonus"):
                    if field in definition:
                        setattr(item, field, definition[field])

    @staticmethod
    def _realm_read(player: Player) -> RealmRead:
        return RealmRead(key=player.realm.key, name=player.realm.name, stage=player.stage, max_stage=player.realm.max_stage)

    def _base_rate_per_minute(self, player: Player) -> float:
        return self.rules.cultivation_base_rate * (1 + player.realm.rank_order * self.rules.cultivation_realm_bonus) * (1 + (player.stage - 1) * self.rules.cultivation_stage_bonus)
