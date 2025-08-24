#!/usr/bin/env python3
"""
Celery App Configuration
Redis-based job queue for YouTube transcript extraction
"""

import os
from celery import Celery

# Create Celery instance
app = Celery('youtube_transcript_worker')

# Redis configuration 
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Configure Celery
app.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    
    # Task routing - use default queue for simplicity
    task_routes={
        'background_tasks.extract_youtube_transcript_task': {'queue': 'celery'},
    },
    
    # Task execution settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,  # Process one job at a time
    task_acks_late=True,
    worker_max_tasks_per_child=50,
    
    # Task timeout settings
    task_soft_time_limit=300,  # 5 minutes soft limit
    task_time_limit=600,       # 10 minutes hard limit
    
    # Result expiration
    result_expires=3600,       # Results expire after 1 hour
    
    # Job tracking
    task_track_started=True,
    task_send_sent_event=True,
)

# Auto-discover tasks
app.autodiscover_tasks(['background_tasks'])

if __name__ == '__main__':
    app.start()