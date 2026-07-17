import asyncio
import sys
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.app.domain.models import Chain


async def reset_chain_counter(chain_id: int, new_number: int):
    
    engine = create_async_engine(
        "sqlite+aiosqlite:///./sharechannel.sqlite3",
        echo=True,
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        result = await session.execute(
            select(Chain).where(Chain.id == chain_id)
        )
        chain = result.scalar_one_or_none()
        
        if chain is None:
            print(f"❌ Chain с id={chain_id} не найден!")
            return False
        
        old_number = chain.next_expected_number
        
        chain.next_expected_number = new_number
        await session.commit()
        
        print(f"✅ Chain {chain_id} обновлён:")
        print(f"   Старый счётчик: {old_number}")
        print(f"   Новый счётчик: {new_number}")
        print(f"   Источник: {chain.source_chat_id}")
        print(f"   Приёмник: {chain.sink_chat_id}")
        
        return True


async def main():
    if len(sys.argv) != 3:
        print("Использование: python reset_chain_counter.py <chain_id> <new_number>")
        print("Пример: python reset_chain_counter.py 1 1795")
        sys.exit(1)
    
    chain_id = int(sys.argv[1])
    new_number = int(sys.argv[2])
    
    print(f"Сброс счётчика для chain {chain_id} на {new_number}...")
    success = await reset_chain_counter(chain_id, new_number)
    
    if success:
        print("\n✅ Готово! Теперь перезапустите бота:")
        print("   systemctl restart sharechannel")
    else:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
