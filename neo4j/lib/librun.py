import asyncio


async def run_always(proc_cmd: str) -> int:
    print(f"\u001b[32m+ {proc_cmd}\u001b[0m")
    proc = await asyncio.create_subprocess_shell(proc_cmd)
    await proc.communicate()
    if proc.returncode is None:
        return 1
    return proc.returncode


async def run_when(run: bool, proc_cmd: str) -> int:
    if run:
        return await run_always(proc_cmd)
    return 0
