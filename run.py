import os
import logging

from logging.handlers import RotatingFileHandler
from app import create_app
from config import DevelopmentConfig, ProductionConfig

# wybieramy konfigurację wg FLASK_ENV
env = os.getenv('FLASK_ENV', 'production')
config_class = DevelopmentConfig if env == 'development' else ProductionConfig

app = create_app(config_class)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = (env == 'development')

    if not debug_mode:
        # production logs
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        handler = RotatingFileHandler(
            os.path.join(log_dir, 'error.log'),
            maxBytes=10240, backupCount=3
        )
        handler.setLevel(logging.WARNING)
        handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        ))
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application started in production mode')

    app.run(host='0.0.0.0', port=port, debug=debug_mode)

    

