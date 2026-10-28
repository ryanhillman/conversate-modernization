from decouple import UndefinedValueError, config

# The largest valid body is a speech-to-text upload, about 1.33MB of base64 for
# a 1MB clip; 2MB leaves headroom.
MAX_REQUEST_BYTES = 2 * 1024 * 1024


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
            raise ConfigError(f'Missing required environment variables: {", ".join(missing)}')

        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}
        self.ALLOWED_ORIGIN = config('ALLOWED_ORIGIN', default='http://localhost:3000')
        self.DEBUG = config('DEBUG', cast=bool, default=False)
        self.MAX_CONTENT_LENGTH = MAX_REQUEST_BYTES
