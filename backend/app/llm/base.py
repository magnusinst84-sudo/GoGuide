class LLMProvider:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError
    def health(self) -> dict:
        raise NotImplementedError
    def model_name(self) -> str:
        raise NotImplementedError
