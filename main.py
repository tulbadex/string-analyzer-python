from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import hashlib
import re
from datetime import datetime
from typing import Optional, List, Dict

# Initialize FastAPI app
api = FastAPI(title="String Analysis Service")

# Data storage
stored_strings = {}

class StringData(BaseModel):
    value: str

class StringAnalysis:
    @staticmethod
    def compute_hash(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()
    
    @staticmethod
    def check_palindrome(text: str) -> bool:
        cleaned = text.lower()
        return cleaned == cleaned[::-1]
    
    @staticmethod
    def count_unique_chars(text: str) -> int:
        return len(set(text))
    
    @staticmethod
    def count_words(text: str) -> int:
        return len(text.split())
    
    @staticmethod
    def build_char_frequency(text: str) -> Dict[str, int]:
        frequency = {}
        for char in text:
            frequency[char] = frequency.get(char, 0) + 1
        return frequency
    
    @classmethod
    def analyze(cls, text: str) -> Dict:
        return {
            "length": len(text),
            "is_palindrome": cls.check_palindrome(text),
            "unique_characters": cls.count_unique_chars(text),
            "word_count": cls.count_words(text),
            "sha256_hash": cls.compute_hash(text),
            "character_frequency_map": cls.build_char_frequency(text)
        }

class QueryParser:
    @staticmethod
    def extract_filters(query_text: str) -> Dict:
        query_lower = query_text.lower()
        conditions = {}
        
        # Palindrome detection
        if "palindrom" in query_lower:
            conditions["is_palindrome"] = True
        
        # Word count patterns
        word_patterns = {
            "single word": 1,
            "two word": 2, 
            "three word": 3
        }
        for pattern, count in word_patterns.items():
            if pattern in query_lower:
                conditions["word_count"] = count
                break
        
        # Length constraints
        longer_match = re.search(r"longer than (\d+)", query_lower)
        if longer_match:
            conditions["min_length"] = int(longer_match.group(1)) + 1
        
        shorter_match = re.search(r"shorter than (\d+)", query_lower)
        if shorter_match:
            conditions["max_length"] = int(shorter_match.group(1)) - 1
        
        # Character containment
        char_match = re.search(r"contain(?:s|ing)? the letter ([a-z])", query_lower)
        if char_match:
            conditions["contains_character"] = char_match.group(1)
        
        if "first vowel" in query_lower:
            conditions["contains_character"] = "a"
        
        return conditions

class StringFilter:
    @staticmethod
    def matches_criteria(string_data: Dict, filters: Dict) -> bool:
        props = string_data["properties"]
        
        if "is_palindrome" in filters and props["is_palindrome"] != filters["is_palindrome"]:
            return False
        
        if "min_length" in filters and props["length"] < filters["min_length"]:
            return False
        
        if "max_length" in filters and props["length"] > filters["max_length"]:
            return False
        
        if "word_count" in filters and props["word_count"] != filters["word_count"]:
            return False
        
        if "contains_character" in filters and filters["contains_character"] not in string_data["value"]:
            return False
        
        return True
    
    @classmethod
    def apply_filters(cls, data_list: List[Dict], filters: Dict) -> List[Dict]:
        return [item for item in data_list if cls.matches_criteria(item, filters)]

@api.get("/")
def root():
    return RedirectResponse("/docs")

@api.post("/strings", status_code=201)
def add_string(data: StringData):
    if not data.value:
        raise HTTPException(status_code=422, detail="Invalid data type for value field")
    
    string_hash = StringAnalysis.compute_hash(data.value)
    
    if string_hash in stored_strings:
        raise HTTPException(status_code=409, detail="String already exists")
    
    analysis = StringAnalysis.analyze(data.value)
    
    string_record = {
        "id": string_hash,
        "value": data.value,
        "properties": analysis,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    stored_strings[string_hash] = string_record
    return string_record

@api.get("/strings/{string_value}")
def retrieve_string(string_value: str):
    for record in stored_strings.values():
        if record["value"] == string_value:
            return record
    
    raise HTTPException(status_code=404, detail="String does not exist in database")

@api.get("/strings")
def list_strings(
    is_palindrome: Optional[bool] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    word_count: Optional[int] = None,
    contains_character: Optional[str] = None
):
    # Validate parameters
    if min_length is not None and min_length < 0:
        raise HTTPException(status_code=400, detail="Invalid query parameter values or types")
    if max_length is not None and max_length < 0:
        raise HTTPException(status_code=400, detail="Invalid query parameter values or types")
    if word_count is not None and word_count < 0:
        raise HTTPException(status_code=400, detail="Invalid query parameter values or types")
    if contains_character is not None and len(contains_character) != 1:
        raise HTTPException(status_code=400, detail="Invalid query parameter values or types")
    
    filters = {}
    if is_palindrome is not None:
        filters["is_palindrome"] = is_palindrome
    if min_length is not None:
        filters["min_length"] = min_length
    if max_length is not None:
        filters["max_length"] = max_length
    if word_count is not None:
        filters["word_count"] = word_count
    if contains_character is not None:
        filters["contains_character"] = contains_character
    
    all_records = list(stored_strings.values())
    filtered_records = StringFilter.apply_filters(all_records, filters)
    
    return {
        "data": filtered_records,
        "count": len(filtered_records),
        "filters_applied": {
            "is_palindrome": is_palindrome,
            "min_length": min_length,
            "max_length": max_length,
            "word_count": word_count,
            "contains_character": contains_character
        }
    }

@api.get("/strings/filter-by-natural-language")
def natural_language_filter(query: str):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Unable to parse natural language query")
    
    parsed_conditions = QueryParser.extract_filters(query)
    
    if not parsed_conditions:
        raise HTTPException(status_code=400, detail="Unable to parse natural language query")
    
    all_records = list(stored_strings.values())
    filtered_records = StringFilter.apply_filters(all_records, parsed_conditions)
    
    return {
        "data": filtered_records,
        "count": len(filtered_records),
        "interpreted_query": {
            "original": query,
            "parsed_filters": parsed_conditions
        }
    }

@api.delete("/strings/{string_value}", status_code=204)
def remove_string(string_value: str):
    for hash_key, record in stored_strings.items():
        if record["value"] == string_value:
            del stored_strings[hash_key]
            return
    
    raise HTTPException(status_code=404, detail=f"String {string_value} not found!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)