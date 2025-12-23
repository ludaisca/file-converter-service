"""
Factory pattern para crear la aplicación Flask con configuración,
error handlers y middleware correctamente inicializados.
"""

from flask import Flask, jsonify, request
from datetime import datetime
import threading
import logging

from src.config_refactored import settings, validate_settings
from src.logging import logger
from src.exceptions import FileConverterException
from src.utils import cleanup_files
from src.routes import main_bp


def create_app(config=None):
    """
    Factory para crear instancia de Flask con configuración completa.
    
    Args:
        config: Objeto de configuración (usa settings por defecto)
    
    Returns:
        Flask: Aplicación configurada
    
    Raises:
        InvalidConfigException: Si la configuración no es válida
    """
    
    # Validar configuración
    try:
        validate_settings()
    except Exception as e:
        logger.error(f"Configuration validation failed: {str(e)}")
        raise
    
    # Crear aplicación
    app = Flask(__name__)
    
    # Configuración Flask
    app.config.update(
        DEBUG=settings.DEBUG,
        JSON_SORT_KEYS=False,
        JSONIFY_PRETTYPRINT_REGULAR=True,
        MAX_CONTENT_LENGTH=settings.MAX_FILE_SIZE
    )
    
    # Registrar blueprints
    app.register_blueprint(main_bp)
    
    # Registrar error handlers
    _register_error_handlers(app)
    
    # Registrar middleware
    _register_middleware(app)
    
    # Registrar comandos CLI (opcional)
    _register_cli_commands(app)
    
    logger.info(f"Flask app created successfully (env={settings.ENV})")
    
    return app


def _register_error_handlers(app: Flask) -> None:
    """
    Registrar handlers para excepciones y errores HTTP.
    
    Args:
        app: Instancia de Flask
    """
    
    @app.errorhandler(FileConverterException)
    def handle_file_converter_exception(error: FileConverterException):
        """Manejar excepciones personalizadas."""
        response = error.to_dict()
        logger.warning(f"FileConverterException: {error.error_code} - {error.message}")
        return jsonify(response), error.status_code
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Manejar solicitudes inválidas."""
        return jsonify({
            'success': False,
            'error': 'Bad request',
            'error_code': 'BAD_REQUEST',
            'timestamp': datetime.utcnow().isoformat()
        }), 400
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Manejar endpoints no encontrados."""
        return jsonify({
            'success': False,
            'error': 'Endpoint not found',
            'error_code': 'NOT_FOUND',
            'timestamp': datetime.utcnow().isoformat()
        }), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Manejar métodos HTTP no permitidos."""
        return jsonify({
            'success': False,
            'error': 'Method not allowed',
            'error_code': 'METHOD_NOT_ALLOWED',
            'timestamp': datetime.utcnow().isoformat()
        }), 405
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Manejar errores internos del servidor."""
        logger.error(f"Internal server error: {str(error)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'error_code': 'INTERNAL_ERROR',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
    
    @app.errorhandler(503)
    def handle_service_unavailable(error):
        """Manejar servicio no disponible."""
        return jsonify({
            'success': False,
            'error': 'Service temporarily unavailable',
            'error_code': 'SERVICE_UNAVAILABLE',
            'timestamp': datetime.utcnow().isoformat()
        }), 503


def _register_middleware(app: Flask) -> None:
    """
    Registrar middleware personalizado.
    
    Args:
        app: Instancia de Flask
    """
    
    @app.before_request
    def before_request():
        """Ejecutar antes de cada request."""
        # Agregar timestamps
        request.start_time = datetime.utcnow()
        
        # Log de request (solo en debug)
        if settings.DEBUG:
            logger.debug(
                f"{request.method} {request.path} - "
                f"Content-Type: {request.content_type}"
            )
    
    @app.after_request
    def after_request(response):
        """Ejecutar después de cada request."""
        # Agregar headers de seguridad
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # CORS headers (configurables)
        if settings.CORS_ORIGINS:
            origin = request.headers.get('Origin')
            if '*' in settings.CORS_ORIGINS or origin in settings.CORS_ORIGINS:
                response.headers['Access-Control-Allow-Origin'] = origin or '*'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        # Log de respuesta con duración
        if hasattr(request, 'start_time'):
            duration = (datetime.utcnow() - request.start_time).total_seconds()
            logger.info(
                f"{request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s"
            )
        
        return response


def _register_cli_commands(app: Flask) -> None:
    """
    Registrar comandos CLI.
    
    Args:
        app: Instancia de Flask
    """
    
    @app.cli.command('validate-config')
    def validate_config_command():
        """Validar configuración de la aplicación."""
        try:
            validate_settings()
            logger.info("\u2713 Configuración válida")
            print("\u2713 Configuration is valid")
        except Exception as e:
            logger.error(f"\u2717 Configuración inválida: {str(e)}")
            print(f"\u2717 Configuration error: {str(e)}")
    
    @app.cli.command('cleanup')
    def cleanup_command():
        """Limpiar archivos temporales."""
        try:
            cleanup_files()
            logger.info("\u2713 Archivos temporales limpiados")
            print("\u2713 Temporary files cleaned up")
        except Exception as e:
            logger.error(f"\u2717 Error limpiando archivos: {str(e)}")
            print(f"\u2717 Cleanup error: {str(e)}")


def setup_cleanup_thread() -> threading.Thread:
    """
    Crear thread de limpieza de archivos.
    
    Returns:
        threading.Thread: Thread configurado e iniciado
    """
    cleanup_thread = threading.Thread(
        target=cleanup_files,
        daemon=True,
        name="CleanupThread"
    )
    cleanup_thread.start()
    logger.info("Cleanup thread started")
    return cleanup_thread


if __name__ == '__main__':
    # Crear aplicación
    app = create_app()
    
    # Iniciar thread de limpieza
    setup_cleanup_thread()
    
    # Mensaje de inicio
    logger.info(
        f"Starting file-converter service... "
        f"(env={settings.ENV}, debug={settings.DEBUG})"
    )
    
    # Ejecutar servidor
    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG,
        use_reloader=settings.DEBUG
    )
