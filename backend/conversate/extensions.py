from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

# Changing this convention rewrites the DDL that the existing baseline migration
# emits, so a fresh database would diverge from an existing one.
metadata = MetaData(
    naming_convention={
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    }
)

db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
