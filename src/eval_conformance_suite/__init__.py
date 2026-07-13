def run(*args, **kwargs):
    from .runner import run as _run

    return _run(*args, **kwargs)


def badge(*args, **kwargs):
    from .badge import badge as _badge

    return _badge(*args, **kwargs)


__all__ = ["run", "badge"]
