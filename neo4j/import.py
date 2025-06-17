from lib.librun import run_always, run_when
import asyncio
import sys


def get_commands(using_podman: bool) -> tuple[str, str, str]:
    stopneo4j_cmd: str
    startneo4j_cmd: str
    runimport_cmd: str

    if using_podman:
        stopneo4j_cmd = "podman stop digital-twin_neo4j_1"
        startneo4j_cmd = "podman start digital-twin_neo4j_1"
        runimport_cmd = (
            "podman run -it --name=neo4j-import --rm "
            "-v digital-twin_neo4j:/data:z -v ./import/:/var/lib/neo4j/backup:U,ro "
            "-u neo4j:neo4j -t digital-twin_neo4j:latest "
            "neo4j-admin database load neo4j --from-path=./backup --overwrite-destination=true --verbose"
        )

    else:
        stopneo4j_cmd = "docker stop digital-twin-neo4j-1"
        startneo4j_cmd = "docker start digital-twin-neo4j-1"
        runimport_cmd = (
            "docker run -it --name=neo4j-import --rm "
            "-v digital-twin_neo4j:/data -v ./import/:/var/lib/neo4j/backup "
            "-u neo4j:neo4j -t digital-twin-neo4j:latest "
            "neo4j-admin database load neo4j --from-path=./backup --overwrite-destination=true --verbose"
        )

    return stopneo4j_cmd, startneo4j_cmd, runimport_cmd

async def main(_program: str, args: list[str]) -> None:
    use_podman = bool(args)
    stopneo4j_cmd, startneo4j_cmd, runimport_cmd = get_commands(use_podman)
    stopcode = await run_always(stopneo4j_cmd)
    _ = await run_always(runimport_cmd)
    _ = await run_when(stopcode == 0, startneo4j_cmd)

if __name__ == "__main__":
    program, *args = sys.argv
    asyncio.run(main(program, args))
