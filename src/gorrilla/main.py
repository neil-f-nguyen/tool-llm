from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from api.registry import APIRegistry
from api.generator import CodeGenerator

# Initialize FastAPI app
app = FastAPI(title="Gorilla API")
registry = APIRegistry()
generator = CodeGenerator(registry)

class QueryRequest(BaseModel):
    query: str

@app.post("/generate")
async def generate_code(request: QueryRequest):
    """Generate code based on user query"""
    try:
        code = await generator.generate_code(request.query)
        return {"code": code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/functions")
async def list_functions():
    """List all available API functions"""
    return {
        "functions": [
            {
                "name": func.name,
                "description": func.description,
                "provider": func.provider,
                "documentation_url": func.documentation_url
            }
            for func in registry.functions.values()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 