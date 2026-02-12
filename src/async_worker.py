import sqlite3
import threading
import uuid
import time
import json
import logging
from enum import Enum
from datetime import datetime, timedelta
from typing import Callable, Any, Dict, Optional
from pathlib import Path
from src.config import settings

logger = logging.getLogger('file_converter')

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class AsyncTaskManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Usar una ubicación persistente pero temporal
            self.db_path = settings.TEMP_FOLDER / "tasks.db"
        else:
            self.db_path = Path(db_path)

        self._stop_event = threading.Event()
        self._worker_thread = None
        self._handlers: Dict[str, Callable] = {}
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(str(self.db_path), timeout=10)

    def _init_db(self):
        """Inicializa la tabla de tareas."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        status TEXT NOT NULL,
                        result TEXT,
                        error TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Índice para optimizar búsqueda de pendientes
                conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    def register_handler(self, task_type: str, handler: Callable):
        """Registra una función para manejar un tipo de tarea específico."""
        self._handlers[task_type] = handler

    def start(self):
        """Inicia el hilo del worker en segundo plano."""
        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._stop_event.clear()
            self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self._worker_thread.start()
            logger.info(f"Async worker started (DB: {self.db_path})")

    def stop(self):
        """Detiene el worker gracefuly."""
        self._stop_event.set()
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
            logger.info("Async worker stopped")

    def submit_task(self, task_type: str, **kwargs) -> str:
        """Envía una tarea a la DB y devuelve un ID de tarea."""
        task_id = str(uuid.uuid4())
        payload = json.dumps(kwargs)

        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO tasks (id, type, payload, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (task_id, task_type, payload, TaskStatus.PENDING, datetime.utcnow(), datetime.utcnow())
                )
            logger.info(f"Task {task_id} submitted (Type: {task_type})")
            return task_id
        except Exception as e:
            logger.error(f"Failed to submit task: {e}")
            raise e

    def get_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado actual de una tarea."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT status, result, error, created_at, updated_at FROM tasks WHERE id = ?", (task_id,))
                row = cursor.fetchone()

                if row:
                    status, result_json, error, created_at, updated_at = row
                    result = json.loads(result_json) if result_json else None
                    return {
                        "status": status,
                        "result": result,
                        "error": error,
                        "created_at": created_at,
                        "updated_at": updated_at
                    }
                return None
        except Exception as e:
            logger.error(f"Failed to get status for {task_id}: {e}")
            return None

    def _worker_loop(self):
        """Bucle principal del worker que procesa las tareas."""
        logger.info("Worker loop running")
        while not self._stop_event.is_set():
            processed = False
            try:
                task = self._claim_task()
                if task:
                    self._process_task(task)
                    processed = True
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")

            # Limpieza periódica (cada 100 iteraciones o similar, aquí simplificado)
            if not processed:
                time.sleep(1) # Esperar si no hay trabajo

            # Limpiar tareas viejas ocasionalmente
            if datetime.now().second == 0: # Una vez por minuto aprox
                self._cleanup_old_tasks()

    def _claim_task(self):
        """Intenta reclamar una tarea pendiente de forma atómica."""
        conn = self._get_connection()
        try:
            # Transacción inmediata para evitar condiciones de carrera
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.execute("SELECT id, type, payload FROM tasks WHERE status = ? ORDER BY created_at ASC LIMIT 1", (TaskStatus.PENDING,))
            row = cursor.fetchone()

            if row:
                task_id, task_type, payload = row
                conn.execute("UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?", (TaskStatus.PROCESSING, datetime.utcnow(), task_id))
                conn.commit()
                return (task_id, task_type, payload)
            else:
                conn.commit() # Liberar bloqueo si no hay tareas
                return None
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _process_task(self, task):
        task_id, task_type, payload_json = task
        logger.info(f"Processing task {task_id}")

        try:
            handler = self._handlers.get(task_type)
            if not handler:
                raise Exception(f"No handler registered for task type: {task_type}")

            payload = json.loads(payload_json)
            # Ejecutar handler
            result = handler(**payload)

            # Guardar éxito
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE tasks SET status = ?, result = ?, updated_at = ? WHERE id = ?",
                    (TaskStatus.COMPLETED, json.dumps(result), datetime.utcnow(), task_id)
                )
            logger.info(f"Task {task_id} completed successfully")

        except Exception as e:
            logger.error(f"Task {task_id} failed: {str(e)}", exc_info=True)
            # Guardar fallo
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE tasks SET status = ?, error = ?, updated_at = ? WHERE id = ?",
                    (TaskStatus.FAILED, str(e), datetime.utcnow(), task_id)
                )

    def _cleanup_old_tasks(self):
        """Elimina tareas completadas o fallidas antiguas (> 24h)."""
        try:
            cutoff = datetime.utcnow() - timedelta(hours=24)
            with self._get_connection() as conn:
                conn.execute(
                    "DELETE FROM tasks WHERE updated_at < ? AND status IN (?, ?)",
                    (cutoff, TaskStatus.COMPLETED, TaskStatus.FAILED)
                )
        except Exception as e:
            logger.error(f"Failed to cleanup old tasks: {e}")

# Instancia global (Singleton)
async_manager = AsyncTaskManager()
