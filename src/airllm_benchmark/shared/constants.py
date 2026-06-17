DEFAULT_MAX_NEW_TOKENS = 20
DEFAULT_DEVICE = "cpu"
DEFAULT_MODELS_DIR = "./models"
DEFAULT_RESULTS_DIR = "./results"

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_GENERATE_EP = "/api/generate"
OLLAMA_HEALTH_EP = "/api/tags"

VALID_METHODS = ("ollama", "hf_baseline", "airllm", "all")
