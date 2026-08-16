from decouple import config, UndefinedValueError


class ConfigError(RuntimeError):
    pass


class Config:
    def __init__(self):
        missing = []

        def required(name):
            try:
                return config(name)
            except UndefinedValueError:
                missing.append(name)
                return None

        self.SQLALCHEMY_DATABASE_URI = required('DATABASE_URL')
        self.AUTH0_DOMAIN = required('AUTH0_DOMAIN')
        self.AUTH0_AUDIENCE = required('AUTH0_AUDIENCE')
        self.GOOGLE_CLOUD_API_KEY = required('GOOGLE_CLOUD_API_KEY')

        if missing:
            raise ConfigError(
                'Missing required environment variables: %s' % ', '.join(missing)
            )

        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}
        self.ALLOWED_ORIGIN = config('ALLOWED_ORIGIN', default='http://localhost:3000')
        self.DEBUG = config('DEBUG', cast=bool, default=False)
