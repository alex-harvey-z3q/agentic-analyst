"""
Centralized configuration for the agentic analyst project.

All environment-variable driven configuration lives here so that:
- model choices can be changed without touching code
- secrets are not hard-coded
- runtime vs optional settings are explicit
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load variables from a local .env file if present.
# In production, environment variables are expected to be set externally.
load_dotenv()


# ---------------------------------------------------------------------
# Required configuration
# ---------------------------------------------------------------------

# OpenAI API key is required for all LLM and embedding calls.
# Fail fast if it is missing.
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


# ---------------------------------------------------------------------
# LLM configuration (optional, with defaults)
# ---------------------------------------------------------------------

# Default model used for text generation.
# Can be overridden via environment variable for cost/quality trade-offs.
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")

# Embedding model used by the retrieval layer.
# Keeping this configurable allows future experimentation without refactors.
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")


# ---------------------------------------------------------------------
# Local storage paths (optional, with defaults)
# ---------------------------------------------------------------------

# Directory where LlamaIndex persists its local index, docstore, and metadata.
# This allows the index to be reused across runs without rebuilding embeddings.
INDEX_PERSIST_DIR = os.getenv("INDEX_PERSIST_DIR", "data/index_storage")

# Path to the lyrics corpus file used to build the index.
# Default points to the checked-in Beatles lyrics corpus.
CORPUS_PATH = os.getenv("CORPUS_PATH", "data/corpus/beatles_lyrics.txt")


# ---------------------------------------------------------------------
# API clients
# ---------------------------------------------------------------------

# OpenAI client used throughout the project.
# Instantiated once here so all calls share configuration.
client = OpenAI(api_key=OPENAI_API_KEY)
