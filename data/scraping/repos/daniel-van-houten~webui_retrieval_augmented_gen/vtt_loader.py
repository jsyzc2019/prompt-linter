import logging
from typing import List, Optional
import re

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain.document_loaders.helpers import detect_file_encodings

logger = logging.getLogger(__name__)


class VttLoader(BaseLoader):
    """Load vtt files.

    Args:
        file_path: Path to the file to load.

        encoding: File encoding to use. If `None`, the file will be loaded
        with the default system encoding.

        autodetect_encoding: Whether to try to autodetect the file encoding
            if the specified encoding fails.
    """

    def __init__(
        self,
        file_path: str,
        encoding: Optional[str] = None,
        autodetect_encoding: bool = False,
    ):
        """Initialize with file path."""
        self.file_path = file_path
        self.encoding = encoding
        self.autodetect_encoding = autodetect_encoding

    def load(self) -> List[Document]:
        """Load from file path."""
        text = ""
        try:
            with open(self.file_path, encoding=self.encoding) as f:
                text = f.read()
                text = self.clean_vtt(text)

        except UnicodeDecodeError as e:
            if self.autodetect_encoding:
                detected_encodings = detect_file_encodings(self.file_path)
                for encoding in detected_encodings:
                    logger.debug("Trying encoding: ", encoding.encoding)
                    try:
                        with open(self.file_path, encoding=encoding.encoding) as f:
                            text = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
            else:
                raise RuntimeError(f"Error loading {self.file_path}") from e
        except Exception as e:
            raise RuntimeError(f"Error loading {self.file_path}") from e

        metadata = {"source": self.file_path}
        return [Document(page_content=text, metadata=metadata)]


    def clean_vtt(self, vtt_text):
        # Regular expression pattern for matching speaker and text
        pattern = r'<v (.*?)>(.*?)</v>'

        # Find all matches in the VTT text
        matches = re.findall(pattern, vtt_text)

        # Create a cleaned text by joining speaker and text for each match
        cleaned_text = ''
        prev_speaker = None
        for speaker, text in matches:
            if speaker == prev_speaker:
                cleaned_text = cleaned_text.rstrip() + ' ' + text
            else:
                cleaned_text += f'\n{speaker}: {text}'
            prev_speaker = speaker

        return cleaned_text.lstrip()
