from os.path import join
from threading import Thread
from typing import Optional

from alembic import command
from alembic.config import Config

from config import settings

PROJECT_ROOT = settings.PROJECT_ROOT
alembic_ini = join(PROJECT_ROOT, 'alembic.ini')
alembic_cfg = Config(alembic_ini)
alembic_sec = alembic_cfg.config_ini_section
sections = alembic_cfg.get_section(alembic_sec)
alembic_cfg.set_section_option(alembic_sec, 'script_location', join(PROJECT_ROOT, sections['script_location']))
alembic_cfg.set_section_option(alembic_sec, 'prepend_sys_path', PROJECT_ROOT)


def _sql_migrate():
    command.upgrade(alembic_cfg, 'head')


def sql_migrate():
    t = Thread(target=_sql_migrate)
    t.start()
    t.join()


def sql_revision(message: Optional[str] = None, autogenerate: bool = False):
    command.revision(alembic_cfg, message=message, autogenerate=autogenerate)
