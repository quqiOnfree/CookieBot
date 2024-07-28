from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from nonebot import on_command, on_request
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, GroupRequestEvent, Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="JoinMessage",
    description="",
    usage="",
    config=Config,
)

plugin_config = get_plugin_config(Config)

request = on_request(priority=1, block=True)
@request.handle()
async def request_handle(bot: Bot, event: GroupRequestEvent, state: T_State):
    if str(event.group_id) not in plugin_config.config_group:
        return
    await bot.send_group_msg(group_id=event.group_id, message="""有新的入群申请
» 申请人 {}
» 答案     {}

回复此消息:/同意 /拒绝""".format(event.user_id, event.get_message()))
    state[str(event.group_id)] = event

agree = on_command('同意', aliases={'/agree', '/同意'}, priority=1, block=True,
                   permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER)
@agree.handle()
async def agree_handle(bot: Bot, event: GroupMessageEvent, state: T_State):
    if str(event.group_id) not in plugin_config.config_group:
        return
    if str(event.group_id) not in state.keys():
        await agree.finish("错误：没有需要同意的请求")
    await state[str(event.group_id)].approve(bot)
    await agree.finish("同意成功")

reject = on_command('拒绝', aliases={'/reject', '/拒绝'}, priority=1, block=True,
                    permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER)
@reject.handle()
async def reject_handle(bot: Bot, event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    if str(event.group_id) not in plugin_config.config_group:
        return
    if str(event.group_id) not in state.keys():
        await agree.finish("错误：没有需要拒绝的请求")
    if reason := args.extract_plain_text():
        await state[str(event.group_id)].reject(bot, reason=reason)
    await state[str(event.group_id)].reject(bot, reason='答案未通过群管验证，可修改答案后再次申请')
    await reject.finish("同意成功")
    