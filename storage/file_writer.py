"""
FileWriter - Atomic JSON file writer for article storage.

Saves scraped articles to distributed JSON file structure with atomic writes
to prevent corruption from interruptions.
"""

import json
import os
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class FileWriter:
    """
    Writes article data to JSON files with atomic operations.
    
    Features:
    - Atomic writes (temp file → rename)
    - Directory structure: ./vincere_corpus/{website}/{category}/{article_id}.json
    - Schema validation
    - UTF-8 encoding enforcement
    - Automatic directory creation
    """
    
    # Required fields in article JSON schema
    REQUIRED_FIELDS = {
        'headline': str,
        'body': str,
        'source': str,
        'category': str,
        'date': str,
        'extraction_timestamp': str
    }
    
    # Optional fields with types
    OPTIONAL_FIELDS = {
        'url': str,
        'author': str,
        'tags': list,
        'image_urls': list,
        'word_count': int,
        'lang_code': str
    }
    
    def __init__(self, base_dir: str = "./vincere_corpus", validate_schema: bool = True):
        """
        Initialize FileWriter.
        
        Args:
            base_dir: Base directory for corpus storage
            validate_schema: Validate JSON schema before writing
        """
        self.base_dir = Path(base_dir)
        self.validate_schema = validate_schema
        
        # Create base directory if it doesn't exist
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"FileWriter initialized: base_dir={self.base_dir}, validate={validate_schema}")
    
    def write_article(
        self,
        article_data: Dict[str, Any],
        website: str,
        category: str,
        article_id: str,
        overwrite: bool = False
    ) -> Path:
        """
        Write article to JSON file with atomic operation.
        
        Path format: {base_dir}/{website}/{category}/{article_id}.json
        
        Args:
            article_data: Article data dictionary
            website: Website name (e.g., 'adaderana')
            category: Category name (e.g., 'politics')
            article_id: Unique article ID
            overwrite: Allow overwriting existing file
        
        Returns:
            Path to written file
        
        Raises:
            ValueError: If schema validation fails
            FileExistsError: If file exists and overwrite=False
            IOError: If write fails
        """
        # Validate schema
        if self.validate_schema:
            self._validate_schema(article_data)
        
        # Build file path
        file_path = self._build_file_path(website, category, article_id)
        
        # Check if file exists
        if file_path.exists() and not overwrite:
            raise FileExistsError(f"Article file already exists: {file_path}")
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Add metadata if not present
        if 'extraction_timestamp' not in article_data:
            article_data['extraction_timestamp'] = datetime.now().isoformat()
        
        # Write atomically
        try:
            self._atomic_write(file_path, article_data)
            logger.debug(f"Wrote article: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to write article {article_id}: {e}")
            raise IOError(f"Failed to write article: {e}") from e
    
    def _build_file_path(self, website: str, category: str, article_id: str) -> Path:
        """
        Build file path from components.
        
        Format: {base_dir}/{website}/{category}/{article_id}.json
        
        Args:
            website: Website name
            category: Category name
            article_id: Article ID
        
        Returns:
            Path object
        """
        # Sanitize components (remove special chars, lowercase)
        website = self._sanitize_path_component(website)
        category = self._sanitize_path_component(category)
        article_id = self._sanitize_path_component(article_id)
        
        return self.base_dir / website / category / f"{article_id}.json"
    
    def _sanitize_path_component(self, component: str) -> str:
        """
        Sanitize path component to be filesystem-safe.
        
        Removes special characters, spaces → underscores, lowercase.
        
        Args:
            component: Path component string
        
        Returns:
            Sanitized string
        """
        # Replace spaces with underscores
        component = component.replace(' ', '_')
        
        # Remove or replace problematic characters
        # Keep: alphanumeric, underscore, hyphen, dot
        import re
        component = re.sub(r'[^\w\-.]', '', component)
        
        # Lowercase for consistency
        component = component.lower()
        
        return component
    
    def _atomic_write(self, file_path: Path, data: Dict[str, Any]):
        """
        Atomically write JSON data to file.
        
        Strategy:
        1. Write to temporary file in same directory
        2. Flush and sync to disk
        3. Atomic rename (replace target file)
        
        This ensures file is never in partial/corrupted state.
        
        Args:
            file_path: Target file path
            data: Data to write
        
        Raises:
            IOError: If write fails
        """
        # Create temp file in same directory (for atomic rename)
        temp_fd, temp_path = tempfile.mkstemp(
            suffix='.json',
            dir=file_path.parent,
            text=False  # Binary mode for explicit encoding control
        )
        
        temp_path = Path(temp_path)
        
        try:
            # Write JSON to temp file with UTF-8 encoding
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(
                    data,
                    f,
                    ensure_ascii=False,  # Allow Unicode characters
                    indent=2,            # Pretty print
                    sort_keys=True       # Deterministic output
                )
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            
            # Atomic rename (replaces existing file if any)
            # This is atomic on POSIX and Windows
            temp_path.replace(file_path)
            
        except Exception as e:
            # Cleanup temp file on error
            try:
                temp_path.unlink()
            except:
                pass
            raise IOError(f"Atomic write failed: {e}") from e
    
    def _validate_schema(self, data: Dict[str, Any]):
        """
        Validate article data against required schema.
        
        Args:
            data: Article data dictionary
        
        Raises:
            ValueError: If schema validation fails
        """
        # Check required fields
        for field, expected_type in self.REQUIRED_FIELDS.items():
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
            
            if not isinstance(data[field], expected_type):
                raise ValueError(
                    f"Field '{field}' has wrong type: "
                    f"expected {expected_type.__name__}, got {type(data[field]).__name__}"
                )
            
            # Check non-empty strings
            if expected_type == str and not data[field].strip():
                raise ValueError(f"Field '{field}' cannot be empty")
        
        # Validate optional fields if present
        for field, expected_type in self.OPTIONAL_FIELDS.items():
            if field in data and not isinstance(data[field], expected_type):
                raise ValueError(
                    f"Optional field '{field}' has wrong type: "
                    f"expected {expected_type.__name__}, got {type(data[field]).__name__}"
                )
        
        logger.debug("Schema validation passed")
    
    def read_article(self, website: str, category: str, article_id: str) -> Optional[Dict[str, Any]]:
        """
        Read article from file.
        
        Args:
            website: Website name
            category: Category name
            article_id: Article ID
        
        Returns:
            Article data dictionary or None if not found
        """
        file_path = self._build_file_path(website, category, article_id)
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read article {article_id}: {e}")
            return None
    
    def article_exists(self, website: str, category: str, article_id: str) -> bool:
        """
        Check if article file exists.
        
        Args:
            website: Website name
            category: Category name
            article_id: Article ID
        
        Returns:
            True if file exists
        """
        file_path = self._build_file_path(website, category, article_id)
        return file_path.exists()
    
    def get_article_path(self, website: str, category: str, article_id: str) -> Path:
        """
        Get full path to article file (may not exist yet).
        
        Args:
            website: Website name
            category: Category name
            article_id: Article ID
        
        Returns:
            Path object
        """
        return self._build_file_path(website, category, article_id)
    
    def count_articles(self, website: Optional[str] = None, category: Optional[str] = None) -> int:
        """
        Count articles in corpus.
        
        Args:
            website: Filter by website (None for all)
            category: Filter by category (None for all)
        
        Returns:
            Count of JSON files
        """
        if website and category:
            search_path = self.base_dir / website / category
            pattern = "*.json"
        elif website:
            search_path = self.base_dir / website
            pattern = "**/*.json"
        else:
            search_path = self.base_dir
            pattern = "**/*.json"
        
        if not search_path.exists():
            return 0
        
        return len(list(search_path.glob(pattern)))
    
    def list_websites(self) -> list[str]:
        """
        List all website directories in corpus.
        
        Returns:
            List of website names
        """
        if not self.base_dir.exists():
            return []
        
        return [d.name for d in self.base_dir.iterdir() if d.is_dir()]
    
    def list_categories(self, website: str) -> list[str]:
        """
        List all category directories for a website.
        
        Args:
            website: Website name
        
        Returns:
            List of category names
        """
        website_dir = self.base_dir / website
        if not website_dir.exists():
            return []
        
        return [d.name for d in website_dir.iterdir() if d.is_dir()]
    
    def get_corpus_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the corpus.
        
        Returns:
            Dict with counts by website and category
        """
        stats = {
            'total_articles': 0,
            'websites': {},
            'total_size_bytes': 0
        }
        
        for website_dir in self.base_dir.iterdir():
            if not website_dir.is_dir():
                continue
            
            website = website_dir.name
            stats['websites'][website] = {
                'total': 0,
                'categories': {}
            }
            
            for category_dir in website_dir.iterdir():
                if not category_dir.is_dir():
                    continue
                
                category = category_dir.name
                json_files = list(category_dir.glob("*.json"))
                count = len(json_files)
                
                stats['websites'][website]['categories'][category] = count
                stats['websites'][website]['total'] += count
                stats['total_articles'] += count
                
                # Calculate size
                for file in json_files:
                    stats['total_size_bytes'] += file.stat().st_size
        
        # Convert bytes to MB
        stats['total_size_mb'] = round(stats['total_size_bytes'] / (1024 * 1024), 2)
        
        return stats


# Demo usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 70)
    print("  FileWriter Test")
    print("=" * 70)
    
    # Initialize with test directory
    writer = FileWriter(base_dir="./test_corpus", validate_schema=True)
    
    # Test article data
    article = {
        'headline': 'ශ්‍රී ලංකා එක්සත් ජාතීන්ගේ සංවිධානයට විරුද්ධ වෙයි',
        'body': 'මෙම ලිපිය ඉතා වැදගත් වේ.\n\nදෙවන පරිච්ඡේදය මෙහි.\n\nතෙවන පරිච්ඡේදය අවසානයයි.',
        'source': 'adaderana',
        'category': 'politics',
        'date': '2026-02-10',
        'url': 'https://sinhala.adaderana.lk/news/123456',
        'author': 'කතෘ නාමය',
        'word_count': 42
    }
    
    # Test write
    print("\n=== Testing Article Write ===")
    try:
        file_path = writer.write_article(
            article_data=article,
            website='adaderana',
            category='politics',
            article_id='test123'
        )
        print(f"✓ Article written to: {file_path}")
        print(f"✓ File exists: {file_path.exists()}")
        
        # Verify file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"✓ File size: {len(content)} bytes")
            print(f"✓ First 100 chars: {content[:100]}...")
        
    except Exception as e:
        print(f"✗ Write failed: {e}")
    
    # Test read
    print("\n=== Testing Article Read ===")
    read_article = writer.read_article('adaderana', 'politics', 'test123')
    if read_article:
        print(f"✓ Read article: {read_article['headline']}")
        print(f"✓ Body length: {len(read_article['body'])} chars")
        print(f"✓ Extraction timestamp: {read_article['extraction_timestamp']}")
    else:
        print("✗ Read failed")
    
    # Test exists
    print("\n=== Testing Article Exists ===")
    exists = writer.article_exists('adaderana', 'politics', 'test123')
    print(f"✓ Article exists: {exists}")
    
    not_exists = writer.article_exists('adaderana', 'politics', 'nonexistent')
    print(f"✓ Non-existent article: {not_exists}")
    
    # Test multiple articles
    print("\n=== Testing Multiple Articles ===")
    for i in range(5):
        test_article = article.copy()
        test_article['headline'] = f"පුවත් අංක {i+1}"
        test_article['body'] = f"පුවත් අංක {i+1} ශරීර."
        
        writer.write_article(
            test_article,
            website='adaderana',
            category='sports' if i % 2 else 'politics',
            article_id=f'article_{i}'
        )
    
    print(f"✓ Written 5 test articles")
    
    # Test counts
    print("\n=== Testing Counts ===")
    total = writer.count_articles()
    adaderana_count = writer.count_articles(website='adaderana')
    politics_count = writer.count_articles(website='adaderana', category='politics')
    
    print(f"✓ Total articles: {total}")
    print(f"✓ Adaderana articles: {adaderana_count}")
    print(f"✓ Adaderana politics: {politics_count}")
    
    # Test listings
    print("\n=== Testing Listings ===")
    websites = writer.list_websites()
    print(f"✓ Websites: {websites}")
    
    categories = writer.list_categories('adaderana')
    print(f"✓ Adaderana categories: {categories}")
    
    # Test corpus stats
    print("\n=== Testing Corpus Stats ===")
    stats = writer.get_corpus_stats()
    print(f"✓ Total articles: {stats['total_articles']}")
    print(f"✓ Total size: {stats['total_size_mb']} MB")
    print(f"✓ Websites: {list(stats['websites'].keys())}")
    for website, data in stats['websites'].items():
        print(f"  - {website}: {data['total']} articles")
        for category, count in data['categories'].items():
            print(f"    - {category}: {count}")
    
    # Test schema validation
    print("\n=== Testing Schema Validation ===")
    
    # Missing required field
    try:
        bad_article = {'headline': 'Test', 'body': 'Body'}
        writer.write_article(bad_article, 'test', 'test', 'bad1')
        print("✗ Should have failed validation")
    except ValueError as e:
        print(f"✓ Caught validation error: {e}")
    
    # Wrong type
    try:
        bad_article = article.copy()
        bad_article['word_count'] = "not a number"
        writer.write_article(bad_article, 'test', 'test', 'bad2')
        print("✗ Should have failed type validation")
    except ValueError as e:
        print(f"✓ Caught type error: {e}")
    
    # Empty string
    try:
        bad_article = article.copy()
        bad_article['headline'] = "   "
        writer.write_article(bad_article, 'test', 'test', 'bad3')
        print("✗ Should have failed empty string validation")
    except ValueError as e:
        print(f"✓ Caught empty string error: {e}")
    
    print("\n✓ FileWriter test completed!")
    print(f"\nTest corpus created at: {writer.base_dir.absolute()}")
