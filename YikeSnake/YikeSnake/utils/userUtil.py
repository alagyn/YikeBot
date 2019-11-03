# userUtil.py


def getId(rawId):
    if rawId[2] == '!':
        return rawId[3:-1]
    else:
        return rawId[2:-1]


def getName(guild, userId):
    name = ''
    for m in guild.members:
        if userId == str(m.id):
            if m.nick is not None:
                name = m.nick
            else:
                name = m.name
            break
    return name
