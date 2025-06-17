from lib.librun import run_always, run_when
import asyncio
import sys


def get_commands(using_podman: bool) -> tuple[str, str, str]:
    stopneo4j_cmd: str
    startneo4j_cmd: str
    runexport_cmd: str

    if using_podman:
        stopneo4j_cmd = "podman stop digital-twin_neo4j_1"
        startneo4j_cmd = "podman start digital-twin_neo4j_1"
        runexport_cmd = (
            "podman run -it --name=neo4j-export --rm "
            "-v digital-twin_neo4j:/data:z -v ./export/:/var/lib/neo4j/export:U,rw "
            "--user=neo4j:neo4j -t digital-twin_neo4j:latest "
            "neo4j-admin database dump neo4j --to-path=./export --overwrite-destination=true --verbose"
        )

    else:
        stopneo4j_cmd = "docker stop digital-twin-neo4j-1"
        startneo4j_cmd = "docker start digital-twin-neo4j-1"
        runexport_cmd = (
            "docker run -it --name=neo4j-export --rm "
            "-v digital-twin_neo4j:/data -v ./export/:/var/lib/neo4j/export "
            "-u neo4j:neo4j -t digital-twin-neo4j:latest "
            "neo4j-admin database dump neo4j --to-path=./export --overwrite-destination=true --verbose"
        )

    return stopneo4j_cmd, startneo4j_cmd, runexport_cmd


async def main(_program: str, args: list[str]) -> None:
    using_podman = bool(args)
    stopneo4j_cmd, startneo4j_cmd, runexport_cmd = get_commands(using_podman)
    stopcode = await run_always(stopneo4j_cmd)
    _ = await run_always(runexport_cmd)
    _ = await run_when(stopcode == 0, startneo4j_cmd)

if __name__ == "__main__":
    program, *args = sys.argv
    asyncio.run(main(program, args))
