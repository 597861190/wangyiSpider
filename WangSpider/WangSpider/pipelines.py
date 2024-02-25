import pymysql.cursors
from twisted.enterprise import adbapi



class MysqlTwistedPipeline(object):
    """
    异步机制将数据写入到mysql数据库中
    """

    #创建初始化函数，当通过此类创建对象时首先被调用的方法
    def __init__(self, dbpool):
        self.dbpool = dbpool

    #创建一个静态方法, 静态方法的加载内存优先级高于init方法
    @classmethod
    #名称固定的
    def from_settings(cls,settings):
        #先将setting中链接数据库所需的内容取出，构造一个地点
        dbparams = dict(host=settings['MYSQL_HOST'],
                        port=settings['MYSQL_PORT']
                        ,user=settings['MYSQL_USER']
                        ,password=settings['MYSQL_PASSWORD'],
                        charset="utf8mb4",
                        database=settings['MYSQL_DATABASE'],
                        #游标设置
                        cursorclass=pymysql.cursors.DictCursor,
                        #设置编码是否使用Unicode
                        use_unicode=True
                        )
        #通过Twisted框架提供的容器连接数据库，pymysql是数据库的模块名
        dbpool = adbapi.ConnectionPool("pymysql", **dbparams)
        #无需直接导入 dbmodule 只需要告诉 adbapi.ConnectionPool 构造器你用的数据库模块的名称比如pymysql
        return cls(dbpool)

    def process_item(self, item, spider):
        #使用Twisted异步的将item数据插入数据库中
        print(item)
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)
        # return item

    def do_insert(self, cursor, item):
        #执行具体的插入语句，不需要commit操作,Tweisted会自动进行
        insert_sql = """
        insert into wangyi_content(head,url,imgUrl,tag,title,content
                 )
             VALUES(%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(insert_sql, (item["head"], item["url"], item["imgUrl"],
                                    item["tag"], item["title"], item["content"]))

    def handle_error(self, failure, item, spider):
        #异步插入异常
        if failure:
            print(failure)