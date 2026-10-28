import logging
from logging.config import fileConfig

from alembic import context
from flask import current_app
from sqlalchemy import engine_from_config, pool

from conversate.models import UTCDateTime

config = context.config
fileConfig(config.config_file_name, disable_existing_loggers=False)
logger = logging.getLogger('alembic.env')

config.set_main_option(
    'sqlalchemy.url',
    current_app.extensions['migrate']
    .db.engine.url.render_as_string(hide_password=False)
    .replace('%', '%%'),
)
target_metadata = current_app.extensions['migrate'].db.metadata


def render_item(type_, obj, autogen_context):
    # UTCDateTime only converts values in Python; write the column type it
    # stores, so migrations don't need to import the app's models.
    if type_ == 'type' and isinstance(obj, UTCDateTime):
        return 'sa.DateTime(timezone=True)'
    return False


def run_migrations_offline():
    context.configure(
        url=config.get_main_option('sqlalchemy.url'),
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            render_item=render_item,
            **current_app.extensions['migrate'].configure_args,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
