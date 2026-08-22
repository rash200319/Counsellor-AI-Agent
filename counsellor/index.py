"""Vector index load / create helpers."""

from __future__ import annotations

import os

from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)


def load_query_engine(folder_path: str, persist_dir: str):
    """Load a persisted index or create one from the knowledge base."""
    if not os.path.exists(persist_dir):
        print(f"Index not found at {persist_dir}. Creating and persisting new index...")
        os.makedirs(persist_dir, exist_ok=True)

        if not os.path.exists(folder_path) or not os.listdir(folder_path):
            print(
                f"Error: Knowledge base directory '{folder_path}' "
                "is empty or does not exist."
            )
            return VectorStoreIndex([]).as_query_engine()

        documents = SimpleDirectoryReader(folder_path).load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=persist_dir)
    else:
        print(f"Loading index from persisted directory: {persist_dir}")
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context)

    return index.as_query_engine()
