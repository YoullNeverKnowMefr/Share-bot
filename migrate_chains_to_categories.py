import asyncio
from sqlalchemy import select

from app.core.db import get_session
from app.domain.models import Shop, Category, Chain


async def migrate_chains_to_categories():
    
    async with get_session() as session:
        result = await session.execute(select(Shop))
        shops = result.scalars().all()
        
        print(f"Найдено магазинов: {len(shops)}")
        
        total_migrated = 0
        
        for shop in shops:
            print(f"\n📦 Обрабатываем магазин '{shop.name}' (ID: {shop.id})")
            
            result = await session.execute(
                select(Chain).where(
                    Chain.shop_id == shop.id,
                    Chain.category_id.is_(None)
                )
            )
            orphan_chains = result.scalars().all()
            
            if not orphan_chains:
                print(f"  ✓ Все цепочки уже привязаны к категориям")
                continue
            
            print(f"  Найдено цепочек без категорий: {len(orphan_chains)}")
            
            result = await session.execute(
                select(Category).where(
                    Category.shop_id == shop.id,
                    Category.name == "Основные",
                    Category.parent_id.is_(None)
                )
            )
            category_level1 = result.scalar_one_or_none()
            
            if not category_level1:
                category_level1 = Category(
                    shop_id=shop.id,
                    name="Основные",
                    parent_id=None
                )
                session.add(category_level1)
                await session.flush()
                print(f"  ✓ Создана категория 1-го уровня: 'Основные' (ID: {category_level1.id})")
            else:
                print(f"  ✓ Найдена категория 1-го уровня: 'Основные' (ID: {category_level1.id})")
            
            result = await session.execute(
                select(Category).where(
                    Category.shop_id == shop.id,
                    Category.name == "Все цепочки",
                    Category.parent_id == category_level1.id
                )
            )
            category_level2 = result.scalar_one_or_none()
            
            if not category_level2:
                category_level2 = Category(
                    shop_id=shop.id,
                    name="Все цепочки",
                    parent_id=category_level1.id
                )
                session.add(category_level2)
                await session.flush()
                print(f"  ✓ Создана категория 2-го уровня: 'Все цепочки' (ID: {category_level2.id})")
            else:
                print(f"  ✓ Найдена категория 2-го уровня: 'Все цепочки' (ID: {category_level2.id})")
            
            for chain in orphan_chains:
                chain.category_id = category_level2.id
                source_title = chain.source_chat_title or f"ID {chain.source_chat_id}"
                print(f"  ✓ Привязана цепочка #{chain.id} ({source_title}) -> '{category_level2.name}'")
                total_migrated += 1
            
            await session.commit()
            print(f"  ✅ Обработано цепочек: {len(orphan_chains)}")
        
        print(f"\n{'='*60}")
        print(f"✅ Миграция завершена успешно!")
        print(f"   Всего мигрировано цепочек: {total_migrated}")
        print(f"{'='*60}")


async def main():
    print("=" * 60)
    print("Миграция цепочек в категории")
    print("=" * 60)
    
    await migrate_chains_to_categories()


if __name__ == "__main__":
    asyncio.run(main())
