import asyncio
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import uuid
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    Range,
    MatchValue,
    MatchAny,
    HasIdCondition,
    IsEmptyCondition,
    IsNullCondition,
    NestedCondition,
    FilterSelector,
    SearchRequest,
    UpdateStatus,
    CollectionStatus,
    OptimizersConfigDiff,
    CreateCollection,
    SearchParams,
    QuantizationConfig,
    ScalarQuantization,
    ProductQuantization,
    BinaryQuantization,
    HnswConfigDiff,
    PointIdsList,
    PointsSelector,
    RecommendStrategy,
    LookupLocation,
    OrderValue,
    Direction
)
import numpy as np
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Data class for search results"""
    id: Union[str, int]
    score: float
    payload: Dict[str, Any]
    vector: Optional[List[float]] = None


class AsyncQdrantManager:
    """
    Async Qdrant client wrapper for handling all database operations
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30,
        grpc_port: int = 6334,
        prefer_grpc: bool = False
    ):
        """
        Initialize the Async Qdrant client
        
        Args:
            host: Qdrant server host
            port: Qdrant REST API port
            url: Full URL (alternative to host:port)
            api_key: API key for authentication
            timeout: Request timeout in seconds
            grpc_port: gRPC port for faster operations
            prefer_grpc: Whether to prefer gRPC over REST
        """
        if url :
            self.client = AsyncQdrantClient(
            url=url,
            api_key=api_key,
            timeout=timeout,
            prefer_grpc=prefer_grpc
        )
        else:
            self.client = AsyncQdrantClient(
                host=host, 
                port=port, 
                grpc_port=grpc_port, 
                timeout=timeout, 
                prefer_grpc=prefer_grpc
                )
            
    async def get_all_collections(self):
        """Fetches all collections """
        try:
            result= await self.client.get_collections()
            return result
        except Exception as e:
            logger.error(f"Error fetching collections:{e}")
            raise

    async def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: Distance = Distance.COSINE,
        on_disk_payload: bool = False,
        hnsw_config: Optional[Dict[str, Any]] = None,
        optimizers_config: Optional[Dict[str, Any]] = None,
        wal_config: Optional[Dict[str, Any]] = None,
        quantization_config: Optional[Union[ScalarQuantization, ProductQuantization, BinaryQuantization]] = None,
        init_from: Optional[str] = None,
        replication_factor: int = 1,
        write_consistency_factor: int = 1
    ) -> bool:
        """
        Create a new collection
        
        Args:
            collection_name: Name of the collection
            vector_size: Size of vectors
            distance: Distance metric (COSINE, EUCLID, DOT)
            on_disk_payload: Store payload on disk
            hnsw_config: HNSW index configuration
            optimizers_config: Optimizer configuration
            wal_config: Write-ahead log configuration
            quantization_config: Quantization settings
            init_from: Initialize from another collection
            replication_factor: Number of replicas
            write_consistency_factor: Write consistency factor
        
        Returns:
            Success status
        """
        try:
            result = await self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance,
                    on_disk=on_disk_payload
                ),
                hnsw_config=hnsw_config,
                optimizers_config=optimizers_config,
                wal_config=wal_config,
                quantization_config=quantization_config,
                init_from=init_from,
                replication_factor=replication_factor,
                write_consistency_factor=write_consistency_factor
            )
            logger.info(f"Collection '{collection_name}' created successfully")
            return result
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection"""
        try:
            result = await self.client.delete_collection(collection_name)
            logger.info(f"Collection '{collection_name}' deleted successfully")
            return result
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise
    
    async def collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists"""
        try:
            collections = await self.client.get_collections()
            return any(col.name == collection_name for col in collections.collections)
        except Exception as e:
            logger.error(f"Error checking collection existence: {e}")
            raise
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get collection information"""
        try:
            info = await self.client.get_collection(collection_name)
            return {
                "status": info.status,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "config": info.config,
                "payload_schema": info.payload_schema
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            raise
    
    async def upload_points(
        self,
        collection_name: str,
        points: List[PointStruct],
        batch_size: int = 100,
        wait: bool = True,
        ordering: Optional[str] = None
    ) -> List[UpdateStatus]:
        """
        Upload points to collection in batches
        
        Args:
            collection_name: Name of the collection
            points: List of PointStruct objects
            batch_size: Size of upload batches
            wait: Wait for operation to complete
            ordering: Write ordering
        
        Returns:
            List of update statuses
        """
        try:
            results = []
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                result = await self.client.upsert(
                    collection_name=collection_name,
                    points=batch,
                    wait=wait,
                    ordering=ordering
                )
                results.append(result)
                logger.info(f"Uploaded batch {i//batch_size + 1}: {len(batch)} points")
            
            return results
        except Exception as e:
            logger.error(f"Error uploading points: {e}")
            raise
    
    async def upsert_point(
        self,
        collection_name: str,
        point_id: Union[str, int],
        vector: List[float],
        payload: Dict[str, Any],
        wait: bool = True
    ) -> UpdateStatus:
        """
        Upsert a single point
        
        Args:
            collection_name: Name of the collection
            point_id: Point ID
            vector: Vector embedding
            payload: Point payload
            wait: Wait for operation to complete
        
        Returns:
            Update status
        """
        try:
            point = PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            )
            
            result = await self.client.upsert(
                collection_name=collection_name,
                points=[point],
                wait=wait
            )
            logger.info(f"Upserted point {point_id}")
            return result
        except Exception as e:
            logger.error(f"Error upserting point: {e}")
            raise
    
    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        offset: int = 0,
        with_vectors: bool = False,
        with_payload: bool = True,
        filter: Optional[Filter] = None,
        search_params: Optional[SearchParams] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors
        
        Args:
            collection_name: Name of the collection
            query_vector: Query vector
            limit: Maximum number of results
            score_threshold: Minimum score threshold
            offset: Offset for pagination
            with_vectors: Include vectors in results
            with_payload: Include payload in results
            filter: Filter conditions
            search_params: Search parameters
        
        Returns:
            List of search results
        """
        try:
            results = await self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                offset=offset,
                with_vectors=with_vectors,
                with_payload=with_payload,
                query_filter=filter,
                search_params=search_params
            )
            
            return [
                SearchResult(
                    id=hit.id,
                    score=hit.score,
                    payload=hit.payload if hit.payload else {},
                    vector=hit.vector if with_vectors else None
                )
                for hit in results
            ]
        except Exception as e:
            logger.error(f"Error searching: {e}")
            raise
    
    async def search_batch(
        self,
        collection_name: str,
        query_vectors: List[List[float]],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        with_vectors: bool = False,
        with_payload: bool = True,
        filter: Optional[Filter] = None
    ) -> List[List[SearchResult]]:
        """
        Batch search for multiple query vectors
        
        Args:
            collection_name: Name of the collection
            query_vectors: List of query vectors
            limit: Maximum number of results per query
            score_threshold: Minimum score threshold
            with_vectors: Include vectors in results
            with_payload: Include payload in results
            filter: Filter conditions
        
        Returns:
            List of search results for each query
        """
        try:
            search_queries = [
                SearchRequest(
                    vector=vector,
                    limit=limit,
                    score_threshold=score_threshold,
                    with_vector=with_vectors,
                    with_payload=with_payload,
                    filter=filter
                )
                for vector in query_vectors
            ]
            
            results = await self.client.search_batch(
                collection_name=collection_name,
                requests=search_queries
            )
            
            return [
                [
                    SearchResult(
                        id=hit.id,
                        score=hit.score,
                        payload=hit.payload if hit.payload else {},
                        vector=hit.vector if with_vectors else None
                    )
                    for hit in batch_results
                ]
                for batch_results in results
            ]
        except Exception as e:
            logger.error(f"Error in batch search: {e}")
            raise
    
    async def recommend(
        self,
        collection_name: str,
        positive: List[Union[str, int]],
        negative: Optional[List[Union[str, int]]] = None,
        limit: int = 10,
        score_threshold: Optional[float] = None,
        offset: int = 0,
        using: Optional[str] = None,
        with_vectors: bool = False,
        with_payload: bool = True,
        filter: Optional[Filter] = None,
        strategy: Optional[RecommendStrategy] = None,
        lookup_from: Optional[LookupLocation] = None
    ) -> List[SearchResult]:
        """
        Get recommendations based on positive and negative examples
        
        Args:
            collection_name: Name of the collection
            positive: List of positive point IDs
            negative: List of negative point IDs
            limit: Maximum number of results
            score_threshold: Minimum score threshold
            offset: Offset for pagination
            using: Named vector to use
            with_vectors: Include vectors in results
            with_payload: Include payload in results
            filter: Filter conditions
            strategy: Recommendation strategy
            lookup_from: Lookup location
        
        Returns:
            List of recommended points
        """
        try:
            results = await self.client.recommend(
                collection_name=collection_name,
                positive=positive,
                negative=negative or [],
                limit=limit,
                score_threshold=score_threshold,
                offset=offset,
                using=using,
                with_vectors=with_vectors,
                with_payload=with_payload,
                query_filter=filter,
                strategy=strategy,
                lookup_from=lookup_from
            )
            
            return [
                SearchResult(
                    id=hit.id,
                    score=hit.score,
                    payload=hit.payload if hit.payload else {},
                    vector=hit.vector if with_vectors else None
                )
                for hit in results
            ]
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            raise
    
    async def delete_points(
        self,
        collection_name: str,
        points_selector: Union[List[Union[str, int]], Filter],
        wait: bool = True,
        ordering: Optional[str] = None
    ) -> UpdateStatus:
        """
        Delete points from collection
        
        Args:
            collection_name: Name of the collection
            points_selector: Point IDs or filter
            wait: Wait for operation to complete
            ordering: Write ordering
        
        Returns:
            Update status
        """
        try:
            if isinstance(points_selector, list):
                selector = PointIdsList(points=points_selector)
            else:
                selector = FilterSelector(filter=points_selector)
            
            result = await self.client.delete(
                collection_name=collection_name,
                points_selector=selector,
                wait=wait,
                ordering=ordering
            )
            logger.info(f"Deleted points from {collection_name}")
            return result
        except Exception as e:
            logger.error(f"Error deleting points: {e}")
            raise
    
    async def update_payload(
        self,
        collection_name: str,
        payload: Dict[str, Any],
        points: Union[List[Union[str, int]], Filter],
        wait: bool = True,
        ordering: Optional[str] = None
    ) -> UpdateStatus:
        """
        Update payload for specified points
        
        Args:
            collection_name: Name of the collection
            payload: New payload values
            points: Point IDs or filter
            wait: Wait for operation to complete
            ordering: Write ordering
        
        Returns:
            Update status
        """
        try:
            result = await self.client.set_payload(
                collection_name=collection_name,
                payload=payload,
                points=points,
                wait=wait,
                ordering=ordering
            )
            logger.info(f"Updated payload for points in {collection_name}")
            return result
        except Exception as e:
            logger.error(f"Error updating payload: {e}")
            raise
    
    async def delete_payload(
        self,
        collection_name: str,
        keys: List[str],
        points: Union[List[Union[str, int]], Filter],
        wait: bool = True,
        ordering: Optional[str] = None
    ) -> UpdateStatus:
        """
        Delete payload keys for specified points
        
        Args:
            collection_name: Name of the collection
            keys: Payload keys to delete
            points: Point IDs or filter
            wait: Wait for operation to complete
            ordering: Write ordering
        
        Returns:
            Update status
        """
        try:
            result = await self.client.delete_payload(
                collection_name=collection_name,
                keys=keys,
                points=points,
                wait=wait,
                ordering=ordering
            )
            logger.info(f"Deleted payload keys from points in {collection_name}")
            return result
        except Exception as e:
            logger.error(f"Error deleting payload: {e}")
            raise
    
    async def retrieve_points(
        self,
        collection_name: str,
        ids: List[Union[str, int]],
        with_vectors: bool = False,
        with_payload: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve specific points by IDs
        
        Args:
            collection_name: Name of the collection
            ids: List of point IDs
            with_vectors: Include vectors in results
            with_payload: Include payload in results
        
        Returns:
            List of points
        """
        try:
            points = await self.client.retrieve(
                collection_name=collection_name,
                ids=ids,
                with_vectors=with_vectors,
                with_payload=with_payload
            )
            
            return [
                {
                    "id": point.id,
                    "payload": point.payload if point.payload else {},
                    "vector": point.vector if with_vectors else None
                }
                for point in points
            ]
        except Exception as e:
            logger.error(f"Error retrieving points: {e}")
            raise
    
    async def scroll(
        self,
        collection_name: str,
        scroll_filter: Optional[Filter] = None,
        limit: int = 100,
        offset: Optional[Union[str, int]] = None,
        with_vectors: bool = False,
        with_payload: bool = True,
        order_by: Optional[str] = None,
        direction: Optional[Direction] = None
    ) -> tuple[List[Dict[str, Any]], Optional[Union[str, int]]]:
        """
        Scroll through points in collection
        
        Args:
            collection_name: Name of the collection
            scroll_filter: Filter conditions
            limit: Maximum number of points to return
            offset: Offset ID for pagination
            with_vectors: Include vectors in results
            with_payload: Include payload in results
            order_by: Field to order by
            direction: Sort direction
        
        Returns:
            Tuple of (points, next_offset)
        """
        try:
            records, next_page_offset = await self.client.scroll(
                collection_name=collection_name,
                scroll_filter=scroll_filter,
                limit=limit,
                offset=offset,
                with_vectors=with_vectors,
                with_payload=with_payload,
                order_by=OrderValue(
                    key=order_by,
                    direction=direction
                ) if order_by else None
            )
            
            points = [
                {
                    "id": record.id,
                    "payload": record.payload if record.payload else {},
                    "vector": record.vector if with_vectors else None
                }
                for record in records
            ]
            
            return points, next_page_offset
        except Exception as e:
            logger.error(f"Error scrolling through points: {e}")
            raise
    
    async def count(
        self,
        collection_name: str,
        count_filter: Optional[Filter] = None,
        exact: bool = True
    ) -> int:
        """
        Count points in collection
        
        Args:
            collection_name: Name of the collection
            count_filter: Filter conditions
            exact: Use exact count
        
        Returns:
            Number of points
        """
        try:
            result = await self.client.count(
                collection_name=collection_name,
                count_filter=count_filter,
                exact=exact
            )
            return result.count
        except Exception as e:
            logger.error(f"Error counting points: {e}")
            raise
    
    async def create_payload_index(
        self,
        collection_name: str,
        field_name: str,
        field_schema: Optional[str] = None,
        wait: bool = True,
        ordering: Optional[str] = None
    ) -> UpdateStatus:
        """
        Create an index for a payload field
        
        Args:
            collection_name: Name of the collection
            field_name: Name of the field to index
            field_schema: Field schema type
            wait: Wait for operation to complete
            ordering: Write ordering
        
        Returns:
            Update status
        """
        try:
            result = await self.client.create_payload_index(
                collection_name=collection_name,
                field_name=field_name,
                field_schema=field_schema,
                wait=wait,
                ordering=ordering
            )
            logger.info(f"Created index for field '{field_name}' in {collection_name}")
            return result
        except Exception as e:
            logger.error(f"Error creating payload index: {e}")
            raise
    
    async def delete_payload_index(
        self,
        collection_name: str,
        field_name: str,
        wait: bool = True,
        ordering: Optional[str] = None
    ) -> UpdateStatus:
        """
        Delete an index for a payload field
        
        Args:
            collection_name: Name of the collection
            field_name: Name of the field
            wait: Wait for operation to complete
            ordering: Write ordering
        
        Returns:
            Update status
        """
        try:
            result = await self.client.delete_payload_index(
                collection_name=collection_name,
                field_name=field_name,
                wait=wait,
                ordering=ordering
            )
            logger.info(f"Deleted index for field '{field_name}' in {collection_name}")
            return result
        except Exception as e:
            logger.error(f"Error deleting payload index: {e}")
            raise
    
    async def update_collection(
        self,
        collection_name: str,
        optimizers_config: Optional[OptimizersConfigDiff] = None,
        hnsw_config: Optional[HnswConfigDiff] = None,
        quantization_config: Optional[Union[ScalarQuantization, ProductQuantization, BinaryQuantization]] = None
    ) -> bool:
        """
        Update collection configuration
        
        Args:
            collection_name: Name of the collection
            optimizers_config: Optimizer configuration
            hnsw_config: HNSW configuration
            quantization_config: Quantization configuration
        
        Returns:
            Success status
        """
        try:
            result = await self.client.update_collection(
                collection_name=collection_name,
                optimizers_config=optimizers_config,
                hnsw_config=hnsw_config,
                quantization_config=quantization_config
            )
            logger.info(f"Updated collection '{collection_name}'")
            return result
        except Exception as e:
            logger.error(f"Error updating collection: {e}")
            raise
    
    @staticmethod
    def create_filter(conditions: Dict[str, Any]) -> Filter:
        """
        Create a filter from conditions dictionary
        
        Args:
            conditions: Dictionary of filter conditions
                Examples:
                {
                    "must": [
                        {"key": "city", "match": {"value": "London"}},
                        {"key": "age", "range": {"gte": 18, "lte": 65}}
                    ],
                    "should": [
                        {"key": "category", "match": {"any": ["A", "B", "C"]}}
                    ],
                    "must_not": [
                        {"key": "status", "match": {"value": "inactive"}}
                    ]
                }
        
        Returns:
            Filter object
        """
        must = []
        should = []
        must_not = []
        
        for condition_type, condition_list in conditions.items():
            target_list = {"must": must, "should": should, "must_not": must_not}.get(condition_type)
            
            if target_list is None:
                continue
            
            for condition in condition_list:
                key = condition.get("key")
                
                if "match" in condition:
                    match = condition["match"]
                    if "value" in match:
                        target_list.append(
                            FieldCondition(
                                key=key,
                                match=MatchValue(value=match["value"])
                            )
                        )
                    elif "any" in match:
                        target_list.append(
                            FieldCondition(
                                key=key,
                                match=MatchAny(any=match["any"])
                            )
                        )
                
                elif "range" in condition:
                    target_list.append(
                        FieldCondition(
                            key=key,
                            range=Range(**condition["range"])
                        )
                    )
                
                elif "is_empty" in condition:
                    target_list.append(
                        IsEmptyCondition(
                            is_empty=condition["is_empty"]
                        )
                    )
                
                elif "is_null" in condition:
                    target_list.append(
                        IsNullCondition(
                            is_null=condition["is_null"]
                        )
                    )
                
                elif "has_id" in condition:
                    target_list.append(
                        HasIdCondition(
                            has_id=condition["has_id"]
                        )
                    )
                
                elif "nested" in condition:
                    nested = condition["nested"]
                    target_list.append(
                        NestedCondition(
                            key=key,
                            filter=AsyncQdrantManager.create_filter(nested)
                        )
                    )
        
        return Filter(
            must=must if must else None,
            should=should if should else None,
            must_not=must_not if must_not else None
        )
    
    async def close(self):
        """Close the client connection"""
        await self.client.close()


# Example usage
async def example_usage():
    """Example usage of the AsyncQdrantManager"""
    
    # Initialize client
    manager = AsyncQdrantManager(host="localhost", port=6333)
    
    # Create collection
    await manager.create_collection(
        collection_name="test_collection",
        vector_size=384,
        distance=Distance.COSINE
    )
    
    # Prepare some sample data
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=np.random.rand(384).tolist(),
            payload={
                "title": f"Document {i}",
                "category": ["A", "B", "C"][i % 3],
                "timestamp": datetime.now().isoformat(),
                "score": np.random.randint(0, 100)
            }
        )
        for i in range(100)
    ]
    
    # Upload points
    await manager.upload_points(
        collection_name="test_collection",
        points=points,
        batch_size=50
    )
    
    # Search with filter
    filter_conditions = {
        "must": [
            {"key": "category", "match": {"value": "A"}},
            {"key": "score", "range": {"gte": 50}}
        ]
    }
    
    search_filter = manager.create_filter(filter_conditions)
    
    results = await manager.search(
        collection_name="test_collection",
        query_vector=np.random.rand(384).tolist(),
        limit=5,
        filter=search_filter
    )
    
    print(f"Found {len(results)} results")
    for result in results:
        print(f"ID: {result.id}, Score: {result.score}, Payload: {result.payload}")
    
    # Count points with filter
    count = await manager.count(
        collection_name="test_collection",
        count_filter=search_filter
    )
    print(f"Total points matching filter: {count}")
    
    # Close connection
    await manager.close()


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())