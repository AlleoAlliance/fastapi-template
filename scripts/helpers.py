from datetime import datetime
from os import PathLike
from os.path import dirname, join, isabs
import json


def split_upgrade_downgrade_script(script: str):
    """
    Splits an upgrade/downgrade script into its upgrade and downgrade parts.
    :param script: A string containing the script.
    :return: A tuple containing two lists: the upgrade script and the downgrade script.
    """
    UPGRADE_FLAG = '-- region upgrade'
    DOWNGRADE_FLAG = '-- region downgrade'
    ENDREGION_FLAG = '-- endregion'

    lines = script.splitlines()
    upgrade_script = []
    downgrade_script = []

    current_region = None
    for line in lines:
        if UPGRADE_FLAG in line:
            current_region = 'upgrade'
            continue
        elif DOWNGRADE_FLAG in line:
            current_region = 'downgrade'
            continue
        elif ENDREGION_FLAG in line:
            current_region = None
            continue

        if current_region == 'upgrade':
            upgrade_script.append(line)
        elif current_region == 'downgrade':
            downgrade_script.append(line)

    return upgrade_script, downgrade_script


def get_current_time() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def read_txt_file(file_path: PathLike, _file: str = None, **kwargs) -> str:
    _dirname = dirname(_file or __file__)
    filename = file_path if isabs(file_path) else join(_dirname, file_path)
    with open(filename, encoding='utf8') as file:
        result = file.read()
        if kwargs.get('compress'):
            result = json_compress(result)
        return result


def json_compress(json_str: str) -> str:
    return json.dumps(json.loads(json_str), separators=(',', ':'), ensure_ascii=False)
