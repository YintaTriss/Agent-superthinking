"""
sanitizer.py - LLM 输出消敏模块

对 LLM 输出进行消敏处理，防止注入攻击和信息泄露。
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# 注入检测模式
INJECTION_PATTERNS = [
    re.compile(r"^ignore\s+(previous|all|above)\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^system\s*:", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^assistant\s*:", re.IGNORECASE | re.MULTILINE),
    re.compile(r"<\|.*?\|>"),  # ChatML control tokens
    re.compile(r"\{\s*\"action\"\s*:\s*\"converge\"", re.IGNORECASE),
]

MAX_CONTENT_LENGTH = 4000  # 最大输出长度


@dataclass
class SanitizedOutput:
    """消敏后的输出"""
    content: str  # 消敏后的内容
    original_length: int  # 原始长度
    blocked: bool  # 是否被拦截
    truncation_applied: bool  # 是否被截断


class OutputSanitizer:
    """
    LLM 输出消敏器。

    对所有 LLM 输出进行消敏处理：
    1. 长度截断（防止长文本注入）
    2. 移除注入指令模式
    3. 移除 markdown code blocks（防止格式化注入）

    用于：
    - LLM 输出进入下一轮 prompt 之前
    - 会话记录写入日志之前
    """

    def __init__(
        self,
        max_length: int = MAX_CONTENT_LENGTH,
        block_patterns: list[re.Pattern] | None = None,
    ):
        self._max_length = max_length
        self._patterns = block_patterns or INJECTION_PATTERNS

    def sanitize(self, content: str) -> SanitizedOutput:
        """
        对 LLM 输出进行消敏。

        Args:
            content: 原始 LLM 输出

        Returns:
            SanitizedOutput 对象
        """
        if not isinstance(content, str):
            content = str(content)

        original_length = len(content)
        blocked = False
        truncation_applied = False

        # 1. 长度截断
        if len(content) > self._max_length:
            content = content[: self._max_length] + f"\n[内容已截断，原始长度: {original_length}]"
            truncation_applied = True

        # 2. 移除 markdown code blocks（防止格式化注入）
        content = re.sub(r"```[^`]*```", "[代码块已移除]", content, flags=re.DOTALL)
        content = re.sub(r"`[^`]*`", "[内联代码已移除]", content)

        # 3. 检测并拦截注入模式
        for pat in self._patterns:
            if pat.search(content):
                logger.warning(f"OutputSanitizer blocked content matching: {pat.pattern}")
                content = "[内容已被安全过滤器拦截]"
                blocked = True
                break

        return SanitizedOutput(
            content=content,
            original_length=original_length,
            blocked=blocked,
            truncation_applied=truncation_applied,
        )

    def sanitize_for_prompt(self, content: str, max_len: int = 150) -> str:
        """
        对 LLM 输出进行消敏，用于嵌入 prompt。

        Args:
            content: 原始 LLM 输出
            max_len: 截断长度（默认 150 字符）

        Returns:
            消敏后的字符串
        """
        result = self.sanitize(content)
        # 嵌入 prompt 时额外截断到 max_len
        if len(result.content) > max_len:
            return result.content[:max_len] + "..."
        return result.content


# 全局默认实例
_default_sanitizer: OutputSanitizer | None = None


def get_sanitizer() -> OutputSanitizer:
    """获取全局默认 sanitizer 实例"""
    global _default_sanitizer
    if _default_sanitizer is None:
        _default_sanitizer = OutputSanitizer()
    return _default_sanitizer


def sanitize_llm_output(content: str) -> str:
    """
    快捷函数：对 LLM 输出进行消敏。

    相当于 get_sanitizer().sanitize(content).content
    """
    return get_sanitizer().sanitize(content).content
