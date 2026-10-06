"""QQ 官方机器人把 QQ 昵称透传给 core 的 ``sender["nickname"]``。

adapter-qq 自 #188 起在 ``author`` 上返回 ``username``（群成员/好友都有）；
连接器必须把它带出去，否则 core 侧 ``event.sender`` 没有 ``nickname``，
消息历史与 user/group 表都记不到名字。
"""

from __future__ import annotations

import pytest
import nonebot

pytest.importorskip("nonebot.adapters.qq", reason="需要安装 nonebot-adapter-qq")

nonebot.init(driver="~none")

from nonebot.adapters.qq.event import (  # noqa: E402
    C2CMessageCreateEvent,
    GroupMessageCreateEvent,
    GroupAtMessageCreateEvent,
)

from GenshinUID.receive import _sender_qq  # noqa: E402

_BASE: dict[str, object] = {
    "id": "message-id",
    "content": "hello",
    "timestamp": "2026-08-05T12:51:27+08:00",
    "time": "2026-08-05T12:51:27+08:00",
    "self_id": "BOT",
}


def _group_author(nickname: str | None) -> dict[str, object]:
    author: dict[str, object] = {
        "id": "SENDER",
        "bot": False,
        "member_openid": "MEMBER_OPENID",
        "member_role": "member",
    }
    if nickname is not None:
        author["username"] = nickname
    return author


def _group_event(nickname: str | None) -> GroupMessageCreateEvent:
    return GroupMessageCreateEvent(
        **_BASE,
        author=_group_author(nickname),
        group_id="GROUP",
        group_openid="GROUP_OPENID",
    )


def _at_event(nickname: str | None) -> GroupAtMessageCreateEvent:
    return GroupAtMessageCreateEvent(
        **_BASE,
        author=_group_author(nickname),
        group_id="GROUP",
        group_openid="GROUP_OPENID",
    )


def _c2c_event(nickname: str | None) -> C2CMessageCreateEvent:
    author: dict[str, object] = {"id": "SENDER", "user_openid": "USER_OPENID_ABCD"}
    if nickname is not None:
        author["username"] = nickname
    return C2CMessageCreateEvent(**_BASE, author=author)


def test_group_message_carries_username() -> None:
    sender = _sender_qq(_group_event("张三"), "MEMBER_OPENID", "BOT_SELF_ID")
    assert sender["nickname"] == "张三"
    assert sender["avatar"] == "https://q.qlogo.cn/qqapp/BOT_SELF_ID/MEMBER_OPENID/0"


def test_group_at_message_carries_username() -> None:
    sender = _sender_qq(_at_event("李四"), "MEMBER_OPENID", "BOT_SELF_ID")
    assert sender["nickname"] == "李四"


def test_group_message_without_username_keeps_avatar_only() -> None:
    """老 payload 没有 username，维持原来只发头像，不要拿 openid 冒充昵称。"""
    sender = _sender_qq(_group_event(None), "MEMBER_OPENID", "BOT_SELF_ID")
    assert "nickname" not in sender
    assert "avatar" in sender


def test_c2c_message_carries_username() -> None:
    sender = _sender_qq(_c2c_event("王五"), "USER_OPENID", "BOT_SELF_ID")
    assert sender["nickname"] == "王五"


def test_c2c_message_without_username_falls_back_to_placeholder() -> None:
    sender = _sender_qq(_c2c_event(None), "USER_OPENID", "BOT_SELF_ID")
    assert sender["nickname"] == "QQ用户USER"
