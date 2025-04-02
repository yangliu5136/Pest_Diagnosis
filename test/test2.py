import json

pests_json = "{\"pest\":\"小麦\",\"diseases\":[{\"小麦蚜虫\":\"0.7\"},{\"小麦锈病\":\"0.6\"},{\"小麦白粉病\":\"0.5\"}]}"

try:

    data = json.loads(pests_json)
    print(data)

except json.JSONDecodeError as e:
    print(f"JSON解析失败: {e}")
except Exception as e:
    print(f"发生错误: {e}")
