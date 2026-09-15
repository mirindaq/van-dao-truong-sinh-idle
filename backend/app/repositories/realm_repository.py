from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.realm import Realm
from app.models.spiritual_root import SpiritualRoot


class RealmRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_realm_by_key(self, key: str) -> Realm | None:
        result = await self.session.execute(select(Realm).where(Realm.key == key))
        return result.scalar_one_or_none()

    async def get_root_by_key(self, key: str) -> SpiritualRoot | None:
        result = await self.session.execute(select(SpiritualRoot).where(SpiritualRoot.key == key))
        return result.scalar_one_or_none()

    async def add_realm(self, realm: Realm) -> Realm:
        self.session.add(realm)
        await self.session.flush()
        return realm

    async def add_root(self, root: SpiritualRoot) -> SpiritualRoot:
        self.session.add(root)
        await self.session.flush()
        return root

