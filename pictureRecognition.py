import os
# 通过 pip install volcengine-python-sdk[ark] 安装方舟SDK
from volcenginesdkarkruntime import Ark

# 替换 <Model> 为模型的Model ID
model = "doubao-1.5-vision-pro-32k-250115"

# 初始化Ark客户端，从环境变量中读取您的API Key
client = Ark(
    api_key='63c9cfad-2269-4805-88be-89ff32545dad',
)


def getPestsFromPicture(pictureUrl):
    '''
    识别图片，返回识别的作物类别和3种病虫害类型
    :param pictureUrl: 图片url
    :return: json结果
    '''
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
                    {"type": "text",
                     "text": '判断图片中出现的农作物类型，并判断图片农作物中可能出现的病虫害，给出3种不同的病虫害名称和对应准确率，最终以非格式化的json格式输出，例如 {"pest": "小麦","diseases": [{"diseases_name": "小麦蚜虫","accuracy_rate": "0.9"}, {"diseases_name": "小麦白粉病","accuracy_rate": "0.2"}, {"diseases_name": "小麦霜霉病","accuracy_rate": "0.1"}]}。如果图片中没有包含农作物，则输出 ： {"pest":"无","diseases":null}'
                     },
                    # 图片信息，希望模型理解的图片
                    {"type": "image_url",
                     "image_url": {
                         "url": pictureUrl}
                     },
                ],
            }
        ],
    )
    return response.choices[0].message.content


if __name__ == '__main__':
    result = getPestsFromPicture(
        "https://nf-file.hbatg.com/nfshop/MANAGER//787da99578c74ed1a53fedffe832bc50.png")
    print(result)