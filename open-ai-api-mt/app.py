import os
import json
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import openai
from dotenv import load_dotenv
from loguru import logger

logger.add("logs/file.log")

logger.info("Starting the application")


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

# Set OpenAI API key
openai.api_key = api_key

logger.info("API key set")

# Define Pydantic models for structured translation outputs
class DefaultTranslation(BaseModel):
    original_text: str = Field(..., description="Original Bangla text")
    translated_text: str = Field(..., description="Translated text in target language")
    formal_alternative: Optional[str] = Field(None, description="More formal translation if applicable")
    notes: Optional[str] = Field(None, description="Translation notes or cultural context")

class WordPair(BaseModel):
    bangla: str = Field(..., description="Bangla word")
    translated: str = Field(..., description="Translated word")
    part_of_speech: Optional[str] = Field(None, description="Part of speech")

class TranslationError(BaseModel):
    error: str = Field(..., description="Error message")
    original_text: Optional[str] = Field(None, description="Original text that caused the error")

class TranslationRequest(BaseModel):
    text: str = Field(..., description="Text to translate")
    target_language: str = Field(..., description="Target language for translation")

# Factory function to create the appropriate model based on structure type
def create_translation_model(structure_type: str):
    models = {
        "default": DefaultTranslation,
    }
    return models.get(structure_type, DefaultTranslation)

def translate_text_structured(text: str, target_language: str, structure_type: str = "default"):
    """
    Translate text from Bangla to the target language using GPT with structured output
    validated by Pydantic models.
    """
    try:
        # Define system prompts based on structure type
        system_prompts = {
            "default": f"""You are a professional translator. Translate the Bangla text to {target_language}.
                          Return a JSON object with the following structure:
                          {{
                              "original_text": "The original Bangla text",
                              "translated_text": "The translated text in {target_language}",
                              "formal_alternative": "A more formal translation if applicable",
                              "notes": "Any translation notes or cultural context"
                          }}"""
        }
        
        # Use the appropriate prompt based on structure type
        system_prompt = system_prompts.get(structure_type, system_prompts["default"])
        
        response = openai.ChatCompletion.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.3
        )
        
        # Parse the JSON response
        result = response.choices[0].message.content.strip()
        
        # Clean up the result to ensure it's valid JSON
        if result.startswith("```json"):
            result = result.replace("```json", "", 1)
        if result.endswith("```"):
            result = result[:-3]
            
        # Parse the JSON and validate with Pydantic
        json_data = json.loads(result.strip())
        
        # Get the appropriate model class based on structure type
        ModelClass = create_translation_model(structure_type)
        
        # Validate and create the model instance
        validated_data = ModelClass(**json_data)
        
        # Return as dictionary
        return validated_data.dict()
    
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors
        error = TranslationError(
            error=f"JSON parsing error: {str(e)}",
            original_text=text
        )
        return error.dict()
        
    except Exception as e:
        # Handle general errors
        error = TranslationError(
            error=f"Translation error: {str(e)}",
            original_text=text
        )
        return error.dict()

# Create FastAPI appS
app = FastAPI(
    title="Structured Bangla Translator API",
    description="API for translating Bangla text to other languages with structured output",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/translate", response_model=Dict[str, Any])
async def translate(request: TranslationRequest):
    """
    Translate Bangla text to the target language with structured output.
    """
    if not request.text:
        raise HTTPException(status_code=400, detail="Text to translate is required")
    if not request.target_language:
        raise HTTPException(status_code=400, detail="Target language is required")
   
    logger.info("Translating text")
    result = translate_text_structured(
        text=request.text,
        target_language=request.target_language
    )

    logger.info(
        f"""
        Translation result:
        {result}
        """
    )

    logger.info("Translation complete")

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result

@app.get("/")
async def root():
    """
    Root endpoint returning API information
    """
    return {
        "name": "Structured Bangla Translator API",
        "version": "1.0.0",
        "description": "API for translating Bangla text to other languages with structured output",
        "endpoints": {
            "/translate": "POST - Translate text with structured output",
            "/docs": "GET - API documentation (Swagger UI)",
            "/redoc": "GET - Alternative API documentation (ReDoc)"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)