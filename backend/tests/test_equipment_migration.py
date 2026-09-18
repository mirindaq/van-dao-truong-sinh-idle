from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from app.services.game_state_service import GameStateService
from app.schemas.game_state import EquipRequest
from tests.test_inventory_migration import upgrade


async def test_upgrade_existing_inventory_then_claim_equip_and_redeploy():
    schema = 'test_equipment_' + uuid4().hex
    admin = create_async_engine(settings.database_url)
    async with admin.begin() as connection:
        await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    options = {'server_settings': {'search_path': schema}}
    engine = create_async_engine(settings.database_url, connect_args=options)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(upgrade, '20260916_0004')
            await connection.execute(text("""INSERT INTO realms (id,key,name,rank_order,max_stage,base_required_exp,growth_factor)
                VALUES (1,'qi_refining','Luyện Khí',1,9,120,1.45)"""))
            await connection.execute(text("""INSERT INTO spiritual_roots (id,key,name,elements,quality,cultivation_modifier,breakthrough_modifier)
                VALUES (1,'wood_common','Mộc Linh Căn',ARRAY['wood'],'common',1.08,1.02)"""))
            await connection.execute(text("""INSERT INTO players (id,name,realm_id,spiritual_root_id,stage,cultivation_exp,spirit_stones,
                combat_power,manual_key,current_activity,last_cultivation_at)
                VALUES (1,'Thanh Vân',1,1,2,45,17,23,'manual/qing_mu_jue','cultivating',now()+interval '1 hour')"""))
            await connection.execute(text("""INSERT INTO owned_items VALUES (1,'items/qi_gathering_pill',2),(1,'manual/qing_mu_jue',1)"""))
            await connection.execute(text("""INSERT INTO game_logs (scope,message,metadata) VALUES ('breakthrough','legacy','{"receipt":"preserved"}')"""))
            await connection.run_sync(upgrade, 'head')
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with sessions() as session:
            service = GameStateService(session)
            state = await service.get_state()
            assert state.player.combat_power == 23 and state.player.qi_gathering_pills == 2
            assert state.cultivation.current_exp == 45 and state.player.spirit_stones == 17
            assert not state.equipment_pack_claimed and len(state.inventory) == 2
            await service.claim_equipment_pack()
            await service.equip(EquipRequest(slot='weapon', item_key='items/bamboo_sword'))
        await engine.dispose()
        engine = create_async_engine(settings.database_url, connect_args=options)
        async with engine.begin() as connection:
            await connection.run_sync(upgrade, 'head')
            assert (await connection.execute(text("SELECT metadata->>'receipt' FROM game_logs WHERE message='legacy'"))).scalar() == 'preserved'
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with sessions() as session:
            state = await GameStateService(session).claim_equipment_pack()
            assert state.player.combat_power == 28 and state.player.base_combat_power == 23
            assert len(state.equipment) == 1 and state.equipment_pack_claimed
            assert all(i.quantity == 1 for i in state.inventory if i.category == 'equipment')
    finally:
        await engine.dispose()
        async with admin.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin.dispose()
