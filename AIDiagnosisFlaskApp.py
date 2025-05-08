from flask import Flask, request
import pictureRecognition
import connectToMysql
from llama_index.core import PromptTemplate
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

import csv, json, ast
import time, logging
from pathlib import Path
from typing import List, Dict
import chromadb
from llama_index.core.schema import TextNode
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore

app = Flask(__name__)
# 防止传输的数据被转义
app.json.ensure_ascii = False
app.config['JSONIFY_TIMEOUT'] = 60  # 设置JSON响应超时为30秒

# 配置日志
logging.basicConfig(
    filename='api.log',  # 日志文件名
    level=logging.INFO,  # 日志级别
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 作物默认的3条病虫害数据
rice_default_pests = ("稻瘟病", "水稻纹枯病", "水稻白叶枯病")
wheat_default_pests = ("小麦锈病", "小麦白粉病", "小麦赤霉病")
corn_default_pests = ("玉米大斑病", "玉米小斑病", "玉米锈病")


@app.before_request
def log_request_info():
    """记录请求信息"""
    logging.info(f"Request: {request.method} {request.url}")
    logging.info(f"Headers: {dict(request.headers)}")
    if request.method in ['POST', 'PUT']:
        logging.info(f"Body: {request.get_json()}")


@app.after_request
def log_response_info(response):
    """记录响应信息"""
    logging.info(f"Response: {response.status} - {response.get_json()}")
    return response


class Config:
    # model存储路径
    EMBEDING_MEDEL_PATH = './LLM/BAAI/bge-small-zh-v1.5'
    RICE_FILE_PATH = './data/rice_pests.csv'
    WHEAT_FILE_PATH = './data/wheat_pests.csv'
    CORN_FILE_PATH = './data/corn_pests.csv'

    # deepseek 配置信息
    # API_BASE = "https://api.deepseek.com/v1"  # vLLM的默认端点
    # MODEL_NAME = "deepseek-chat"
    # API_KEY = "sk-fb4e0293a2df4bf2a622d14e5e18b148"  # vLLM默认不需要密钥

    # 阿里云
    # API_KEY = "sk-47f9e5d9876f4d6ca71622b35953a753"
    # API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    # MODEL_NAME = "deepseek-r1"

    # 火山引擎的deepseek
    # API_BASE = "https://ark.cn-beijing.volces.com/api/v3"  # vLLM的默认端点
    # MODEL_NAME = "deepseek-r1-250120"
    # API_KEY = "e6e19c79-3735-4ff1-80c7-8da8c6fe0fd9"  # vLLM默认不需要密钥

    # 豆包doubao-lite-32k-240828
    API_BASE = "https://ark.cn-beijing.volces.com/api/v3"  # vLLM的默认端点
    MODEL_NAME = "doubao-lite-32k-240828"
    API_KEY = "e6e19c79-3735-4ff1-80c7-8da8c6fe0fd9"  # vLLM默认不需要密钥

    TIMEOUT = 60  # 请求超时时间

    # 向量数据库存储路径
    DATA_DIR = "./data"
    VECTOR_DB_DIR = "./chroma_db"
    PERSIST_DIR = "./storage"

    RICE_COLLECTION_NAME = "rice_pests"
    WHEAT_COLLECTION_NAME = "wheat_pests"
    CORN_COLLECTION_NAME = "corn_pests"

    TOP_K = 1


QA_TEMPLATE = (
    "<|im_start|>system\n"
    "你是一个专业的智能问答助手，请严格根据以下信息回答问题：\n"
    "相关信息：\n{context_str}\n<|im_end|>\n"
    "<|im_start|>user\n{query_str}<|im_end|>\n"
    "<|im_start|>assistant\n"
)

response_template = PromptTemplate(QA_TEMPLATE)


def init_models():
    embeding_model = HuggingFaceEmbedding(
        model_name=Config.EMBEDING_MEDEL_PATH
    )
    # LLM
    llm = OpenAILike(
        model=Config.MODEL_NAME,
        api_base=Config.API_BASE,
        api_key=Config.API_KEY,
        temperature=0.3,
        max_tokens=1024,
        timeout=Config.TIMEOUT,
        is_chat_model=True,  # 适用于对话模型
        additional_kwargs={"stop": ["<|im_end|>"]},  # DeepSeek的特殊停止符
        TOKENIZERS_PARALLELISM=True
    )

    Settings.embed_model = embeding_model
    Settings.llm = llm

    # 验证模型
    test_embedding = embeding_model.get_text_embedding("测试文本")
    print(f"Embedding维度验证：{len(test_embedding)}")

    return embeding_model, llm


# ================== 数据处理 ==================
def load_and_validate_json_files(file_path: str):
    '''将供需数据加载进来，每一行为一个基点，返回list
    file_path:数据cvs文件
    '''
    all_data = []
    with open(file_path, mode='r', newline='', encoding='UTF-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            print(row)
            # 将每一行转换为字典，{'id':'病虫害id','cotent':'其余内容'}，并添加到列表中
            content = str(row[1:])
            row_dict = {'id': row[0], 'content': content}
            all_data.append(row_dict)
    print(f"成功加载{file_path} 中 {len(all_data)} 个数据")
    return all_data


def create_nodes(demand_data: list) -> list[TextNode]:
    """添加ID稳定性保障"""
    nodes = []
    for entry in demand_data:
        pest_id = entry["id"]
        pest_info = entry["content"]

        # 生成稳定ID（避免重复）
        node_id = f"{pest_id}"
        # 创建node
        node = TextNode(
            text=pest_info,
            id_=node_id,  # 显式设置稳定ID
            metadata={
                "id": pest_id,
                "pest_info": pest_info,
            }
        )
        nodes.append(node)
    print(f"生成 {len(nodes)} 个文本节点（ID示例：{nodes[0].id_}）")
    return nodes


# ================== 向量存储 ==================
def init_vector_store(collection_data_name, nodes: list[TextNode]) -> VectorStoreIndex:
    '''将数据进行向量存储
    :param collection_data_name: 要存储的集合名称
    :param nodes: 节点
    :return:
    '''
    chroma_client = chromadb.PersistentClient(path=Config.VECTOR_DB_DIR)
    chroma_collection = chroma_client.get_or_create_collection(
        name=collection_data_name,
        metadata={"hnsw:space": "cosine"}
    )

    # 确保存储上下文正确初始化
    storage_context = StorageContext.from_defaults(
        vector_store=ChromaVectorStore(chroma_collection=chroma_collection)
    )

    # 判断是否需要新建索引
    if chroma_collection.count() == 0 and nodes is not None:
        print(f"创建新索引（{len(nodes)}个节点）...")

        # 显式将节点添加到存储上下文
        storage_context.docstore.add_documents(nodes)

        index = VectorStoreIndex(
            nodes,
            storage_context=storage_context,
            show_progress=True
        )
        # 双重持久化保障
        storage_context.persist(persist_dir=Config.PERSIST_DIR)
        index.storage_context.persist(persist_dir=Config.PERSIST_DIR)  # <-- 新增
    else:
        print("加载已有索引...")
        storage_context = StorageContext.from_defaults(
            persist_dir=Config.PERSIST_DIR,
            vector_store=ChromaVectorStore(chroma_collection=chroma_collection)
        )
        index = VectorStoreIndex.from_vector_store(
            storage_context.vector_store,
            storage_context=storage_context,
            embed_model=Settings.embed_model
        )

    # 安全验证
    print("\n存储验证结果：")
    doc_count = len(storage_context.docstore.docs)
    print(f"DocStore记录数：{doc_count}")

    if doc_count > 0:
        sample_key = next(iter(storage_context.docstore.docs.keys()))
        print(f"示例节点ID：{sample_key}")
    else:
        print("警告：文档存储为空，请检查节点添加逻辑！")

    return index


def init_storage(data_type, data_file_path):
    '''
    初始化数据，及向量存储
    :param data_type: 数据集合类型
    :param data_file_path: 数据文件路径
    :return:
    '''
    # 仅当需要更新数据时执行
    print("\n初始化数据...")
    raw_data = load_and_validate_json_files(data_file_path)
    nodes = create_nodes(raw_data)
    # if not Path(Config.VECTOR_DB_DIR).exists():
    #     print("\n初始化数据...")
    #     raw_data = load_and_validate_json_files(data_file_path)
    #     nodes = create_nodes(raw_data)
    # else:
    #     nodes = None  # 已有数据时不加载

    print("\n初始化向量存储...")
    start_time = time.time()
    index = init_vector_store(data_type, nodes)
    print(f"索引加载耗时：{time.time() - start_time:.2f}s")
    return index

@app.route('/test', methods=['GET'])
def test():
    response = {"success": True,
                "message": "success",
                "code": 200,
                "timestamp": int(time.time()),
                "result": "result"}
    content = json.dumps(response, ensure_ascii=False)
    print(content)
    return content

@app.route('/pictureRecognition', methods=['POST'])
def picture_recognition():
    '''
    调用图片识别大模型，识别图片中的作物和病虫害类别
    :return:
    '''
    pictureUrl = request.json.get('pictureUrl')
    print("pictureUrl=====", pictureUrl)
    if not pictureUrl:
        return {"success": True, "message": "传入url为空", "code": 201}
    result = pictureRecognition.getPestsFromPicture(pictureUrl)
    response = {"success": True,
                "message": "success",
                "code": 200,
                "timestamp": int(time.time()),
                "result": result}
    content = json.dumps(response, ensure_ascii=False)
    print(content)
    return content


@app.route('/getPests', methods=['POST'])
def get_pests():
    '''
    获取病虫害匹配数据接口，传入参数： pestsCategory = '水稻' '小麦' ...
    pictureRecognitionResult : json 格式
    :return:
    '''
    # 传入作物品种类型
    pestsCategory = request.json.get('pestsCategory')
    # 传入图片识别返回的结果
    pictureRecognitionResult = request.json.get('pictureRecognitionResult')
    # 先判断传入作物类别是否正确
    if pestsCategory not in ("水稻", "小麦","玉米"):
        return {"success": True, "message": "传入作物类型不正确", "code": 201}
    # 如果传入作物类别正确，则解析图片识别的结果json
    try:
        data = json.loads(pictureRecognitionResult)
        print(data, "图片识别结果解析成功")
        # 判断图片识别的作物类型和传入作物类型是否一致，如果一致，执行rag，如果不一致，直接用户输入作物默认3条病虫害数据
        pictureRecognitionResultPest = data["pest"]
        if pictureRecognitionResultPest != pestsCategory:
            #         作物默认病虫害，查询mysql，返回数据
            if pestsCategory == '水稻':
                sql = "SELECT * FROM pests WHERE  title IN ('稻瘟病', '水稻纹枯病', '水稻白叶枯病');"
                result = connectToMysql.query_data_from_mysql(sql)
                for i in result:
                    i.update({'accuracy_rate': '0.1'})
                response = {"success": True,
                            "message": "success",
                            "code": 200,
                            "timestamp": int(time.time()),
                            "result": result}
                content = json.dumps(response, ensure_ascii=False)
                return content
            elif pestsCategory == '小麦':
                sql = "SELECT * FROM pests WHERE  title IN ('小麦锈病', '小麦白粉病', '小麦赤霉病');"
                result = connectToMysql.query_data_from_mysql(sql)
                for i in result:
                    i.update({'accuracy_rate': '0.1'})
                response = {"success": True,
                            "message": "success",
                            "code": 200,
                            "timestamp": int(time.time()),
                            "result": result}
                content = json.dumps(response, ensure_ascii=False)
                return content
            elif pestsCategory == '玉米':
                sql = "SELECT * FROM pests WHERE  title IN ('玉米大斑病', '玉米小斑病', '玉米锈病');"
                result = connectToMysql.query_data_from_mysql(sql)
                for i in result:
                    i.update({'accuracy_rate': '0.1'})
                response = {"success": True,
                            "message": "success",
                            "code": 200,
                            "timestamp": int(time.time()),
                            "result": result}
                content = json.dumps(response, ensure_ascii=False)
                return content
        else:
            # 图片识别的作物类型和传入的作物类型一致，执行rag
            # 创建查询引擎
            if pestsCategory == '水稻':
                index = rice_index
            elif pestsCategory == '小麦':
                index = wheat_index
            elif pestsCategory == '玉米':
                index = corn_index

            query_engine = index.as_query_engine(
                similarity_top_k=Config.TOP_K,
                text_qa_template=response_template,
                verbose=True
            )
            # 先取出图片识别返回的3个病虫害类别，再进行匹配
            records_list = []
            for disease_dict in data['diseases']:

                diseases_name = disease_dict['diseases_name']
                print('diseases name=====', diseases_name)
                response = query_engine.query(diseases_name)
                # 处理返回数据

                print("\n检索得到的需求数据：")
                for idx, node in enumerate(response.source_nodes, 1):
                    meta = node.metadata
                    print(f"\n[{idx}] {meta['id']}")
                    print(f"  返回内容：{meta['pest_info']}")
                    pest_info_list = ast.literal_eval(meta['pest_info'])
                    # response_dict = {}
                    # response_dict['id'] = meta['id']
                    # response_dict['title'] = pest_info_list[0]
                    sql = "SELECT * FROM pests WHERE id = %s ;"
                    sql_result = connectToMysql.query_data_from_mysql(sql, (meta['id'],))
                    dict_temp = sql_result[0]
                    dict_temp.update({'accuracy_rate': disease_dict['accuracy_rate']})
                    print('sql_result =====', dict_temp)
                    records_list.append(dict_temp)

            response = {"success": True,
                        "message": "success",
                        "code": 200,
                        "timestamp": int(time.time()),
                        "result": records_list}

            content = json.dumps(response, ensure_ascii=False)

            return content
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return {"success": True, "message": "JSON解析失败", "code": 201}
    except Exception as e:
        print(f"发生错误: {e}")
        return {"success": True, "message": "JSON解析错误", "code": 201}



@app.route('/getDetail', methods=['GET'])
def get_detail():
    # 传入病虫害id
    id = request.args.get('id')
    sql = "SELECT * FROM pests WHERE id = %s ;"
    result = connectToMysql.query_data_from_mysql(sql,id)
    response = {"success": True,
                "message": "success",
                "code": 200,
                "timestamp": int(time.time()),
                "result": result}
    content = json.dumps(response, ensure_ascii=False)
    return content

if __name__ == "__main__":
    embed_model, llm = init_models()
    rice_index = init_storage(Config.RICE_COLLECTION_NAME, Config.RICE_FILE_PATH)
    wheat_index = init_storage(Config.WHEAT_COLLECTION_NAME, Config.WHEAT_FILE_PATH)
    corn_index = init_storage(Config.CORN_COLLECTION_NAME, Config.CORN_FILE_PATH)

    app.run(host='0.0.0.0', port=5001, debug=True)
