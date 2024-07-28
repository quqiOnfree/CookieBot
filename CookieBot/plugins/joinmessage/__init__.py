#   This is a group operation bot for QQ.
#   Copyright (C) 2024  Xuan Xiao

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published
#   by the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.

#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command, on_request
from nonebot.adapters.onebot.v11 import GroupMessageEvent, GroupRequestEvent, Bot, Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER

import json

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="JoinMessage",
    description="",
    usage="",
    config=Config,
)

plugin_config = get_plugin_config(Config)

request_list = {}

request = on_request(priority=1, block=True)
@request.handle()
async def request_handle(bot: Bot, event: GroupRequestEvent):
    if str(event.group_id) not in plugin_config.config_group:
        return
    if str(event.group_id) not in request_list.keys():
        request_list[str(event.group_id)] = {}
    request_list[str(event.group_id)][str(event.user_id)] = event
    await bot.send_group_msg(group_id=event.group_id, message="""有新的入群申请
» 申请人 {}
{}

回复此消息:/同意 {}
/拒绝 {} 原因

若拒绝需要填写拒绝原因""".format(event.user_id, json.loads(event.model_dump_json())["comment"]), event.user_id, event.user_id)

agree = on_command('同意', aliases={'/agree', '/同意'}, priority=1, block=True,
                   permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER)
@agree.handle()
async def agree_handle(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if str(event.group_id) not in plugin_config.config_group:
        return
    if str(event.group_id) not in request_list.keys():
        await agree.finish("错误：没有需要同意的请求")
    if len(args.extract_plain_text()) == 0:
        await agree.finish("必须带上用户qq号")
    qq = 0
    try:
        qq = int(args.extract_plain_text())
    except:
        await agree.finish("参数要为qq号")
    try:
        await request_list[str(event.group_id)][str(qq)].approve(bot)
    except:
        pass
    del request_list[str(event.group_id)][str(qq)]
    await agree.finish("同意成功")

reject = on_command('拒绝', aliases={'/reject', '/拒绝'}, priority=1, block=True,
                    permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER)
@reject.handle()
async def reject_handle(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if str(event.group_id) not in plugin_config.config_group:
        return
    if str(event.group_id) not in request_list.keys():
        await agree.finish("错误：没有需要拒绝的请求")
    if len(args.extract_plain_text()) == 0:
        await reject.finish("拒绝需要理由")
    orgin = args.extract_plain_text().split(' ')
    if len(orgin) < 2:
        await reject.finish("拒绝需要qq号和理由")
    qq = 0
    try:
        qq = int(orgin[0])
    except:
        await reject.finish("参数要为qq号")
    if str(qq) not in request_list[str(event.group_id)].keys():
        await agree.finish("错误：没有需要拒绝的请求")
    try:
        await request_list[str(event.group_id)][str(qq)].reject(bot, reason=orgin[1])
    except:
        pass
    del request_list[str(event.group_id)][str(qq)]
    await reject.finish("拒绝成功")
    
