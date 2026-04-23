import pathlib
import sys
from logging.config import fileConfig

import sqlalchemy
from alembic import context
from sqlalchemy import engine_from_config, pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config


sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "app/"))
from models.core import Base

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


IGNORE_TABLES = ["alembic_version"]


def include_object(
    object_: sqlalchemy.schema.Table | sqlalchemy.schema.Column,
    name,
    type_,
    reflected,
    compare_to,
) -> bool:
    """
    Should you include this table or not?
    """
    # excludes with matched schema name, not only table itself
    if isinstance(object_, sqlalchemy.schema.Table):
        if object_.fullname in IGNORE_TABLES:
            return False
    elif object_.table in IGNORE_TABLES:
        return False

    if type_ == "table" and (name in IGNORE_TABLES or object_.info.get("skip_autogenerate", False)):
        return False

    if type_ == "column" and object_.info.get("skip_autogenerate", False):  # noqa: SIM103
        return False

    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        version_table_schema="public",
        template_args={},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema="public",
            include_object=include_object,
            template_args={},
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
