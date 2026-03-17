"""
数据库基础模型
所有模型的基类，包含公共字段和方法
"""

from datetime import datetime, timezone
from typing import Any, Dict
from uuid import UUID, uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """
    SQLAlchemy 声明式基类
    所有模型的共同基类
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        自动生成表名
        将类名转换为复数形式（简单实现）
        例如: User -> users, UserRole -> user_roles
        """
        name = cls.__name__
        if name.endswith("y"):
            return name[:-1] + "ies"
        elif name.endswith("s"):
            return name + "es"
        else:
            return name + "s"

    # 类型注解映射
    type_annotation_map = {
        UUID: PGUUID(as_uuid=True),
        datetime: DateTime(timezone=True),
    }


class TimestampMixin:
    """
    时间戳混入类
    提供 created_at 和 updated_at 字段
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )


class SoftDeleteMixin:
    """
    软删除混入类
    提供 deleted_at 字段，支持软删除
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="删除时间（软删除）",
    )

    def soft_delete(self) -> None:
        """软删除标记"""
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        """恢复软删除"""
        self.deleted_at = None

    @property
    def is_deleted(self) -> bool:
        """检查是否已软删除"""
        return self.deleted_at is not None


class UUIDMixin:
    """
    UUID主键混入类
    提供 id 字段作为UUID主键
    """

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
        comment="主键ID",
    )


class AuditMixin:
    """
    审计混入类
    提供创建者和更新者跟踪
    """

    created_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
        default=None,
        comment="创建者ID",
    )

    updated_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
        default=None,
        comment="更新者ID",
    )


# 常用基础模型组合
class BaseModel(Base, UUIDMixin, TimestampMixin):
    """
    基础模型
    包含ID、创建时间、更新时间
    """
    __abstract__ = True

    def to_dict(self, exclude: list[str] | None = None) -> Dict[str, Any]:
        """
        将模型转换为字典
        排除指定的字段
        """
        if exclude is None:
            exclude = []

        result = {}
        for column in self.__table__.columns:
            column_name = column.name
            if column_name in exclude:
                continue

            value = getattr(self, column_name)
            # 处理特殊类型
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, UUID):
                value = str(value)

            result[column_name] = value

        return result

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """
        从字典更新模型属性
        只更新存在的字段
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


class BaseModelWithSoftDelete(BaseModel, SoftDeleteMixin):
    """
    带软删除的基础模型
    """
    __abstract__ = True


class BaseModelWithAudit(BaseModel, AuditMixin):
    """
    带审计的基础模型
    """
    __abstract__ = True


class BaseModelWithSoftDeleteAndAudit(BaseModel, SoftDeleteMixin, AuditMixin):
    """
    带软删除和审计的基础模型
    """
    __abstract__ = True