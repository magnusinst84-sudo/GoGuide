import datetime
from app.schemas.llm import LLMRequest, LLMResponse
from app.llm.factory import get_llm_provider
from app.llm.prompts import construct_prompt

def process_chat_request(request: LLMRequest) -> LLMResponse:
    provider = get_llm_provider()
    
    # 1. Receive context via request
    # 2. Validate it (Pydantic does this automatically in API layer)
    # 3. Construct grounded prompt
    full_prompt = construct_prompt(request.prompt, request.context)
    
    # 4. Call provider
    try:
        response_text = provider.generate(full_prompt)
    except Exception as e:
        raise RuntimeError(f"LLM Provider failed: {str(e)}")
        
    # 5. Return structured response
    return LLMResponse(
        response_text=response_text,
        generated_at=datetime.datetime.utcnow().isoformat() + "Z",
        model=provider.model_name()
    )