from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import engine, async_session_maker
from app.models import Category, Role, SitePage, User


ROLE_SEEDS = [
    {"name": "admin", "display_name": "管理员", "color": "#F56C6C", "priority": 100},
    {"name": "super_moderator", "display_name": "超级版主", "color": "#E6A23C", "priority": 80},
    {"name": "moderator", "display_name": "版主", "color": "#409EFF", "priority": 60},
    {"name": "verified_member", "display_name": "认证会员", "color": "#67C23A", "priority": 40},
    {"name": "member", "display_name": "普通会员", "color": "#909399", "priority": 20},
    {"name": "muted", "display_name": "禁言用户", "color": "#303133", "priority": 10},
]

DEFAULT_CATEGORIES = [
    {"name": "综合讨论", "description": "技术交流与日常讨论", "type": "forum", "sort_order": 1},
    {"name": "学科竞赛", "description": "竞赛资讯与经验分享", "type": "contest", "sort_order": 2},
    {"name": "项目开发招募", "description": "项目招募专区", "type": "recruit_project", "sort_order": 3},
    {"name": "竞赛组队招募", "description": "组队与招募专区", "type": "recruit_team", "sort_order": 4},
    {"name": "官方公告", "description": "管理员公告板块", "type": "notice", "sort_order": 5},
]

DEFAULT_PAGES = [
    {"slug": "home", "title": "TensorHub 首页", "content": "欢迎来到 TensorHub 社区。"},
    {"slug": "about", "title": "关于 TensorHub", "content": "这里是 TensorHub 团队介绍页面。"},
]


async def bootstrap_data() -> None:
    settings = get_settings()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        for role_data in ROLE_SEEDS:
            exists = await session.execute(select(Role).where(Role.name == role_data["name"]))
            if not exists.scalar_one_or_none():
                session.add(Role(**role_data))

        for category_data in DEFAULT_CATEGORIES:
            exists = await session.execute(select(Category).where(Category.name == category_data["name"]))
            if not exists.scalar_one_or_none():
                session.add(Category(**category_data))

        for page_data in DEFAULT_PAGES:
            exists = await session.execute(select(SitePage).where(SitePage.slug == page_data["slug"]))
            if not exists.scalar_one_or_none():
                session.add(SitePage(**page_data))

        await session.commit()

        admin_result = await session.execute(select(User).where(User.username == settings.bootstrap_admin_username))
        admin_user = admin_result.scalar_one_or_none()
        if not admin_user:
            role_result = await session.execute(select(Role).where(Role.name.in_(["admin", "verified_member"])))
            roles = list(role_result.scalars().all())
            admin_user = User(
                username=settings.bootstrap_admin_username,
                password_hash=hash_password(settings.bootstrap_admin_password),
                email=settings.bootstrap_admin_email,
                real_name=settings.bootstrap_admin_real_name,
                gender=settings.bootstrap_admin_gender,
                major=settings.bootstrap_admin_major,
                student_id=settings.bootstrap_admin_student_id,
                verification_status="approved",
                roles=roles,
            )
            session.add(admin_user)
            await session.commit()
