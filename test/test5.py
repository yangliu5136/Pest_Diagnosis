import streamlit as st
import pandas as pd
from PIL import Image
import os
import subprocess

uploaded_file = st.file_uploader("选择图片")
if uploaded_file is not None:
    # To read file as bytes:
    img = Image.open(uploaded_file)
    st.image(img, caption='上传的图片', use_container_width=True)
    # 将上传的文件保存到 Streamlit 的缓存目录下
    with open(os.path.join(os.getcwd(), uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())



    # 获取保存后的文件路径（相对路径）
    # image_path = os.path.join("images", uploaded_file.name)
    # image_url = f"/static/{uploaded_file.name}"  # 注意：这种方法在某些 Streamlit 版本中可能需要额外配置才能正确工作。通常，直接使用路径即可。

    # 显示图片和提供链接（如果需要）

    file_path = os.path.join(os.getcwd(),uploaded_file.name)
    shell = 'curl --location --request POST \'https://www.hbatg.com/api/common/common/common/upload/file\' \
   --header \'accesstoken: eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyQ29udGV4dCI6IntcInVzZXJuYW1lXCI6XCJtMTM1KioqKjUxMzZcIixcIm5pY2tOYW1lXCI6XCLmnajmn7NcIixcImZhY2VcIjpcImh0dHBzOi8vbmYtZmlsZS5oYmF0Zy5jb20vbmZzaG9wL01FTUJFUi8xNzg0NDg5NzY5OTgwNzQzNjgwLy83YTYwMjM0YThiMGM0NDFhYTFiNGNhMTRiYWQ4Njg1Ni5qcGVnXCIsXCJpZFwiOlwiMTc4NDQ4OTc2OTk4MDc0MzY4MFwiLFwibG9uZ1Rlcm1cIjpmYWxzZSxcInJvbGVcIjpcIk1FTUJFUlwifSIsInN1YiI6Im0xMzUqKioqNTEzNiIsImV4cCI6MTc0MzY4Mjg5NH0.Jd3lzgAphjJUOBEh0TY5IUkoQAsoxEhr0YGw5yrG2xo\' \
   --header \'content-type: multipart/form-data; boundary=----WebKitFormBoundaryyw6lb8Oztsr8PUIP\' \
   --form \'file=@\"/Users/yangliu/PycharmProjects/Pest_Diagnosis/test/ark_demo_img_1.png\"\''
    print(shell)
    result = subprocess.run([shell], capture_output=True, text=True)

    # result = subprocess.run(shell, stdout=subprocess.PIPE, text=True)
    print(result.stdout)
    # os.system(shell)


