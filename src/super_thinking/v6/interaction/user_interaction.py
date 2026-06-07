"""UserInteraction — v6 外部用户交互接口"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@runtime_checkable
class UserInteraction(Protocol):
    """用户交互协议。主持人用此向用户提问或请求澄清。"""

    def request_clarification(self, question: str, options: list[str]) -> str:
        """向用户请求澄清，返回用户选择的选项。"""
        ...

    def notify(self, message: str) -> None:
        """向用户发送通知（不等待回复）。"""
        ...


@dataclass
class NoOpInteraction:
    """无操作交互——用于不需要用户交互的场景（如纯批量处理）。"""

    def request_clarification(self, question: str, options: list[str]) -> str:
        return options[0] if options else ""

    def notify(self, message: str) -> None:
        pass
