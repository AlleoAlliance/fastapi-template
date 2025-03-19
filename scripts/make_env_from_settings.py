import os
import sys
from os.path import dirname, join, basename
import json
from typing import List

from pydantic import ValidationError
from pydantic_settings import BaseSettings

__dirname = dirname(__file__)
sys.path.append(join(__dirname, '..'))
os.environ['IGNORE_SETTINGS'] = '1'

from config_env import ENV_DIR, check_env_exists, CHANGE_THIS, ENVS  # noqa
from config import get_settings_class, get_settings  # noqa


def generate_dotenv(settings: BaseSettings, settings_class: BaseSettings) -> str:
    """Generate a .env template based on the Pydantic Settings class."""
    fields = settings_class.model_fields
    lines = []
    settings = settings.model_dump() if settings else {}
    for field_name, field_info in fields.items():
        title = field_info.title or 'No description available'
        default = field_info.get_default()
        value = settings.get(field_name) or default
        comment = f'# {title}'
        if value is CHANGE_THIS:
            comment += ' (*REQUIRED)'
        lines.append(comment)
        if value is None or value is CHANGE_THIS:
            lines.append(f'{field_name}=')
        else:
            lines.append(f'{field_name}={json.dumps(value)}')
        lines.append('')

    return '\n'.join(lines)


def main(args: List[str] = None):
    args = args or sys.argv[1:]
    if '-h' in args:
        print(f'Usage: python {sys.argv[0]} [-f] [-e env_name {{{",".join(ENVS)}}}]')
        print('  -f: 强制生成 .env 文件，即使已经存在')
        print(f'  -e: 指定环境，{",".join(ENVS)}，（未指定生成所有环境的配置文件）')
        return
    if '-e' in args:
        env_name = args[args.index('-e') + 1]
        if env_name not in ENVS:
            print(f'[-] 错误的环境名称: {env_name}')
            return
        env_files = [join(ENV_DIR, f'.env.{env_name}')]
    else:
        env_files = [join(ENV_DIR, f'.env.{env_name}') for env_name in ENVS]
    for env_file in env_files:
        if check_env_exists(env_file) and '-f' not in args:
            print(f'[~] 已经存在 .env: {env_file}', '可使用 -f 强制生成')
            return
    try:
        settings = get_settings()
    except ValidationError:
        settings = None
    for env_file in env_files:
        with open(env_file, 'w', encoding='utf8') as ef:
            ef.write(generate_dotenv(settings, get_settings_class(basename(env_file)[5:])))
            print(f'[+] 已生成 .env 文件: {env_file}')


if __name__ == '__main__':
    main()
