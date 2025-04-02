import json

json_data = "{\"pest\": \"水稻\",\"diseases\": [{\"diseases_name\": \"稻瘟病\",\"accuracy_rate\": \"0.8\"}, {\"diseases_name\": \"水稻纹枯病\",\"accuracy_rate\": \"0.7\"}, {\"diseases_name\": \"水稻螟虫\",\"accuracy_rate\": \"0.6\"}]}"
data = json.loads(json_data)
# for disease_dict in data['diseases']:
#     for k,v in disease_dict.items():
#         print(k,v)


# list1 = [{'id': 71, 'category': 'rice', 'title': '水稻粘虫', 'symptom': '主要以幼虫食叶，大面积发生时可将作物叶片全部吃光；在抽穗后则咬断小穗，落粒满田，造成减产或无收。形态特征:成虫头部与胸部灰褐色，腹部暗褐色。前翅灰黄褐色、黄色或橙色，变化很多。后翅暗褐色，向基部色渐淡。卵半球形，初产白色渐变黄色，有光泽。幼虫头红褐色，头盖有网纹，额扁，两侧有褐色粗纵纹，略呈八字形，外侧有褐色网纹。体色由淡绿至浓黑。蛹红褐色。 ', 'occurrence_regularity': '一年发生2-8代。成虫对糖醋液趋性强，产卵趋向黄枯叶片。在稻田多把卵产在中上部半枯黄的叶尖上，着卵枯叶纵卷成条状。初孵幼虫有群集性，1、2龄幼虫多在基部叶背或分蘖叶背处危害，3龄后食量大增，5-6龄进入暴食阶段，食光叶片或把穗头咬断，睛天白昼潜伏在植株根际处土缝中，傍晚后或阴天再到植株上危害。', 'harm': '啃食叶片、影响光合作用、减产', 'agricultural_control': None, 'chemical_control': '在水稻粘虫卵孵盛期用10%阿维菌素悬浮剂6-8毫升/亩，喷雾；或16%甲维茚虫威悬浮剂10-15毫升/亩，喷雾；或20%甲维甲虫肼20-25毫升/亩，喷雾；或5%阿维茚虫威悬浮剂30-40毫升/亩，喷雾；35%氯虫苯甲酰胺水分散粒剂4-6克/亩，喷雾。', 'physical_control': None, 'biological_control': None, 'cover': 'https://nf-file.hbatg.com/nfshop/MANAGER//9e1fefa8b415416dbfcab24249fdb8f4.png'}]
#
# dic1 = list1[0]
#
# dic1.update({'accuracy_rate':'0.9'})
# print(dic1)

result = [{'id': 71, 'category': 'rice'}, {'id': 72, 'category': 'rice2'}]
for i in result:
    i.update({'accuracy_rate': '0.1'})

print(result)
