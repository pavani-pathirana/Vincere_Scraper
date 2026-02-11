"""
SinhalaNormalizer - Unicode normalization for Sinhala text.

Ensures consistent Unicode representation for ML training by normalizing
Sinhala combining characters and handling special cases.
"""

import unicodedata
import re
import logging
from typing import Optional


logger = logging.getLogger(__name__)


class SinhalaNormalizer:
    """
    Normalizes Sinhala text for ML consistency.
    
    Key operations:
    - Unicode NFC normalization (compose combining characters)
    - Zero-Width Joiner (ZWJ) preservation for ligatures
    - Invisible character removal
    - Whitespace normalization
    """
    
    # Unicode ranges for Sinhala script
    SINHALA_RANGE = (0x0D80, 0x0DFF)  # Sinhala Unicode block
    
    # Zero-Width characters to preserve or remove
    ZWJ = '\u200D'  # Zero Width Joiner - PRESERVE for Sinhala ligatures
    ZWNJ = '\u200C'  # Zero Width Non-Joiner - PRESERVE for Sinhala
    ZWSP = '\u200B'  # Zero Width Space - REMOVE
    BOM = '\uFEFF'   # Byte Order Mark - REMOVE
    
    # Pattern for invisible characters to remove (but not ZWJ/ZWNJ)
    INVISIBLE_CHARS = re.compile(f'[{ZWSP}{BOM}\u2060\u2061\u2062\u2063\u2064\u206A-\u206F]')
    
    # Pattern for multiple spaces/newlines
    MULTIPLE_SPACES = re.compile(r' {2,}')
    MULTIPLE_NEWLINES = re.compile(r'\n{3,}')
    
    def __init__(self, preserve_zwj: bool = True, preserve_zwnj: bool = True):
        """
        Initialize SinhalaNormalizer.
        
        Args:
            preserve_zwj: Keep Zero-Width Joiner (recommended for Sinhala)
            preserve_zwnj: Keep Zero-Width Non-Joiner (recommended for Sinhala)
        """
        self.preserve_zwj = preserve_zwj
        self.preserve_zwnj = preserve_zwnj
        
        logger.info(f"SinhalaNormalizer initialized: ZWJ={preserve_zwj}, ZWNJ={preserve_zwnj}")
    
    def normalize(self, text: str) -> str:
        """
        Normalize Sinhala text to canonical Unicode form.
        
        Process:
        1. Unicode NFC normalization (compose combining characters)
        2. Remove invisible characters (except ZWJ/ZWNJ if configured)
        3. Normalize whitespace
        
        Args:
            text: Input text (possibly mixed Sinhala-English)
        
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Step 1: Unicode NFC normalization
        # This composes combining characters: base + combining mark → single codepoint
        # Critical for Sinhala vowel signs, repaya, rakaransaya
        text = unicodedata.normalize('NFC', text)
        
        # Step 2: Remove unwanted invisible characters
        # Keep ZWJ/ZWNJ if configured (important for Sinhala rendering)
        text = self.INVISIBLE_CHARS.sub('', text)
        
        # Optionally remove ZWJ/ZWNJ
        if not self.preserve_zwj:
            text = text.replace(self.ZWJ, '')
        if not self.preserve_zwnj:
            text = text.replace(self.ZWNJ, '')
        
        # Step 3: Normalize whitespace
        text = self._normalize_whitespace(text)
        
        return text.strip()
    
    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace without collapsing paragraph structure.
        
        - Collapse multiple spaces to single space
        - Collapse 3+ newlines to 2 newlines (preserve paragraphs)
        - Remove trailing whitespace per line
        
        Args:
            text: Input text
        
        Returns:
            Text with normalized whitespace
        """
        # Collapse multiple spaces
        text = self.MULTIPLE_SPACES.sub(' ', text)
        
        # Collapse excessive newlines (keep paragraph breaks)
        text = self.MULTIPLE_NEWLINES.sub('\n\n', text)
        
        # Remove trailing whitespace from each line
        lines = text.split('\n')
        lines = [line.rstrip() for line in lines]
        text = '\n'.join(lines)
        
        return text
    
    def has_sinhala(self, text: str) -> bool:
        """
        Check if text contains Sinhala characters.
        
        Args:
            text: Input text
        
        Returns:
            True if Sinhala characters found
        """
        if not text:
            return False
        
        return any(
            self.SINHALA_RANGE[0] <= ord(char) <= self.SINHALA_RANGE[1]
            for char in text
        )
    
    def get_sinhala_ratio(self, text: str) -> float:
        """
        Calculate ratio of Sinhala characters to total characters.
        
        Useful for filtering low-quality or non-Sinhala content.
        
        Args:
            text: Input text
        
        Returns:
            Ratio between 0.0 and 1.0
        """
        if not text:
            return 0.0
        
        # Count only alphabetic/numeric characters (ignore spaces/punctuation)
        total_chars = sum(1 for c in text if c.isalnum())
        if total_chars == 0:
            return 0.0
        
        sinhala_chars = sum(
            1 for c in text
            if self.SINHALA_RANGE[0] <= ord(c) <= self.SINHALA_RANGE[1]
        )
        
        return sinhala_chars / total_chars
    
    def fix_mojibake(self, text: str) -> str:
        """
        Attempt to fix common encoding issues (mojibake) in Sinhala text.
        
        Note: Requires 'ftfy' library for robust mojibake fixing.
        
        Args:
            text: Text with potential encoding issues
        
        Returns:
            Fixed text
        """
        try:
            import ftfy
            return ftfy.fix_text(text)
        except ImportError:
            logger.warning("ftfy not installed, skipping mojibake fix. Install with: pip install ftfy")
            return text


class TextCleaner:
    """
    Cleans HTML and formats text for ML training.
    
    Features:
    - HTML tag removal
    - HTML entity decoding
    - Excessive whitespace removal
    - Preserves paragraph structure
    """
    
    # Common patterns to remove
    HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
    HTML_COMMENT_PATTERN = re.compile(r'<!--.*?-->', re.DOTALL)
    SCRIPT_STYLE_PATTERN = re.compile(r'<(script|style)[^>]*>.*?</\1>', re.DOTALL | re.IGNORECASE)
    
    # Advertisement/noise patterns
    AD_PATTERNS = [
        r'Advertisement',
        r'\(adsbygoogle\s*=.*?\)',
        r'Read more[:：]',
        r'Continue reading',
        r'Click here',
    ]
    
    def __init__(self, preserve_newlines: bool = True, remove_ads: bool = True):
        """
        Initialize TextCleaner.
        
        Args:
            preserve_newlines: Keep newlines (paragraph structure)
            remove_ads: Remove common advertisement text
        """
        self.preserve_newlines = preserve_newlines
        self.remove_ads = remove_ads
        
        if remove_ads:
            self.ad_pattern = re.compile('|'.join(self.AD_PATTERNS), re.IGNORECASE)
        
        logger.info(f"TextCleaner initialized: preserve_newlines={preserve_newlines}, remove_ads={remove_ads}")
    
    def clean(self, html: str) -> str:
        """
        Clean HTML and extract text.
        
        Process:
        1. Remove <script> and <style> tags
        2. Remove HTML comments
        3. Remove HTML tags
        4. Decode HTML entities
        5. Remove advertisement text
        6. Normalize whitespace
        
        Args:
            html: Raw HTML content
        
        Returns:
            Clean text
        """
        if not html:
            return ""
        
        text = html
        
        # Step 1: Remove <script> and <style> content
        text = self.SCRIPT_STYLE_PATTERN.sub('', text)
        
        # Step 2: Remove HTML comments
        text = self.HTML_COMMENT_PATTERN.sub('', text)
        
        # Step 3: Replace <p>, <div>, <br> with newlines to preserve structure
        if self.preserve_newlines:
            text = re.sub(r'</(p|div|h[1-6]|li|tr)>', '\n', text, flags=re.IGNORECASE)
            text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        
        # Step 4: Remove all remaining HTML tags
        text = self.HTML_TAG_PATTERN.sub('', text)
        
        # Step 5: Decode HTML entities (&nbsp; &amp; &#3458; etc.)
        text = self._decode_html_entities(text)
        
        # Step 6: Remove advertisement text
        if self.remove_ads:
            text = self.ad_pattern.sub('', text)
        
        # Step 7: Normalize whitespace
        text = self._normalize_whitespace(text)
        
        return text.strip()
    
    def _decode_html_entities(self, text: str) -> str:
        """
        Decode HTML entities to Unicode characters.
        
        Converts: &nbsp; → space, &amp; → &, &#3458; → ඒ, etc.
        
        Args:
            text: Text with HTML entities
        
        Returns:
            Decoded text
        """
        import html
        return html.unescape(text)
    
    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace while preserving paragraph breaks.
        
        Args:
            text: Input text
        
        Returns:
            Text with normalized whitespace
        """
        # Collapse multiple spaces to single space
        text = re.sub(r' {2,}', ' ', text)
        
        # Collapse excessive newlines (keep paragraph breaks)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove spaces at line start/end
        lines = text.split('\n')
        lines = [line.strip() for line in lines]
        
        # Remove empty lines at start/end, but preserve internal structure
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        
        return '\n'.join(lines)
    
    def remove_extra_newlines(self, text: str) -> str:
        """
        Remove all extra newlines, collapse to single line.
        
        Useful for headlines or short text.
        
        Args:
            text: Input text
        
        Returns:
            Single-line text
        """
        return ' '.join(text.split())
    
    def extract_paragraphs(self, text: str, min_length: int = 20) -> list[str]:
        """
        Split text into paragraphs, filtering short ones.
        
        Args:
            text: Input text
            min_length: Minimum paragraph length (characters)
        
        Returns:
            List of paragraph strings
        """
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs]
        paragraphs = [p for p in paragraphs if len(p) >= min_length]
        return paragraphs


class TextProcessor:
    """
    Combined text processing pipeline for Sinhala news articles.
    
    Combines HTML cleaning and Sinhala normalization.
    """
    
    def __init__(
        self,
        preserve_zwj: bool = True,
        preserve_zwnj: bool = True,
        remove_ads: bool = True,
        fix_mojibake: bool = True
    ):
        """
        Initialize TextProcessor.
        
        Args:
            preserve_zwj: Keep Zero-Width Joiner
            preserve_zwnj: Keep Zero-Width Non-Joiner
            remove_ads: Remove advertisement text
            fix_mojibake: Attempt to fix encoding issues
        """
        self.cleaner = TextCleaner(preserve_newlines=True, remove_ads=remove_ads)
        self.normalizer = SinhalaNormalizer(preserve_zwj=preserve_zwj, preserve_zwnj=preserve_zwnj)
        self.fix_mojibake = fix_mojibake
        
        logger.info("TextProcessor initialized")
    
    def process(self, html: str) -> str:
        """
        Full processing pipeline: HTML → clean text → normalized Sinhala.
        
        Args:
            html: Raw HTML content
        
        Returns:
            Clean, normalized text ready for ML corpus
        """
        # Step 1: Clean HTML
        text = self.cleaner.clean(html)
        
        # Step 2: Fix encoding issues
        if self.fix_mojibake:
            text = self.normalizer.fix_mojibake(text)
        
        # Step 3: Normalize Sinhala Unicode
        text = self.normalizer.normalize(text)
        
        return text
    
    def process_headline(self, html: str) -> str:
        """
        Process headline (single line, no paragraph breaks).
        
        Args:
            html: Raw headline HTML
        
        Returns:
            Clean, normalized headline
        """
        text = self.cleaner.clean(html)
        text = self.cleaner.remove_extra_newlines(text)
        
        if self.fix_mojibake:
            text = self.normalizer.fix_mojibake(text)
        
        text = self.normalizer.normalize(text)
        
        return text


# Demo usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 70)
    print("  Sinhala Text Processing Test")
    print("=" * 70)
    
    # Test SinhalaNormalizer
    print("\n=== Testing SinhalaNormalizer ===")
    normalizer = SinhalaNormalizer()
    
    # Test Unicode normalization (combining characters)
    test_sinhala = "මෙම පාඩම ඉතා වැදගත්"  # This text in Sinhala
    normalized = normalizer.normalize(test_sinhala)
    print(f"Original: {test_sinhala}")
    print(f"Normalized: {normalized}")
    print(f"Has Sinhala: {normalizer.has_sinhala(normalized)}")
    
    # Test mixed Sinhala-English
    mixed_text = "Sri Lanka ශ්‍රී ලංකා 2024"
    ratio = normalizer.get_sinhala_ratio(mixed_text)
    print(f"\nMixed text: {mixed_text}")
    print(f"Sinhala ratio: {ratio:.2%}")
    
    # Test whitespace normalization
    messy = "මෙය    බොහෝ    spaces\n\n\n\nහා බොහෝ newlines"
    clean = normalizer.normalize(messy)
    print(f"\nMessy: {repr(messy)}")
    print(f"Clean: {repr(clean)}")
    
    # Test TextCleaner
    print("\n=== Testing TextCleaner ===")
    cleaner = TextCleaner()
    
    html = """
    <div class="article">
        <p>පළමු පරිච්ඡේදය මෙම ලිපිය</p>
        <p>දෙවන පරිච්ඡේදය වැදගත් වෙයි</p>
        <script>alert('ad');</script>
        <p>තෙවන&nbsp;පරිච්ඡේදය &#3458;හොඳයි</p>
        <!-- Comment -->
    </div>
    """
    
    clean_text = cleaner.clean(html)
    print(f"HTML input: {html[:50]}...")
    print(f"Clean output:\n{clean_text}")
    
    # Test paragraphs
    paragraphs = cleaner.extract_paragraphs(clean_text)
    print(f"\nExtracted {len(paragraphs)} paragraphs:")
    for i, para in enumerate(paragraphs, 1):
        print(f"  {i}. {para[:50]}...")
    
    # Test TextProcessor (full pipeline)
    print("\n=== Testing TextProcessor (Full Pipeline) ===")
    processor = TextProcessor()
    
    html_article = """
    <html>
    <head><title>Test</title></head>
    <body>
        <h1>ශ්‍රී    ලංකා    පුවත්</h1>
        <div class="content">
            <p>මෙම පුවත ඉතා වැදගත් වේ</p>
            <p>දෙවන  පරිච්ඡේදය&nbsp;&nbsp;මෙහි</p>
        </div>
        <script>ads.load();</script>
    </body>
    </html>
    """
    
    processed = processor.process(html_article)
    print(f"Processed article:\n{processed}")
    
    # Test headline processing
    headline_html = "<h1>පළමු   පිටුවේ   පුවත්   මෙයයි</h1>"
    headline = processor.process_headline(headline_html)
    print(f"\nHeadline: {headline}")
    
    print("\n✓ Sinhala text processing test completed!")
