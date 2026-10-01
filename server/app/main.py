from datetime import datetime, timezone
from pathlib import Path

import jwt
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Batch, Factory, Product, TraceCode, User
from .schemas import ApiMessage, CodeToggle, LoginRequest, TraceBatch, TraceCard, TraceFactory, TraceProduct
from .seed import generate_code, seed

SECRET_KEY = "garment-trace-demo-secret"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="服装二维码溯源 Demo", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

seed()


def ok(data=None, message="ok") -> JSONResponse:
    return JSONResponse({"code": 0, "message": message, "data": data})


def fail(message: str, code: int = 1, status: int = 400) -> JSONResponse:
    return JSONResponse({"code": code, "message": message, "data": None}, status_code=status)


def build_timeline(batch: Batch, product: Product) -> list[dict]:
    d = batch.production_date.isoformat() if batch.production_date else "—"
    return [
        {"step": "原料入库", "time": f"{d} 09:20", "note": "面料/里料检验合格入库"},
        {"step": "裁剪缝制", "time": f"{d} 13:40", "note": f"{batch.workshop or '一车间'} 流水线作业"},
        {
            "step": "成衣检验",
            "time": f"{d} 17:10",
            "note": f"检验员 {batch.inspector or '—'} · {batch.grade or '合格'}",
        },
        {"step": "包装出库", "time": f"{d} 18:30", "note": "吊牌赋码 · 批次挂签"},
    ]


@app.get("/api/trace/{code}")
def get_trace(code: str, db: Session = Depends(get_db)):
    row = (
        db.query(TraceCode)
        .filter(TraceCode.code == code.upper())
        .first()
    )
    if not row:
        return fail("未查询到溯源信息", code=404, status=404)
    if row.status != "active":
        return fail("该溯源码已停用", code=403, status=403)

    batch = db.get(Batch, row.batch_id)
    product = db.get(Product, batch.product_id)
    factory = db.get(Factory, product.factory_id)

    card = TraceCard(
        code=row.code,
        verified=True,
        queried_at=datetime.now(timezone.utc),
        factory=TraceFactory(
            name=factory.name,
            brand=factory.brand,
            address=factory.address,
            license_no=factory.license_no,
            contact=factory.contact,
            phone=factory.phone,
            intro=factory.intro,
        ),
        product=TraceProduct(
            style_no=product.style_no,
            name=product.name,
            category=product.category,
            composition=product.composition,
            standard_no=product.standard_no,
            color=product.color,
            size_range=product.size_range,
            care=product.care,
        ),
        batch=TraceBatch(
            batch_no=batch.batch_no,
            production_date=batch.production_date,
            inspector=batch.inspector,
            workshop=batch.workshop,
            grade=batch.grade,
        ),
        timeline=build_timeline(batch, product),
    )
    return ok(card.model_dump(mode="json"))


@app.post("/api/admin/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not pwd_context.verify(payload.password, user.password_hash):
        return fail("账号或密码错误", code=401, status=401)
    token = jwt.encode(
        {"sub": user.username, "role": user.role, "exp": datetime.now(timezone.utc).timestamp() + 86400},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return ok({"token": token, "username": user.username, "role": user.role})


def get_token(
    authorization: str | None = Header(default=None),
    token: str | None = Header(default=None),
) -> str:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip()
    if token:
        return token.strip()
    if authorization:
        return authorization.strip()
    return ""


def require_admin(token: str, db: Session) -> User:
    if not token:
        raise HTTPException(status_code=401, detail="未登录或登录已过期")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="未登录或登录已过期")
    user = db.query(User).filter(User.username == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


@app.get("/api/admin/summary")
def admin_summary(db: Session = Depends(get_db), token: str = Depends(get_token)):
    require_admin(token, db)
    return ok(
        {
            "products": db.query(Product).count(),
            "batches": db.query(Batch).count(),
            "codes": db.query(TraceCode).count(),
            "active_codes": db.query(TraceCode).filter(TraceCode.status == "active").count(),
        }
    )


@app.get("/api/admin/codes")
def admin_codes(db: Session = Depends(get_db), token: str = Depends(get_token)):
    require_admin(token, db)
    rows = (
        db.query(TraceCode, Batch, Product, Factory)
        .join(Batch, TraceCode.batch_id == Batch.id)
        .join(Product, Batch.product_id == Product.id)
        .join(Factory, Product.factory_id == Factory.id)
        .order_by(TraceCode.id.desc())
        .all()
    )
    items = []
    for code, batch, product, factory in rows:
        items.append(
            {
                "id": code.id,
                "code": code.code,
                "status": code.status,
                "style_no": product.style_no,
                "product_name": product.name,
                "batch_no": batch.batch_no,
                "factory_name": factory.name,
                "production_date": batch.production_date.isoformat() if batch.production_date else "",
            }
        )
    return ok(items)


class ImportRow(BaseModel):
    style_no: str
    name: str
    composition: str = ""
    standard_no: str = ""
    batch_no: str
    production_date: str = ""
    inspector: str = ""
    factory_name: str = ""
    factory_address: str = ""


class ImportPayload(BaseModel):
    rows: list[ImportRow]


@app.post("/api/admin/import")
def admin_import(payload: ImportPayload, db: Session = Depends(get_db), token: str = Depends(get_token)):
    require_admin(token, db)
    factory = db.query(Factory).first()
    created = []
    errors = []
    for i, row in enumerate(payload.rows, start=1):
        if not row.style_no or not row.batch_no:
            errors.append({"row": i, "reason": "style_no 与 batch_no 必填"})
            continue
        product = (
            db.query(Product)
            .filter(Product.factory_id == factory.id, Product.style_no == row.style_no)
            .first()
        )
        if not product:
            product = Product(
                factory_id=factory.id,
                style_no=row.style_no,
                name=row.name or row.style_no,
                composition=row.composition,
                standard_no=row.standard_no,
            )
            db.add(product)
            db.flush()
        batch = (
            db.query(Batch)
            .filter(Batch.product_id == product.id, Batch.batch_no == row.batch_no)
            .first()
        )
        if not batch:
            batch = Batch(
                product_id=product.id,
                factory_id=factory.id,
                batch_no=row.batch_no,
                inspector=row.inspector,
            )
            db.add(batch)
            db.flush()
        code = generate_code()
        while db.query(TraceCode).filter(TraceCode.code == code).first():
            code = generate_code()
        db.add(TraceCode(code=code, batch_id=batch.id, factory_id=factory.id))
        created.append({"row": i, "code": code, "style_no": row.style_no, "batch_no": row.batch_no})

    if errors:
        db.rollback()
        return fail(f"导入失败：{errors[0]['reason']}（第 {errors[0]['row']} 行）", code=2)
    db.commit()
    return ok({"created": created}, message=f"成功生成 {len(created)} 个溯源码")


@app.patch("/api/admin/codes/{code_id}")
def toggle_code(code_id: int, payload: CodeToggle, db: Session = Depends(get_db), token: str = Depends(get_token)):
    require_admin(token, db)
    row = db.get(TraceCode, code_id)
    if not row:
        return fail("码不存在", code=404, status=404)
    if payload.status not in {"active", "disabled"}:
        return fail("status 仅支持 active/disabled")
    row.status = payload.status
    db.commit()
    return ok({"id": row.id, "status": row.status})


@app.get("/api/demo/codes")
def demo_codes(db: Session = Depends(get_db)):
    rows = db.query(TraceCode).order_by(TraceCode.id).all()
    return ok([row.code for row in rows])


@app.get("/api/health")
def health():
    return ok({"status": "up"})


@app.get("/t/{code}")
def trace_page(code: str):
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/admin")
def admin_page():
    return FileResponse(STATIC_DIR / "admin.html")


@app.get("/demo")
def demo_page():
    return FileResponse(STATIC_DIR / "demo.html")


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
