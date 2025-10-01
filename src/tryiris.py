from sqlalchemy import create_engine,text
import datetime

engine = None
conn = None

def initial():
    global engine, conn
    engine = create_engine("iris://SuperUser:SYS@localhost:1972/USER",echo=True)
    if engine is None:
        engine = create_engine("iris://SuperUser:SYS@localhost:1972/USER", echo=True, future=True)
    if conn is None:
        conn = engine.connect()

#インポート時に初期化
initial()


def insert(chatrole,content,logdate):
    #sql="create table FS.MyLog (ChatRole VARCHAR(50),Content VARCHAR(10000),LogDT DATE)"
    sql="insert into FS.MyLog (ChatRole,Content,LogDate) values(:chatrole,:content,:logdate)"
    para={"chatrole":chatrole,"content":content,"logdate":logdate}
    rset = conn.execute(text(sql),para)
    #rset = conn.execute(text(sql), dict(word=word))

#input [{dict}]
def jsonToDB(input):
    today=datetime.date.today()
    formatted_dt = today.strftime('%Y-%m-%d %H:%M:%S')
    sql="insert into FS.MyLog (ChatRole,Content,LogDT) values(:chatrole,:content,:logdate)"
    for reco in input:
        para={"chatrole":reco["role"],"content":reco["content"],"logdate":formatted_dt}
        rset = conn.execute(text(sql),para)

# インポート時にだけ実行したい場合は、関数の呼び出し方を工夫する
if __name__ == "__main__":
    initial()