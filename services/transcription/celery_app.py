#!/usr/bin/env python3
"""
Celery configuration for AIBOA Transcription Service
Implements the proven async job processing method from TRANSCRIPT_METHOD.md
"""

import os
from celery import Celery
from celery.signals import after_setup_logger
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "transcription_service",
    broker=f"redis://{os.getenv('REDIS_HOST', 'redis')}:{os.getenv('REDIS_PORT', '6379')}/0",
    backend=f"redis://{os.getenv('REDIS_HOST', 'redis')}:{os.getenv('REDIS_PORT', '6379')}/0",
    include=["celery_tasks"]
)

# Celery configuration matching the proven method
celery_app.conf.update(
    # Task routing
    task_default_queue='transcription',
    task_routes={
        'celery_tasks.*': {'queue': 'transcription'}
    },
    
    # Worker configuration (from proven method)
    worker_concurrency=4,  # CELERYD_CONCURRENCY from TRANSCRIPT_METHOD.md
    task_time_limit=600,   # CELERY_TASK_TIME_LIMIT: 10 minutes
    task_soft_time_limit=480,  # 8 minutes soft limit
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks to prevent memory leaks
    
    # Result backend settings
    result_expires=3600,  # 1 hour as in proven method
    result_backend_transport_options={
        'retry_on_timeout': True,
    },
    
    # Task execution settings
    task_acks_late=True,  # Acknowledge tasks after completion
    worker_prefetch_multiplier=1,  # One task at a time per worker
    
    # Monitoring and logging
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Redis settings
    broker_transport_options={
        'retry_on_timeout': True,
        'visibility_timeout': 3600,  # 1 hour
    },
    
    # Task serialization
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)

@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    """Setup logging for Celery workers"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)