import pymysql
from DBUtils.PooledDB import PooledDB



class MysqlPool:

    def __init__(self, host, port,user, password, db):
        self.host = host
        self.port = port  # 端口号
        self.user = user  # 用户名
        self.password = password  # 密码
        self.db = db  # 库

    def connect(self):
        try:
            self.pool = PooledDB(
                creator=pymysql,  # 使用链接数据库的模块
                maxconnections=64,  # 连接池允许的最大连接数，0和None表示不限制连接数
                mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
                maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
                maxshared=1,
                # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
                blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
                maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
                setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
                ping=0,
                # ping MySQL服务端，检查是否服务可用。
                # 如：0 = None = never,
                # 1 = default = whenever it is requested,
                # 2 = when a cursor is created,
                # 4 = when a query is executed,
                # 7 = always
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.db,
                charset='utf8'
            )
        except Exception as e:
            msg = 'mysql连接失败：{}'.format(e)
            print(msg)
            return msg

    def execute_select_need_fetch(self, sql, fetch_type=2, many=10):
        return self.execute(sql, fetch_type=fetch_type, many=many, commmit=False)

    def execute_commit_not_fetch(self, sql):
        return self.execute(sql, fetch_type=0)

    def execute(self, sql, fetch_type=2, many=10, commmit=True):
        """
        :param sql:
        :param commmit: insert，update，delete 等类型需要提交commit操作
        :param fetch_type: fetchone, fetchall, fetchmany
        :param many: fetchmany需要指定数量
        :return:
        """

        conn = self.pool.connection()   # 从连接池创建连接
        cur = conn.cursor(pymysql.cursors.DictCursor)
        # cur = conn.cursor()

        row = None
        err_msg = None
        datas = None

        try:
            row = cur.execute(sql)  # ret是执行受影响的行的数量
            if commmit:
                conn.commit()
            if fetch_type == 0:       # 不需要取数据
                pass
            elif fetch_type == 1:
                datas = cur.fetchone()  # 获取查询到的所有数据
            elif fetch_type == 2:
                datas = cur.fetchall()  # 获取查询到的所有数据
            elif fetch_type == 3:
                datas = cur.fetchmany(many)  # 获取查询到的10条数据
            # conn.insert_id()  # 插入成功后返回的id

        except pymysql.Error as e:
            conn.rollback()
            err_msg = "发生错误：{}；sql：{}".format(e, sql)

        finally:
            cur.close()
            conn.close()

        return row, err_msg, datas

    def close(self):
        self.pool.close()

if __name__ == '__main__':

    """
        CREATE TABLE IF NOT EXISTS `hotelgg_tel`(
       `id` INT UNSIGNED AUTO_INCREMENT,
       `hotel_id` INT(15) UNSIGNED NOT NULL,
       `decode` VARCHAR(100) NOT NULL,
       `tel` VARCHAR(20) default '0',
       PRIMARY KEY ( `id` )
    )ENGINE=InnoDB DEFAULT CHARSET=utf8;
    """

    "alter table hotelgg_tel change hotelid hotel_id VARCHAR DEFAULT 0"
    "alter table hotelgg_tel add tel int(15) default '0';"
    "DELETE FROM hotelgg_tel WHERE tel =0;"
    "UPDATE hotelgg_tel SET tel={} WHERE hotel_id={};"
    "INSERT INTO {} (hotel_id,decode) VALUES ({},'{}')"
    "SELECT max(id) FROM table"  # 查询最后一条数据的id值
    "truncate label_history_6v8_2;" # 清空表

    # host='127.0.0.1'
    # port=3306
    # user='root'
    # password="mysql"
    # db="hotel"

    # host = '192.168.100.22'
    # port = 3306
    # user = 'root'
    # password = "ChinaDASS@2020"
    # db = "chinadaas"

    # msyql = MysqlPool(host='127.0.0.1', port=3306, user='root', password="mysql", db="hotel")
    mysql = MysqlPool()
    flag = mysql.connect()
    if flag:
        print(flag)
    row, err_msg, datas = mysql.execute_select_need_fetch("select * from jsyh_label where id=3", fetch_type=1)
    print(row)
    print(err_msg)
    print(datas)
    mysql.close()


