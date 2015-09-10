from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
# from databases.hint import *

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Pass the course name on the command line
args = context.get_x_argument(as_dictionary=True)
course = args.get('course_name') or 'UCSD_CSE103'

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# MyHints = Hint.course_class(course)
# target_metadata = MyHints.metadata
target_metadata=None
# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def run_migrations_offline():
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
        url=url, target_metadata=target_metadata,
        version_table="{0}_alembic_version".format(course),
        course_name=course # This passes the course name to the migration script
    )
    mcontext = context.get_context()
    mcontext.course = course

    with context.begin_transaction():
        context.run_migrations()

webwork_tables = ['user', 'password', 'permission', 'key', 'set',
                  'problem', 'set_user', 'problem_user',
                  'global_user_achievement', 'past_answer', 'achievement',
                  'setting', 'set_locations']

def include_object(object, name, type_, reflected, compare_to):
    if (type_ == "table" and not name.startswith(course) or
        any([name.endswith(table) for table in webwork_tables])):
        return False
    else:
        return True

def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    engine = engine_from_config(
                config.get_section(config.config_ini_section),
                prefix='sqlalchemy.',
                poolclass=pool.NullPool)

    connection = engine.connect()
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
        version_table="{0}_alembic_version".format(course),
        course_name=course # This passes the course name to the migration script
    )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

