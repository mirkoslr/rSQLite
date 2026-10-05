def link(label, target, params=None, color=None):
    parts = []

    if params:
        for param in params:
            if isinstance(param, tuple):
                key, value = param
                parts.append(f"{key}={value}")
            else:
                parts.append(str(param))

    arguments = "|".join(parts)

    if arguments:
        target = f"{target}`{arguments}"

    result = f"`[{label}`:{target}]`"

    if color:
        result = f"`{color}{result}`"

    return result

