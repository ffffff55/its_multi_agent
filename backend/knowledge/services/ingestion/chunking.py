"""文档切分规则。长文档只切当前这一篇，避免同一次加载的其它文档被重复切开。"""
import os
from collections.abc import Callable, Iterable

# 必须分成两条。"\n**" 和 "\n\n" 写在相邻行且漏了逗号时，会被粘成一条，标题和空行都切不开。
MD_SEPARATORS = [
    "\n## ",
    "\n**",
    "\n\n",
    "\n",
    " ",
    "",
]

SHORT_DOCUMENT_CHARS = 3000


def chunk_documents(
    documents: Iterable,
    split_documents: Callable,
    threshold: int = SHORT_DOCUMENT_CHARS,
) -> list:
    final_document_chunks = []
    for doc in documents:
        if len(doc.page_content) < threshold:
            final_document_chunks.append(doc)
            continue
        documents_chunks_list = split_documents([doc])
        for document_chunk in documents_chunks_list:
            source = document_chunk.metadata.get("source") or ""
            title = os.path.basename(source) if source else ""
            document_chunk.page_content = f"文档来源:{title}\n{document_chunk.page_content}"
        final_document_chunks.extend(documents_chunks_list)
    return final_document_chunks
