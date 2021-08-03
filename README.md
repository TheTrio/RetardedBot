# RetardedBot

A silly Discord Bot I made

## Set up debugging

```
// tasks.json
{
    "version": "2.0.0",
    "tasks": [
        {
            "type": "docker-build",
            "label": "docker-build",
            "platform": "python",
            "dockerBuild": {
                "tag": "retardedbot/debug:latest",
                "dockerfile": "${workspaceFolder}/Dockerfile",
                "context": "${workspaceFolder}",
                "pull": true
            }
        },
        {
            "type": "docker-run",
            "label": "docker-run: debug",
            "dependsOn": ["docker-build"],
            "python": {
                "file": "src/Main.py"
            },
            "dockerRun": {
                "volumes": [
                    {
                        "containerPath": "/app/data",
                        "localPath": "${workspaceFolder}/data"
                    }
                ],
                "envFiles": [".env"],
                "env": {
                    "PYTHONPATH": "/app"
                }
            }
        }
    ]
}
```

## How to run tests

Simply run [pytest](https://docs.pytest.org/en/6.2.x/contents.html) to run all the tests.

```
$ pytest
```
