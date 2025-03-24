import os
# 通过 pip install volcengine-python-sdk[ark] 安装方舟SDK
from volcenginesdkarkruntime import Ark

# 替换 <Model> 为模型的Model ID
model = "doubao-1.5-vision-pro-32k-250115"

# 初始化Ark客户端，从环境变量中读取您的API Key
client = Ark(
    api_key='63c9cfad-2269-4805-88be-89ff32545dad',
)

# 创建一个对话请求
response = client.chat.completions.create(
    # 指定您部署了视觉理解大模型的推理接入点ID
    model=model,
    messages=[
        {
            # 指定消息的角色为用户
            "role": "user",
            "content": [
                # 文本消息，希望模型根据图片信息回答的问题
                {"type": "text", "text": "判断图片中出现的农作物类型，并判断图片农作物中可能出现的病虫害，给出至少3个病虫害名称，最终以json格式输出，例如 {\"pest\":\"小麦\",\"diseases\":[{\"0\":\"水稻蚜虫\"},{\"1\":\"白粉病\"},{\"2\":\"小麦赤霉病\"}]} 。如果图片中没有包含农作物，则输出 ： {\"pest\":\"无\",\"diseases\":null}"
                 },
                # 图片信息，希望模型理解的图片
                {"type": "image_url",
                 "image_url": {"url": "https://nf-file.hbatg.com/nfshop/MEMBER/1784489769980743680//5e13e97e47d84a05aa2e5834b46a621a.jpg"}
                 },
            ],
        }
    ],
)

print(response.choices[0].message.content)
