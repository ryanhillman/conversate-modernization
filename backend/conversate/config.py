from decouple import UndefinedValueError, config


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
        # The largest legitimate body is the base64-encoded STT audio upload
        # (~1.33MB for a 1MB clip); 2MB leaves headroom without letting a
        # logged-in client make Flask parse an arbitrarily large body.
        self.MAX_CONTENT_LENGTH = 2 * 1024 * 1024
