import connectToMysql
import csv

# 从mysql中获取对应作物的title数据，并保存在csv文件中

def getPestsData(SearchCategory):
    '''
    从mysql获取对应作物类型的title数据,保存在csv文件中
    :param SearchCategory: 作物类型 rice  wheat ...
    :return:
    '''
    results = connectToMysql.query_data_from_mysql("SELECT id, title FROM pests WHERE category = %s;", (SearchCategory,))
    print(results)

    #     存储结果到csv文件
    with open('./data/' + SearchCategory + '_pests.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id','title'])
        writer.writerows(results)


if __name__ == '__main__':
    getPestsData('corn')
