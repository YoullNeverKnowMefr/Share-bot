import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.config import get_settings
from app.core.db import get_session
from app.domain.repositories import ChainRepository
from app.domain.services.telethon_client import telethon_manager


async def migrate_chain_titles():
    
    await telethon_manager.start()
    
    try:
        async with get_session() as session:
            repo = ChainRepository(session)
            chains = await repo.list_all()
            
            updated_count = 0
            
            for chain in chains:
                if not chain.source_chat_title:
                    try:
                        entity = await telethon_manager.client.get_entity(chain.source_chat_id)
                        title = getattr(entity, 'title', None) or getattr(entity, 'username', None) or f"ID {chain.source_chat_id}"
                        
                        chain.source_chat_title = title
                        await session.flush()
                        
                        print(f"✅ Цепочка #{chain.id}: '{title}'")
                        updated_count += 1
                        
                    except Exception as e:
                        print(f"❌ Ошибка для цепочки #{chain.id} (chat_id={chain.source_chat_id}): {e}")
                        continue
            
            await session.commit()
            print(f"\n✅ Обновлено цепочек: {updated_count}")
            
    finally:
        await telethon_manager.stop()


if __name__ == "__main__":
    asyncio.run(migrate_chain_titles())
