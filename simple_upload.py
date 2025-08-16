import os
import argparse
import sys
import glob  # 我们用 glob 库来查找文件
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_vertexai.vectorstores import MatchingEngine

# --- 配置区 ---
# (和之前一样，从环境变量读取)
try:
    PROJECT_ID = os.environ["PROJECT_ID"]
    REGION = os.environ["REGION"]
    BUCKET_NAME = os.environ["BUCKET_NAME"]
    ME_INDEX_ID = os.environ["ME_INDEX_ID_VALUE"]
    ME_INDEX_ENDPOINT_ID = os.environ["ME_INDEX_ENDPOINT_ID_VALUE"]
except KeyError as e:
    print(f"错误：环境变量 {e} 未设置。")
    print("请确认你已经运行了 'source setup_env.sh' 并且脚本中的变量已正确设置。")
    sys.exit(1)


# --- 核心功能 ---
def upload_single_pdf(file_path: str, vector_store: MatchingEngine):
    """加载、分割单个PDF，并将向量上传到已初始化的 vector_store"""
    try:
        print(f"\n▶️ 开始处理文件: {os.path.basename(file_path)}")
        
        # 1. 加载 PDF
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # 2. 分割文本
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = text_splitter.split_documents(documents)
        print(f"  - ✂️ 已分割成 {len(docs)} 个文本块。")

        # 3. 添加文档（这会自动处理向量生成和上传）
        print(f"  - ⏳ 正在上传到 Matching Engine...")
        vector_store.add_documents(docs)
        print(f"  - ✅ 成功上传: {os.path.basename(file_path)}")
        
    except Exception as e:
        print(f"  - ❌ 处理文件失败: {os.path.basename(file_path)}。错误: {e}")


# --- 脚本主入口 ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="扫描目录并上传所有PDF到 Vertex AI Matching Engine。")
    parser.add_argument(
        "directory",
        nargs="?",  # '?' 表示这个参数是可选的
        default="./data",  # 如果不提供参数，则默认为 './data' 目录
        help="包含PDF文件的目录路径。默认为 './data'。"
    )
    args = parser.parse_args()
    pdf_directory = args.directory

    if not os.path.isdir(pdf_directory):
        print(f"错误: 目录 '{pdf_directory}' 不存在。")
        sys.exit(1)

    # 查找目录中所有 .pdf 和 .PDF 文件
    print(f"🔍 正在扫描目录 '{pdf_directory}' 中的PDF文件...")
    pdf_files = glob.glob(os.path.join(pdf_directory, "*.pdf"))
    pdf_files.extend(glob.glob(os.path.join(pdf_directory, "*.PDF")))

    if not pdf_files:
        print("🤷 在该目录中没有找到PDF文件。")
        sys.exit(0)

    print(f"✨ 找到了 {len(pdf_files)} 个PDF文件，准备开始处理。")

    # ---- 初始化一次，供所有文件使用 ----
    print("☁️ 正在初始化并连接到 Vertex AI Matching Engine... (只需一次)")
    embeddings_service = VertexAIEmbeddings(model_name="textembedding-gecko@003", project=PROJECT_ID)
    vector_store_instance = MatchingEngine.from_components(
        project_id=PROJECT_ID,
        region=REGION,
        gcs_bucket_name=BUCKET_NAME.replace("gs://", "").strip("/"),
        embedding=embeddings_service,
        index_id=ME_INDEX_ID,
        endpoint_id=ME_INDEX_ENDPOINT_ID,
    )
    print("🔗 连接成功！")
    # ------------------------------------

    # 循环处理找到的每个文件
    for pdf_path in pdf_files:
        upload_single_pdf(pdf_path, vector_store_instance)

    print("\n🎉 全部任务完成！")
    