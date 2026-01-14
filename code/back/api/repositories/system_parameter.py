"""System parameter repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.system_parameter import SystemParameter
from repositories.base import BaseRepository


class SystemParameterRepository(BaseRepository[SystemParameter]):
    """Repository for SystemParameter model operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SystemParameter)

    async def get_by_name(self, name: str) -> SystemParameter | None:
        """Get parameter by name."""
        result = await self.session.execute(
            select(SystemParameter).where(SystemParameter.parameter_name == name)
        )
        return result.scalar_one_or_none()

    async def get_value(self, name: str, default: str | None = None) -> str | None:
        """Get parameter value by name, with optional default."""
        param = await self.get_by_name(name)
        if param:
            return param.parameter_value
        return default

    async def set_value(self, name: str, value: str, description: str | None = None) -> SystemParameter:
        """Set parameter value, creating if it doesn't exist."""
        param = await self.get_by_name(name)
        if param:
            param.parameter_value = value
            if description:
                param.description = description
            await self.session.commit()
            await self.session.refresh(param)
            return param
        else:
            new_param = SystemParameter(
                parameter_name=name,
                parameter_value=value,
                description=description,
            )
            return await self.create(new_param)
