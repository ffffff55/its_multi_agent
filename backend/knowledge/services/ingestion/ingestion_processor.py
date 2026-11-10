import os.path
from repositories.vector_store_repository import VectorStoreRepository
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import  RecursiveCharacterTextSplitter
from langchain_community.vectorstores.utils import filter_complex_metadata
from  utils.markdown_utils import MarkDownUtils
from services.ingestion.chunking import MD_SEPARATORS, chunk_documents
import  logging
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

class IngestionProcessor:
    """
    文档摄入类：（摄入：加载、切分、存储）
    """

    def __init__(self):

        self.vector_store = VectorStoreRepository()
        self.document_spliter=RecursiveCharacterTextSplitter(
            chunk_size=1500,  # 长文档内容分块的阈值（略大一些。永远考虑语义优先）
            chunk_overlap=200,# 给一定重合度
            separators=MD_SEPARATORS,
        )

    def ingest_file(self, md_path: str) -> int:
        """
        文档完整操作
        包含阶段：文件的加载->文档的切割->文档的存储
        Args:
            md_path:文件的路径

        Returns:
          int: 保存成功的文档数
        """

        # 1. 根据文件的路径加载得到文档列表
        file_extension = os.path.splitext(md_path)[1].lower()
        # a. 按文件类型选择加载器：PDF 用 PyPDFLoader，文本/md 用 TextLoader
        try:
            if file_extension == ".pdf":
                text_loader = PyPDFLoader(file_path=md_path)
            else:
                text_loader = TextLoader(file_path=md_path, encoding="utf-8")
            # b. 加载文件返回文档列表
            documents = text_loader.load()
        except Exception as e:
            logger.error(f"文件：{md_path}没有加载到,原因:{str(e)}")
            raise Exception(f"文件：{md_path}没有加载到,原因:{str(e)}")
        # 1.为什么们要切分？ 目的：1.防止token限制  2.内容过多（大量噪音）--->LLM参考的上下文不精准。回复质量不好【1.二次利用模型对检索到大量内容的chunk 做降噪（1.只提取 2.总结）2.利用嵌入模型二次优化chunk】
        # 2.到底要不要切？【文档内容大不大、多不多】如果文档内容比较多，一般都要切【上下文会断掉，语义不完整】。相反，如果内容较少，不用切（将整个内容作为一个完整的chunk[语义不丢]）
        # ①.(改写查询)---1.学习大模型主要要学习哪些技术？ 2.在学习大模型阶段要学些哪些常见的技术栈 3. 4.
        # ②. 用这4个问题去分别检索（多路召回） 1个query:4:answer  4个query:16:answer ---16个文档块（去重）--->10个（1:二次利用模型对检索到大量内容的chunk 2:.利用嵌入模型二次优化chunk）--->留4个--->LLM(1.稳 2.精准)


        for doc in documents:
            # PDF 等非 Markdown 文件没有 md 标题结构，直接用文件名作为标题
            if file_extension in (".md", ".markdown"):
                doc.metadata['title'] = MarkDownUtils.extract_title(md_path)
            else:
                doc.metadata['title'] = os.path.basename(md_path)



        # 2.切分文档得到文档块列表
        # 2.1 动态机制切分
        # a.如果文档内容不大，直接将这内容作为一个chunk(不用切分)
        # b.如果内容比较大，分析大内容的数据结构，然后为他定制切分策略。采用header rejection:标题注入（保留没一块的业务背景、上下文）

        # 短文档整篇保留。长文档只切当前这一篇，标题仍按「文档来源:文件名」接在块前面。
        final_document_chunks = chunk_documents(
            documents,
            self.document_spliter.split_documents,
        )


        #  3.切分后文档块的元数据校验(过滤不被向量数据库支持的元数据清除掉)
        clean_documents_chunks=filter_complex_metadata(final_document_chunks)

        #  4. 无效性检查（校验page_content的是否合法（不能为空））
        valid_documents_chunks=[document for document in  clean_documents_chunks if document.page_content.strip()]

        if not valid_documents_chunks:
            logger.error("切分后的文档块没有任何的内容")
            return 0

        # 5 .存储文档块到向量数据库
        total_documents_chunks=self.vector_store.add_documents(valid_documents_chunks)


        # 6 .返回保存成功的文档块数
        return total_documents_chunks


if __name__ == '__main__':
    # text_loader = TextLoader(file_path="C:\\Users\\Administrator\\Desktop\\0004-开机之后无任何反应怎么办？.md",encoding="utf-8")
    # # b. 加载文件返回文档列表(TextLoader返回的文档列表中有且只有一个文档对象)
    # documents = text_loader.load()
    # for doc  in documents:
    #     print(doc.page_content)

    # from langchain_community.document_loaders import UnstructuredMarkdownLoader

    # loader = UnstructuredMarkdownLoader(
    #     "C:\\Users\\Administrator\\Desktop\\0004-开机之后无任何反应怎么办？.md",
    #     mode="single",
    #     strategy="fast",
    # )
    # docs = loader.load()
    # print(docs[0].metadata)
    # print(docs[0].page_content)

    ingest_processor=IngestionProcessor()

    ingest_processor.ingest_file("C:\\Users\\Administrator\\Desktop\\0430-联想手机K900常见问题汇总.md")
    # ingest_processor.ingest_file("C:\\Users\\Administrator\\Desktop\\0188-手机、平板上的画面能无线传输到电视上播放吗？.md")







