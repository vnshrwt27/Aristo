"""Handles uploading chunks to vector database"""

from typing import List, Optional
import uuid
import asyncio
from datetime import datetime

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    CollectionStatus
)
