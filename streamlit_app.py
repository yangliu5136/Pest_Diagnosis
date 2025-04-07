import streamlit as st

from PIL import Image
import requests, json, os, sys

package_path = os.path.abspath('/Users/yangliu/PycharmProjects/Pest_Diagnosis/test')  # 替换为实际的路径
sys.path.append(package_path)
from test import test4

st.set_page_config(page_title="病虫害自动诊断", page_icon="🦜🔗")
st.title("病虫害自动诊断")

diseases = []


def picture_recognition(pictureUrl):
    '''
    图片识别接口
    :param pictureUrl:
    :return:
    '''
    url = "http://127.0.0.1:5001/pictureRecognition"
    dict_picture = {"pictureUrl": pictureUrl}
    payload = json.dumps(dict_picture)
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    response = requests.request("POST", url, headers=headers, data=payload)
    response.encoding = 'utf-8'
    return response.text


def get_pests(pestsCategory, pictureRecognitionResult):
    '''
    获取病虫害数据
    :param pestsCategory:
    :param pictureRecognitionResult:
    :return:
    '''
    url = "http://127.0.0.1:5001/getPests"
    dictate_request = {"pestsCategory": pestsCategory, "pictureRecognitionResult": pictureRecognitionResult}
    payload = json.dumps(dictate_request)
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text


# 创建一个文件上传控件
uploaded_file = st.file_uploader("上传图片", type=["jpg", "png", "jpeg"])

# 检查是否有文件被上传
if uploaded_file is not None:
    # 将上传的文件转换为PIL图像对象
    img = Image.open(uploaded_file)
    st.image(img, caption='上传的图片',width=30, use_container_width=True)
    file_path = "/Users/yangliu/PycharmProjects/Pest_Diagnosis/images"
    local_path = os.path.join(file_path, uploaded_file.name)
    with open(local_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.write("图片已保存到本地路径：", local_path)
    response = test4.upload_file(uploaded_file.name, local_path)
    print("response=====", response)
    picture_url = json.loads(response).get("result")

    print("picture_url=====", picture_url)
    response = picture_recognition(picture_url)
    print("response====", response)
    diseases = json.loads(response)['result']
    print("diseases====", diseases)

    # 下拉单选框：选择范例
    st.subheader("选择作物品种: ")

    # 用户选择的作物品种
    pest_select = st.selectbox(
        label='请选择作物品种：',
        options=("水稻", "小麦"),
        index=0,
        format_func=str,
    )

    if st.button("开始诊断病虫害"):
        response = get_pests(pest_select, diseases)
        print('response====', response)
        result = json.loads(response)['result']
        for disease in result:
            st.image(disease['cover'], width=100)
            st.write("病虫害名称：", disease['title'])
            st.write("可信度：", f"{float(disease['accuracy_rate']) * 100:.2f}%")
            st.write("症状：", disease['symptom'])
            st.write("发生规律：", disease['occurrence_regularity'])
            st.write("危害：", disease['harm'])
            if disease['agricultural_control']:
                st.write("农业防治：", disease['agricultural_control'])
            else:
                st.write("农业防治：", "无")

            if disease['chemical_control']:
                st.write("化学防治：", disease['chemical_control'])
            else:
                st.write("化学防治：", "无")

            if disease['physical_control']:
                st.write("物理防治：", disease['physical_control'])
            else:
                st.write("物理防治：", "无")

            if disease['biological_control']:
                st.write("生物防治：", disease['biological_control'])
            else:
                st.write("生物防治：", "无")
            st.markdown("---")


