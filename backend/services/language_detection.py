"""
Language Detection Service for Memo AI Coach
Robust multi-method language detection with fallback strategies
"""

import logging
from typing import Dict, Any, Optional, Tuple
from enum import Enum

# Import Language enum from config models to ensure consistency
try:
    from models.config_models import Language
except ImportError:
    from backend.models.config_models import Language

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DetectionMethod(str, Enum):
    """Language detection methods"""
    POLYGLOT = "polyglot"
    LANGDETECT = "langdetect"
    PYCLD2 = "pycld2"
    HEURISTIC = "heuristic"

# Language enum is now imported from config_models

class DetectionResult:
    """Language detection result with confidence and method information"""
    
    def __init__(self, language: Language, confidence: float, method: DetectionMethod, 
                 raw_result: Any = None):
        self.language = language
        self.confidence = confidence
        self.method = method
        self.raw_result = raw_result
    
    def __str__(self):
        return f"Language: {self.language}, Confidence: {self.confidence:.2f}, Method: {self.method}"

class RobustLanguageDetector:
    """Robust language detector using multiple methods with fallback strategies"""
    
    def __init__(self, confidence_threshold: float = 0.7):
        self.confidence_threshold = confidence_threshold
        self._initialize_detectors()
    
    def _initialize_detectors(self):
        """Initialize all available language detection methods"""
        self.detectors = {}
        
        # Try to initialize Polyglot
        try:
            from polyglot.detect import Detector
            self.detectors[DetectionMethod.POLYGLOT] = Detector
            logger.info("Polyglot language detector initialized")
        except ImportError:
            logger.warning("Polyglot not available - skipping Polyglot detection")
        
        # Try to initialize Langdetect
        try:
            import langdetect
            self.detectors[DetectionMethod.LANGDETECT] = langdetect
            logger.info("Langdetect language detector initialized")
        except ImportError:
            logger.warning("Langdetect not available - skipping Langdetect detection")
        
        # Try to initialize Pycld2
        try:
            import pycld2
            self.detectors[DetectionMethod.PYCLD2] = pycld2
            logger.info("Pycld2 language detector initialized")
        except ImportError:
            logger.warning("Pycld2 not available - skipping Pycld2 detection")
        
        if not self.detectors:
            logger.warning("No language detection libraries available - using heuristic detection only")
    
    def detect_language(self, text: str) -> DetectionResult:
        """
        Detect language using multiple methods with fallback strategies
        
        Args:
            text: Text to analyze
            
        Returns:
            DetectionResult with language, confidence, and method information
        """
        if not text or len(text.strip()) < 3:
            logger.warning("Text too short for reliable language detection")
            return DetectionResult(Language.UNKNOWN, 0.0, DetectionMethod.HEURISTIC)
        
        # Try primary detection methods
        for method in [DetectionMethod.POLYGLOT, DetectionMethod.LANGDETECT, DetectionMethod.PYCLD2]:
            if method in self.detectors:
                try:
                    result = self._detect_with_method(text, method)
                    if result and result.confidence >= self.confidence_threshold:
                        logger.info(f"Language detected using {method}: {result}")
                        return result
                except Exception as e:
                    logger.warning(f"Error with {method} detection: {e}")
        
        # Fallback to heuristic detection
        logger.info("Using heuristic fallback detection")
        return self._heuristic_detection(text)
    
    def _detect_with_method(self, text: str, method: DetectionMethod) -> Optional[DetectionResult]:
        """Detect language using a specific method"""
        try:
            if method == DetectionMethod.POLYGLOT:
                return self._detect_with_polyglot(text)
            elif method == DetectionMethod.LANGDETECT:
                return self._detect_with_langdetect(text)
            elif method == DetectionMethod.PYCLD2:
                return self._detect_with_pycld2(text)
        except Exception as e:
            logger.error(f"Error in {method} detection: {e}")
            return None
    
    def _detect_with_polyglot(self, text: str) -> DetectionResult:
        """Detect language using Polyglot"""
        try:
            detector = self.detectors[DetectionMethod.POLYGLOT](text)
            language_code = detector.language.code.lower()
            confidence = detector.confidence
            
            # Map language codes to our supported languages
            if language_code in ['en', 'eng']:
                detected_lang = Language.EN
            elif language_code in ['es', 'spa']:
                detected_lang = Language.ES
            else:
                detected_lang = Language.UNKNOWN
                confidence *= 0.5  # Reduce confidence for unsupported languages
            
            return DetectionResult(detected_lang, confidence, DetectionMethod.POLYGLOT, detector)
            
        except Exception as e:
            logger.error(f"Polyglot detection error: {e}")
            return None
    
    def _detect_with_langdetect(self, text: str) -> DetectionResult:
        """Detect language using Langdetect"""
        try:
            from langdetect import detect, DetectorFactory
            # Set seed for consistent results
            DetectorFactory.seed = 0
            
            language_code = detect(text)
            confidence = 0.8  # Langdetect doesn't provide confidence scores
            
            # Map language codes to our supported languages
            if language_code == 'en':
                detected_lang = Language.EN
            elif language_code == 'es':
                detected_lang = Language.ES
            else:
                detected_lang = Language.UNKNOWN
                confidence *= 0.5
            
            return DetectionResult(detected_lang, confidence, DetectionMethod.LANGDETECT, language_code)
            
        except Exception as e:
            logger.error(f"Langdetect detection error: {e}")
            return None
    
    def _detect_with_pycld2(self, text: str) -> DetectionResult:
        """Detect language using Pycld2"""
        try:
            import pycld2
            is_reliable, text_bytes_found, details = pycld2.detect(text)
            
            if is_reliable and details:
                language_code = details[0][1].lower()
                confidence = details[0][2] / 100.0  # Convert percentage to 0-1 scale
                
                # Map language codes to our supported languages
                if language_code in ['en', 'eng']:
                    detected_lang = Language.EN
                elif language_code in ['es', 'spa']:
                    detected_lang = Language.ES
                else:
                    detected_lang = Language.UNKNOWN
                    confidence *= 0.5
                
                return DetectionResult(detected_lang, confidence, DetectionMethod.PYCLD2, details)
            
            return None
            
        except Exception as e:
            logger.error(f"Pycld2 detection error: {e}")
            return None
    
    def _heuristic_detection(self, text: str) -> DetectionResult:
        """Heuristic language detection based on common patterns"""
        try:
            # Common Spanish words and patterns
            spanish_indicators = [
                'el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le',
                'por', 'son', 'con', 'para', 'al', 'del', 'las', 'los', 'una', 'como', 'más',
                'pero', 'sus', 'me', 'hasta', 'hay', 'donde', 'han', 'quien', 'están', 'estado',
                'desde', 'todo', 'nos', 'durante', 'todos', 'podemos', 'así', 'mismo', 'ya',
                'vez', 'puede', 'cada', 'ellos', 'e', 'esto', 'mí', 'antes', 'ellos', 'sí',
                'dentro', 'su', 'también', 'solo', 'pueden', 'así', 'mío', 'antes', 'ellos',
                'sí', 'dentro', 'su', 'también', 'solo', 'pueden', 'así', 'mío', 'antes'
            ]
            
            # Common English words and patterns
            english_indicators = [
                'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for',
                'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his',
                'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my',
                'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if',
                'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like',
                'time', 'no', 'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your',
                'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then', 'now',
                'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after',
                'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new',
                'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us'
            ]
            
            # Count Spanish and English indicators
            text_lower = text.lower()
            spanish_count = sum(1 for word in spanish_indicators if word in text_lower)
            english_count = sum(1 for word in english_indicators if word in text_lower)
            
            # Calculate confidence based on indicator ratio
            total_indicators = spanish_count + english_count
            if total_indicators == 0:
                return DetectionResult(Language.UNKNOWN, 0.3, DetectionMethod.HEURISTIC)
            
            spanish_ratio = spanish_count / total_indicators
            english_ratio = english_count / total_indicators
            
            # Determine language based on ratio
            if spanish_ratio > 0.6:
                confidence = min(0.8, spanish_ratio)
                return DetectionResult(Language.ES, confidence, DetectionMethod.HEURISTIC)
            elif english_ratio > 0.6:
                confidence = min(0.8, english_ratio)
                return DetectionResult(Language.EN, confidence, DetectionMethod.HEURISTIC)
            else:
                # Mixed or unclear - default to English with low confidence
                return DetectionResult(Language.EN, 0.4, DetectionMethod.HEURISTIC)
                
        except Exception as e:
            logger.error(f"Heuristic detection error: {e}")
            return DetectionResult(Language.UNKNOWN, 0.2, DetectionMethod.HEURISTIC)
    
    def get_detection_summary(self, text: str) -> Dict[str, Any]:
        """Get comprehensive language detection summary"""
        result = self.detect_language(text)
        
        return {
            "detected_language": result.language.value,
            "confidence": result.confidence,
            "method": result.method.value,
            "text_length": len(text),
            "available_methods": [method.value for method in self.detectors.keys()],
            "confidence_threshold": self.confidence_threshold,
            "is_confident": result.confidence >= self.confidence_threshold
        }
    
    def validate_language_support(self, language: str) -> bool:
        """Check if a language is supported"""
        try:
            return Language(language) in [Language.EN, Language.ES]
        except ValueError:
            return False
