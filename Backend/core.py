import asyncio

_main_executor = None
_main_loop = None


def set_main_executor(executor, loop):
    """
    Register main async AI executor
    """
    global _main_executor, _main_loop
    _main_executor = executor
    _main_loop = loop


def call_main_executor(command):
    """
    Safely send command to main async AI
    """
    if _main_executor is None or _main_loop is None:
        print("⚠️ Main executor not ready")
        return False

    try:
        future = asyncio.run_coroutine_threadsafe(
            _main_executor(command),
            _main_loop
        )

        return future  # return future instead of bool

    except Exception as e:
        print("Executor error:", e)
        return False
