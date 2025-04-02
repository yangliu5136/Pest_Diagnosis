import pymysql
from pymysql import Error


def query_data_from_mysql(sql, *params):
    '''
    从mysql数据库中查询数据
    :param sql: sql语句
    :param params: sql语句中的占位符 ，必须是元素格式
    :return: 查询结果
    '''
    try:
        # 1. 建立数据库连接
        connection = pymysql.connect(
            host='10.0.0.7',  # 数据库服务器地址
            user='root',  # 数据库用户名
            password='9twubYgsPxiFJz0T',  # 数据库密码
            database='nfshop',  # 数据库名称
            charset='utf8mb4',  # 字符编码
            cursorclass=pymysql.cursors.DictCursor  # 结果以字典形式返回
        )

        print("成功连接到MySQL数据库")

        # 2. 创建游标对象
        with connection.cursor() as cursor:
            # 3. 执行SQL查询
            cursor.execute(sql, params)

            # 4. 获取查询结果
            results = cursor.fetchall()

            print(f"共查询到 {len(results)} 条记录:")
            return results

    except Error as e:
        print(f"数据库错误: {e}")
    finally:
        # 6. 关闭连接
        if 'connection' in locals() and connection.open:
            connection.close()
            print("MySQL连接已关闭")


# 调用函数执行查询"SELECT * FROM pests WHERE  title IN ("稻瘟病", "水稻纹枯病", "水稻白叶枯病");"
if __name__ == '__main__':
    result = query_data_from_mysql("SELECT * FROM pests WHERE  title IN ('稻瘟病', '水稻纹枯病', '水稻白叶枯病');")
    print(result)
