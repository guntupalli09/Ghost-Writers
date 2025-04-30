from typing import List, Tuple

def chunk_days(days: int, chunk_size: int = 7) -> List[Tuple[int, int]]:
    """
    Split a number of days into weekly chunks.
    
    Args:
        days (int): Total number of days
        chunk_size (int): Size of each chunk (default 7 for weeks)
        
    Returns:
        List[Tuple[int, int]]: List of (start_day, end_day) tuples
    """
    return [(i + 1, min(i + chunk_size, days)) for i in range(0, days, chunk_size)]

def chunk_text_by_length(text: str, max_tokens: int = 1200) -> List[str]:
    """
    Split text into chunks based on token length.
    
    Args:
        text (str): Text to chunk
        max_tokens (int): Maximum tokens per chunk
        
    Returns:
        List[str]: List of text chunks
    """
    paragraphs = text.split("\n\n")
    chunks, current = [], ""
    for para in paragraphs:
        if len(current + para) < max_tokens:
            current += "\n\n" + para
        else:
            chunks.append(current.strip())
            current = para
    if current:
        chunks.append(current.strip())
    return chunks

def chunk_calendar_by_weeks(calendar_text: str) -> List[str]:
    """
    Split calendar text into weekly chunks.
    
    Args:
        calendar_text (str): Calendar markdown text
        
    Returns:
        List[str]: List of weekly calendar chunks
    """
    return [chunk.strip() for chunk in calendar_text.split("---\n\n") if chunk.strip()] 