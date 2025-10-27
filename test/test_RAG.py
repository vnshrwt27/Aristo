"""
Production-ready RAG Evaluation Script
"""

import asyncio
import logging
from typing import List, Dict, Tuple
from datetime import datetime
from pathlib import Path

from datasets import load_dataset
from core.vdb_client import client
from core.qdrant_uploader import QdrantUploader
from core.document_chunker import DocumentChunk, ChunkMetadata
from core.embedding import model

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RAGTester:
    """Complete RAG testing with metrics"""
    
    def __init__(self, collection_name: str = "rag_test"):
        self.collection_name = collection_name
        self.client = client
        self.uploader = None
        
    async def initialize(self):
        """Initialize async components"""
        logger.info(f"Initializing RAG tester with collection: {self.collection_name}")
        self.uploader = await QdrantUploader.create(
            self.client, 
            self.collection_name, 
            768
        )
        logger.info("✓ Initialization complete")
    
    def load_squad_data(self, max_samples: int = 100) -> Tuple[List[Dict], Dict[str, str]]:
        """
        Load SQuAD v2 dataset for testing
        
        Returns:
            (test_cases, context_mapping)
        """
        logger.info("Loading SQuAD v2 dataset...")
        squad = load_dataset("squad_v2", split="validation")
        
        test_cases = []
        context_to_id = {}
        
        for idx, example in enumerate(squad):
            if idx >= max_samples:
                break
            
            # Skip unanswerable questions
            if not example['answers']['text']:
                continue
            
            context = example['context']
            
            # Create unique ID for context
            if context not in context_to_id:
                context_to_id[context] = f"squad_ctx_{len(context_to_id)}"
            
            test_cases.append({
                'id': f"q_{idx}",
                'question': example['question'],
                'context': context,
                'context_id': context_to_id[context],
                'answers': example['answers']['text'],
                'title': example.get('title', 'Unknown')
            })
        
        logger.info(f"✓ Loaded {len(test_cases)} test cases")
        logger.info(f"✓ Unique contexts: {len(context_to_id)}")
        
        return test_cases, context_to_id
    
    def create_chunks(self, context_to_id: Dict[str, str]) -> List[DocumentChunk]:
        """
        Convert contexts to DocumentChunks with proper metadata
        
        Args:
            context_to_id: Mapping of context text to IDs
            
        Returns:
            List of DocumentChunks ready for upload
        """
        logger.info("Creating document chunks...")
        chunks = []
        
        for context, ctx_id in context_to_id.items():
            # Create proper metadata
            metadata = ChunkMetadata(
                doc_id=ctx_id,
                chunk_id=ctx_id,
                source="squad_v2_validation",
                chunk_index=0,
                total_chunks=1,
                created_at=datetime.now().timestamp()
            )
            
            # Create chunk
            chunk = DocumentChunk(
                content=context,
                metadata=metadata,
                embedding=None  # Will be generated during upload
            )
            
            chunks.append(chunk)
        
        logger.info(f"✓ Created {len(chunks)} chunks")
        return chunks
    
    async def index_chunks(self, chunks: List[DocumentChunk], batch_size: int = 50):
        """
        Index chunks into vector database with batching
        
        Args:
            chunks: List of DocumentChunks to index
            batch_size: Number of chunks per batch
        """
        logger.info(f"Indexing {len(chunks)} chunks in batches of {batch_size}...")
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            try:
                await self.uploader.upload_chunks(batch)
                logger.info(f"  ✓ Indexed {min(i + batch_size, len(chunks))}/{len(chunks)}")
            except Exception as e:
                logger.error(f"  ✗ Error indexing batch {i//batch_size + 1}: {e}")
                raise
        
        logger.info("✓ All chunks indexed successfully")
    
    async def search(self, query: str, k: int = 10) -> List[Dict]:
        """
        Search for relevant contexts
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of search results with context_id, content, score
        """
        query_embedding = model.encode(query)
        
        results = await self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=k
        )
        
        search_results = []
        for point in results.points:
            search_results.append({
                'context_id': point.payload['metadata']['doc_id'],
                'content': point.payload['content'],
                'score': point.score
            })
        
        return search_results
    
    def calculate_metrics(self, test_cases: List[Dict], k_values: List[int] = None) -> Dict:
        """
        Calculate evaluation metrics
        
        Args:
            test_cases: List of test cases with retrieved results
            k_values: List of k values to evaluate
            
        Returns:
            Dictionary of metrics
        """
        if k_values is None:
            k_values = [1, 3, 5, 10]
        
        logger.info("Calculating metrics...")
        
        metrics = {
            'precision': {k: [] for k in k_values},
            'recall': {k: [] for k in k_values},
            'hit_rate': {k: [] for k in k_values},
            'mrr_scores': [],
        }
        
        for case in test_cases:
            if 'retrieved' not in case:
                continue
            
            expected = case['context_id']
            retrieved_ids = [r['context_id'] for r in case['retrieved']]
            
            # Calculate metrics for each k
            for k in k_values:
                top_k = retrieved_ids[:k]
                
                # Precision@k
                relevant_in_k = 1 if expected in top_k else 0
                precision = relevant_in_k / k
                metrics['precision'][k].append(precision)
                
                # Recall@k (binary: either found or not)
                recall = 1.0 if expected in top_k else 0.0
                metrics['recall'][k].append(recall)
                
                # Hit@k
                hit = 1 if expected in top_k else 0
                metrics['hit_rate'][k].append(hit)
            
            # MRR (using all retrieved)
            try:
                rank = retrieved_ids.index(expected) + 1
                mrr = 1.0 / rank
            except ValueError:
                mrr = 0.0
            metrics['mrr_scores'].append(mrr)
        
        # Aggregate results
        aggregated = {
            'precision@k': {k: sum(v)/len(v) if v else 0 for k, v in metrics['precision'].items()},
            'recall@k': {k: sum(v)/len(v) if v else 0 for k, v in metrics['recall'].items()},
            'hit_rate@k': {k: sum(v)/len(v) if v else 0 for k, v in metrics['hit_rate'].items()},
            'mrr': sum(metrics['mrr_scores'])/len(metrics['mrr_scores']) if metrics['mrr_scores'] else 0,
            'total_queries': len(test_cases),
        }
        
        return aggregated
    
    async def run_evaluation(self, test_cases: List[Dict], k: int = 10) -> List[Dict]:
        """
        Run retrieval for all test cases
        
        Args:
            test_cases: List of test cases
            k: Number of results to retrieve per query
            
        Returns:
            Test cases with retrieved results added
        """
        logger.info(f"Running evaluation on {len(test_cases)} test cases...")
        
        for idx, case in enumerate(test_cases):
            if (idx + 1) % 20 == 0:
                logger.info(f"  Progress: {idx + 1}/{len(test_cases)}")
            
            # Retrieve
            retrieved = await self.search(case['question'], k=k)
            case['retrieved'] = retrieved
            
            # Check if correct context is retrieved
            retrieved_ids = [r['context_id'] for r in retrieved]
            case['found'] = case['context_id'] in retrieved_ids
            
            if case['found']:
                case['rank'] = retrieved_ids.index(case['context_id']) + 1
            else:
                case['rank'] = None
        
        logger.info("✓ Evaluation complete")
        return test_cases
    
    def print_results(self, metrics: Dict):
        """Print formatted results"""
        print("\n" + "="*70)
        print("RAG EVALUATION RESULTS")
        print("="*70)
        print(f"\nTotal Queries: {metrics['total_queries']}")
        print(f"Mean Reciprocal Rank (MRR): {metrics['mrr']:.4f}")
        print()
        
        # Print @k metrics
        for k in sorted(metrics['precision@k'].keys()):
            print(f"--- Metrics @ k={k} ---")
            print(f"  Precision@{k}: {metrics['precision@k'][k]:.4f}")
            print(f"  Recall@{k}: {metrics['recall@k'][k]:.4f}")
            print(f"  Hit Rate@{k}: {metrics['hit_rate@k'][k]:.4f}")
            print()
        
        print("="*70)
    
    def save_results(self, metrics: Dict, test_cases: List[Dict], output_dir: str = "results"):
        """Save results to files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save metrics
        import json
        metrics_file = output_path / f"metrics_{timestamp}.json"
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"✓ Metrics saved to {metrics_file}")
        
    async def run_full_test(self, 
                           max_samples: int = 100,
                           k_values: List[int] = None,
                           skip_indexing: bool = False):
        """
        Run complete RAG test pipeline
        
        Args:
            max_samples: Number of samples to test
            k_values: List of k values for metrics
            skip_indexing: Skip indexing if data already in DB
        """
        if k_values is None:
            k_values = [1, 3, 5, 10]
        
        # Initialize
        await self.initialize()
        
        # Load data
        test_cases, context_to_id = self.load_squad_data(max_samples)
        
        # Index contexts
        if not skip_indexing:
            chunks = self.create_chunks(context_to_id)
            await self.index_chunks(chunks)
        else:
            logger.warning("⚠ Skipping indexing - using existing collection")
        
        # Run evaluation
        test_cases = await self.run_evaluation(test_cases, k=max(k_values))
        
        # Calculate metrics
        metrics = self.calculate_metrics(test_cases, k_values)
        
        # Print and save results
        self.print_results(metrics)
        self.save_results(metrics, test_cases)
        
        return metrics, test_cases


async def main():
    """Main entry point"""
    tester = RAGTester(collection_name="rag_test_squad")
    
    try:
        metrics, test_cases = await tester.run_full_test(
            max_samples=100,
            k_values=[1, 3, 5, 10],
            skip_indexing=False  # Set to True for subsequent runs
        )
        
        # Print some example failures
        failures = [tc for tc in test_cases if not tc['found']]
        if failures:
            print(f"\n{len(failures)} queries failed to retrieve correct context")
            print(f"First {len(failures)} failures:")
            for fail in failures[:3]:
                print(f"  Q: {fail['question'][:80]}...")
                print(f"  Expected: {fail['context_id']}")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}")

asyncio.run(main())