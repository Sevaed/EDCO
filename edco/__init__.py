try:
    from importlib.metadata import version as _pkg_version
    __version__ = _pkg_version("edco")
except Exception:
    # когда пакет ещё не установлен (локальные запуски), пусть будет "0.0.0"
    __version__ = "0.0.0"
