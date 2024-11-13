import abc
import io
from abc import abstractmethod
from typing import Type, Optional, Dict
import re
import PyPDF2
import docx


class FileManager(abc.ABC):
    @abstractmethod
    def __init__(self, content: bytes) -> None:
        self.content = content

    @abstractmethod
    def read(self) -> Optional[str]:
        pass


def clean_text(text: str) -> str:
    text = re.sub(
        r"(?<!\n)\n(?!\n)", " ", text
    )  # Reemplaza saltos de línea simples por un espacio.
    text = re.sub(
        r"\n+", "\n", text
    )  # Reemplaza múltiples saltos de línea consecutivos por uno solo.
    text = re.sub(r"[ \t]+", " ", text)  # Quita múltiples espacios y tabulaciones.
    return text


class PDFFileManager(FileManager):
    def __init__(self, content: bytes) -> None:
        super().__init__(content)

    def read(self) -> Optional[str]:
        try:
            with io.BytesIO(self.content) as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in range(len(reader.pages)):
                    text += reader.pages[page].extract_text()

                cleaned_text = clean_text(text)
                return cleaned_text

        except Exception as e:
            return f"An error occurred while reading the PDF: {e}"


class WordFileManager(FileManager):
    def __init__(self, content: bytes) -> None:
        super().__init__(content)

    def read(self) -> Optional[str]:
        try:
            with io.BytesIO(self.content) as file:
                doc = docx.Document(file)
                text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                return text
        except Exception as e:
            return f"An error occurred while reading the Word file: {e}"


class TextFileManager(FileManager):
    def __init__(self, content: bytes) -> None:
        super().__init__(content)

    def read(self) -> Optional[str]:
        try:
            return self.content.decode("utf-8")
        except Exception as e:
            return f"An error occurred while reading the text file: {e}"


strategies: Dict[str, Type[FileManager]] = {
    "pdf": PDFFileManager,
    "docx": WordFileManager,
    "txt": TextFileManager,
}


class FileReader:
    def __init__(self, content: bytes, extension: str) -> None:
        if extension not in strategies:
            raise ValueError(f"Unsupported file type: {extension}")
        self.manager = strategies[extension](content)

    def read_file(self) -> Optional[str]:
        return self.manager.read()
