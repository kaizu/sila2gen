# sila2gen

Install [sila_python](https://gitlab.com/kaizu1/sila_python/-/tree/sila2gen?ref_type=heads).

```shell-session
$  uv pip install -e ./sila_python[codegen]
```

Generate server files.

```shell-session
$ CODE_GENERATOR_TEMPLATES_PATH=./code_generator_templates uv run python generate_feature_xml.py
$ ls servers
```

Run them on Docker.

```shell-session
$ docker compose up -d
$ uv run python client.py
```
