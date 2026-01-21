"""System settings service."""

from sqlalchemy.ext.asyncio import AsyncSession

from models.system_parameter import SystemParameter
from repositories.system_parameter import SystemParameterRepository


class SettingsService:
    """Service for system settings operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.param_repo = SystemParameterRepository(session)

    async def get_all(self) -> list[SystemParameter]:
        """Get all system parameters."""
        return await self.param_repo.get_all()

    async def get_by_name(self, name: str) -> SystemParameter | None:
        """Get parameter by name."""
        return await self.param_repo.get_by_name(name)

    async def get_value(self, name: str, default: str | None = None) -> str | None:
        """Get parameter value by name."""
        return await self.param_repo.get_value(name, default)

    async def set_value(
        self,
        name: str,
        value: str,
        description: str | None = None,
    ) -> SystemParameter:
        """Set parameter value."""
        return await self.param_repo.set_value(name, value, description)

    async def get_float(self, name: str, default: float = 0.0) -> float:
        """Get parameter value as float."""
        value = await self.get_value(name)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default

    async def get_int(self, name: str, default: int = 0) -> int:
        """Get parameter value as integer."""
        value = await self.get_value(name)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    async def get_bool(self, name: str, default: bool = False) -> bool:
        """Get parameter value as boolean."""
        value = await self.get_value(name)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")
