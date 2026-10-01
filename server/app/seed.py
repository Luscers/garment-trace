"""Seed demo factory / products / batches / codes and admin user."""

from datetime import date
import secrets

from passlib.context import CryptContext

from .database import Base, SessionLocal, engine
from .models import Batch, Factory, Product, TraceCode, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEMO_CODES = {
    "GT2026A01": "GT-A01-8F3K2M",
    "GT2026A02": "GT-A02-5R9W1P",
    "GT2026B01": "GT-B01-7N4Q6X",
}


def _timeline(batch: Batch, product: Product) -> list[dict]:
    d = batch.production_date or date(2026, 9, 12)
    return [
        {"step": "原料入库", "time": f"{d.isoformat()} 09:20", "note": "面料/里料检验合格入库"},
        {"step": "裁剪缝制", "time": f"{d.isoformat()} 13:40", "note": f"{batch.workshop or '一车间'} 流水线作业"},
        {"step": "成衣检验", "time": f"{d.isoformat()} 17:10", "note": f"检验员 {batch.inspector or '王敏'} · {batch.grade or '合格'}"},
        {"step": "包装出库", "time": f"{d.isoformat()} 18:30", "note": "吊牌赋码 · 批次挂签"},
    ]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Factory).count() == 0:
            factory = Factory(
                name="宁波雅澜服饰有限公司",
                brand="雅澜 YALAN",
                address="浙江省宁波市海曙区望春工业园雅澜路 18 号",
                license_no="91330200MA2AF1XY3K",
                contact="品质管理部",
                phone="0574-8888-6688",
                intro="专注中高端女装成衣制造 18 年，服务国内外品牌 OEM/ODM，通过 ISO9001 质量管理体系认证。",
            )
            db.add(factory)
            db.flush()

            products = [
                Product(
                    factory_id=factory.id,
                    style_no="YL-W-2601",
                    name="精纺羊毛大衣",
                    category="女装 / 大衣",
                    composition="80% 羊毛 · 20% 聚酯纤维",
                    standard_no="GB/T 2666-2017",
                    color="燕麦色",
                    size_range="S / M / L / XL",
                    care="干洗 · 低温熨烫 · 悬挂收纳",
                ),
                Product(
                    factory_id=factory.id,
                    style_no="YL-S-2618",
                    name="真丝印花连衣裙",
                    category="女装 / 连衣裙",
                    composition="100% 桑蚕丝",
                    standard_no="GB/T 18132-2016",
                    color="墨绿提花",
                    size_range="S / M / L",
                    care="手洗或干洗 · 避光晾干",
                ),
                Product(
                    factory_id=factory.id,
                    style_no="YL-M-2630",
                    name="精梳棉衬衫",
                    category="男装 / 衬衫",
                    composition="100% 长绒棉",
                    standard_no="GB/T 2660-2017",
                    color="雾蓝",
                    size_range="38 / 39 / 40 / 41 / 42",
                    care="机洗温和 · 中温熨烫",
                ),
            ]
            db.add_all(products)
            db.flush()

            batches = [
                Batch(
                    product_id=products[0].id,
                    factory_id=factory.id,
                    batch_no="20260912-W",
                    production_date=date(2026, 9, 12),
                    inspector="王敏",
                    workshop="一车间",
                    grade="一等品",
                ),
                Batch(
                    product_id=products[1].id,
                    factory_id=factory.id,
                    batch_no="20260918-S",
                    production_date=date(2026, 9, 18),
                    inspector="陈晓",
                    workshop="精品线",
                    grade="一等品",
                ),
                Batch(
                    product_id=products[2].id,
                    factory_id=factory.id,
                    batch_no="20260922-M",
                    production_date=date(2026, 9, 22),
                    inspector="李强",
                    workshop="二车间",
                    grade="合格品",
                ),
            ]
            db.add_all(batches)
            db.flush()

            for batch, code in zip(batches, DEMO_CODES.values()):
                db.add(
                    TraceCode(
                        code=code,
                        batch_id=batch.id,
                        factory_id=factory.id,
                        status="active",
                    )
                )

        if db.query(User).filter(User.username == "admin").count() == 0:
            db.add(
                User(
                    username="admin",
                    password_hash=pwd_context.hash("yalan2026"),
                    role="admin",
                )
            )

        db.commit()
    finally:
        db.close()


def generate_code() -> str:
    return "GT-" + secrets.token_hex(4).upper()
