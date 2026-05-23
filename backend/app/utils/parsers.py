import io
import logging
from abc import ABC, abstractmethod
import fitz  # PyMuPDF
import docx

# Set up a logger for this module
logger = logging.getLogger(__name__)

class FileParsingError(Exception):
    """Custom exception raised when file extraction fails."""
    pass

class BaseParser(ABC):
    """
    The interface contract. Any class inheriting from this MUST implement extract_text.
    """
    @abstractmethod
    def extract_text(self, file_bytes: bytes) -> str:
        pass

class PDFParser(BaseParser):
    def extract_text(self, file_bytes: bytes) -> str:
        logger.info("Attempting to parse PDF document.")
        try:
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                full_text = ""  
                for page in doc:  
                    full_text += page.get_text()
                return full_text
        except Exception as e:
            logger.error(f"Failed to parse PDF: {str(e)}")
            raise FileParsingError(f"PDF Parsing failed: {str(e)}")   

class DocxParser(BaseParser):
    def extract_text(self, file_bytes: bytes) -> str:
        logger.info("Attempting to parse DOCX document.")
        try:
            
            file_stream = io.BytesIO(file_bytes)
            doc = docx.Document(file_stream)
            full_text = "\n".join([p.text for p in doc.paragraphs])
            return full_text
            
        except Exception as e:
            logger.error(f"Failed to parse DOCX: {str(e)}")
            raise FileParsingError(f"DOCX Parsing failed: {str(e)}")
        
class ParserFactory:
    """
    The Factory: Give it a filename, and it returns the correct parser object.
    """
    @staticmethod
    def get_parser(filename: str) -> BaseParser:
        extension = filename.split(".")[-1].lower()
        
        if extension == "pdf":
            return PDFParser()
        elif extension in ["doc", "docx"]:
            return DocxParser()
        else:
            raise ValueError(f"Unsupported file extension: {extension}")

# --- Helper function for your API routes to call ---
def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """
    HINT: Your FastAPI route will just call this single function!
    It abstracts away all the complexity above.
    """
    parser = ParserFactory.get_parser(filename)
    return parser.extract_text(file_bytes)