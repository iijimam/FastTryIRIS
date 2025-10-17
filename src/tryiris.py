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

def search(input):
    sql=(
     "select TOP 5 VECTOR_DOT_PRODUCT(TextVec,TO_VECTOR(FS.GetTextVec(:text),FLOAT,1536)) as sim ,FileName,Title,Text"
     " FROM FS.Document ORDER BY sim DESC"
    )
    print(sql)
    rset = conn.execute(text(sql), {'text': input}).fetchall()
    docref=[]
    for reco in rset:
        #print(reco)
        docref.append(
            {"FileName":reco[1],"Title":reco[2],"Doc":reco[3]}
        )
    return docref

# インポート時にだけ実行したい場合は、関数の呼び出し方を工夫する
if __name__ == "__main__":
    initial()