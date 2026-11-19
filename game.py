import hashlib
import hmac
import json
import os
import random
import sqlite3
import time
import uuid
from urllib.parse import parse_qsl
from aiohttp import web

BOT_TOKEN = os.environ["BOT_TOKEN"]
DB_PATH = os.environ.get("DATABASE_PATH", "brainsir.db")

# Формат: вопрос, четыре варианта, индекс правильного ответа, тема.
QUESTIONS = [
("Какая планета самая большая в Солнечной системе?", ["Земля","Юпитер","Сатурн","Нептун"], 1,"Космос"),
("Сколько сторон у шестиугольника?", ["5","6","7","8"], 1,"Наука"),
("Столица Австралии?", ["Сидней","Мельбурн","Канберра","Перт"], 2,"География"),
("Кто написал роман «Война и мир»?", ["Фёдор Достоевский","Лев Толстой","Антон Чехов","Иван Тургенев"], 1,"Культура"),
("Какой химический символ у золота?", ["Ag","Fe","Au","Go"], 2,"Наука"),
("Сколько минут в двух часах?", ["100","110","120","130"], 2,"Математика"),
("Какая река протекает через Египет?", ["Амазонка","Нил","Дунай","Ганг"], 1,"География"),
("Какая звезда ближе всего к Земле?", ["Сириус","Вега","Солнце","Полярная"], 2,"Космос"),
("В каком году человек впервые ступил на Луну?", ["1959","1969","1979","1989"], 1,"История"),
("Какой океан самый большой?", ["Атлантический","Индийский","Северный Ледовитый","Тихий"], 3,"География"),
("Сколько будет 9 × 8?", ["70","72","81","64"], 1,"Математика"),
("Какой газ растения поглощают при фотосинтезе?", ["Кислород","Азот","Углекислый газ","Водород"], 2,"Наука"),
("Кто создал картину «Мона Лиза»?", ["Ван Гог","Пикассо","Леонардо да Винчи","Клод Моне"], 2,"Культура"),
("В какой стране появилась пицца?", ["Франция","Италия","Греция","Испания"], 1,"Культура"),
("Сколько игроков одной футбольной команды на поле?", ["9","10","11","12"], 2,"Спорт"),
("Какой орган перекачивает кровь?", ["Лёгкие","Печень","Сердце","Почки"], 2,"Наука"),
("Какая гора самая высокая над уровнем моря?", ["К2","Эверест","Килиманджаро","Эльбрус"], 1,"География"),
("Какой язык программирования назван в честь комедийного шоу?", ["Java","Python","Ruby","Pascal"], 1,"Технологии"),
("Сколько хромосом обычно у человека?", ["23","44","46","48"], 2,"Наука"),
("Какой металл жидкий при комнатной температуре?", ["Железо","Ртуть","Медь","Алюминий"], 1,"Наука"),
("Кто был первым космонавтом?", ["Юрий Гагарин","Нил Армстронг","Алексей Леонов","Герман Титов"], 0,"История"),
("Столица Японии?", ["Киото","Осака","Токио","Нагоя"], 2,"География"),
("Сколько градусов в прямом угле?", ["45","90","180","360"], 1,"Математика"),
("Самое быстрое наземное животное?", ["Лев","Гепард","Антилопа","Страус"], 1,"Природа"),
("Самый холодный материк?", ["Европа","Азия","Антарктида","Северная Америка"], 2,"География"),
("Как называется превращение воды в пар?", ["Конденсация","Замерзание","Испарение","Плавление"], 2,"Наука"),
("Кто написал «Маленького принца»?", ["Жюль Верн","Антуан де Сент-Экзюпери","Виктор Гюго","Альбер Камю"], 1,"Культура"),
("Какой материк пересекают экватор и нулевой меридиан?", ["Африка","Австралия","Южная Америка","Европа"], 0,"География"),
("Сколько костей примерно у взрослого человека?", ["106","206","306","406"], 1,"Наука"),
("Кто написал «Звёздную ночь»?", ["Рембрандт","Ван Гог","Моне","Дали"], 1,"Культура"),
("Наименьшая частица химического элемента?", ["Молекула","Атом","Клетка","Кристалл"], 1,"Наука"),
("Мадагаскар — это…", ["Регион Кении","Часть Танзании","Отдельное государство","Часть Мозамбика"], 2,"География"),
("Сколько колец в олимпийском символе?", ["4","5","6","7"], 1,"Спорт"),
("Какой прибор измеряет атмосферное давление?", ["Термометр","Барометр","Гигрометр","Анемометр"], 1,"Наука"),
("Столица Канады?", ["Торонто","Ванкувер","Оттава","Монреаль"], 2,"География"),
("Какое число простое?", ["21","27","29","33"], 2,"Математика"),
("Какой витамин вырабатывается под действием солнечного света?", ["A","B12","C","D"], 3,"Наука"),
("Кто открыл пенициллин?", ["Мария Кюри","Александр Флеминг","Луи Пастер","Исаак Ньютон"], 1,"История"),
("Самая длинная кость человека?", ["Большеберцовая","Плечевая","Бедренная","Лучевая"], 2,"Наука"),
("Какой город называют Вечным городом?", ["Афины","Рим","Стамбул","Иерусалим"], 1,"География"),
("Сколько планет в Солнечной системе?", ["7","8","9","10"], 1,"Космос"),
("Кто создал Шерлока Холмса?", ["Агата Кристи","Артур Конан Дойл","Эдгар По","Чарльз Диккенс"], 1,"Культура"),
("Переход вещества из твёрдого состояния в жидкое?", ["Плавление","Кипение","Сублимация","Конденсация"], 0,"Наука"),
("В какой стране находится Самарканд?", ["Казахстан","Таджикистан","Узбекистан","Кыргызстан"], 2,"География"),
("Какой океан омывает восточное побережье США?", ["Тихий","Индийский","Атлантический","Южный"], 2,"География"),
("Сколько будет 15 в квадрате?", ["125","200","225","250"], 2,"Математика"),
("Какое яйцекладущее млекопитающее существует?", ["Кенгуру","Утконос","Дельфин","Коала"], 1,"Природа"),
("Столица Турции?", ["Стамбул","Анкара","Измир","Бурса"], 1,"География"),
("Какой газ преобладает в атмосфере Земли?", ["Кислород","Углекислый газ","Азот","Аргон"], 2,"Наука"),
("Сколько дней в високосном году?", ["365","366","367","364"], 1,"Математика"),
]

def connect():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

async def init_db():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS players(
            user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,
            best_score INTEGER NOT NULL DEFAULT 0, games INTEGER NOT NULL DEFAULT 0)""")
        c.execute("""CREATE TABLE IF NOT EXISTS sessions(
            session_id TEXT PRIMARY KEY, user_id INTEGER NOT NULL, questions_json TEXT NOT NULL,
            position INTEGER NOT NULL, score INTEGER NOT NULL, status TEXT NOT NULL,
            question_started REAL NOT NULL, created_at REAL NOT NULL)""")
        c.commit()

def telegram_user(request):
    raw = request.headers.get("X-Telegram-Init-Data", "")
    if not raw:
        return None
    try:
        data = dict(parse_qsl(raw, keep_blank_values=True))
        received_hash = data.pop("hash")
        check = "\n".join(f"{k}={v}" for k,v in sorted(data.items()))
        secret = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(calculated, received_hash):
            return None
        if time.time() - int(data.get("auth_date", "0")) > 86400:
            return None
        return json.loads(data["user"])
    except Exception:
        return None

def require_user(request):
    user = telegram_user(request)
    if not user:
        raise web.HTTPUnauthorized(text="Открой игру через Telegram")
    return user

def view(q, pos, score):
    return {"position":pos+1,"total":50,"score":score,"topic":q["topic"],
            "question":q["question"],"options":q["options"],"seconds":15}

async def api_start(request):
    user = require_user(request)
    ids = list(range(len(QUESTIONS)))
    random.shuffle(ids)
    chosen = []
    for i in ids[:50]:
        question, opts, correct, topic = QUESTIONS[i]
        order = list(range(4))
        random.shuffle(order)
        chosen.append({"question":question,"options":[opts[x] for x in order],
                       "correct":order.index(correct),"topic":topic})
    sid, now = uuid.uuid4().hex, time.time()
    with connect() as c:
        c.execute("""INSERT INTO players(user_id,username,first_name) VALUES(?,?,?)
        ON CONFLICT(user_id) DO UPDATE SET username=excluded.username,first_name=excluded.first_name""",
        (int(user["id"]),user.get("username",""),user.get("first_name","Игрок")))
        c.execute("INSERT INTO sessions VALUES(?,?,?,?,?,?,?,?)",
                  (sid,int(user["id"]),json.dumps(chosen,ensure_ascii=False),0,0,"playing",now,now))
        c.commit()
    return web.json_response({"session_id":sid,"question":view(chosen[0],0,0)})

async def api_answer(request):
    user = require_user(request)
    try:
        body = await request.json()
        sid, answer = str(body["session_id"]), int(body["answer"])
    except Exception:
        raise web.HTTPBadRequest(text="Некорректный запрос")
    uid = int(user["id"])
    with connect() as c:
        row = c.execute("SELECT * FROM sessions WHERE session_id=? AND user_id=?",(sid,uid)).fetchone()
        if not row or row["status"] != "playing":
            raise web.HTTPBadRequest(text="Игра уже завершена или не найдена")
        questions = json.loads(row["questions_json"])
        pos, score = row["position"], row["score"]
        if time.time() - row["question_started"] > 15.5:
            status = "timeout"
        elif answer == questions[pos]["correct"]:
            score += 1
            status = "won" if pos == 49 else "playing"
        else:
            status = "wrong"
        if status == "playing":
            pos += 1
            c.execute("UPDATE sessions SET position=?,score=?,question_started=? WHERE session_id=?",
                      (pos,score,time.time(),sid))
            c.commit()
            return web.json_response({"status":"playing","question":view(questions[pos],pos,score)})
        c.execute("UPDATE sessions SET score=?,status=? WHERE session_id=?",(score,status,sid))
        c.execute("UPDATE players SET games=games+1,best_score=MAX(best_score,?) WHERE user_id=?",(score,uid))
        best=c.execute("SELECT best_score FROM players WHERE user_id=?",(uid,)).fetchone()["best_score"]
        c.commit()
        return web.json_response({"status":status,"score":score,"total":50,"best_score":best})

async def api_me(request):
    user = require_user(request)
    with connect() as c:
        row=c.execute("SELECT best_score,games FROM players WHERE user_id=?",(int(user["id"]),)).fetchone()
    return web.json_response({"best_score":row["best_score"] if row else 0,
                              "games":row["games"] if row else 0})

async def api_leaderboard(request):
    require_user(request)
    with connect() as c:
        rows=c.execute("SELECT username,first_name,best_score FROM players WHERE games>0 "
                       "ORDER BY best_score DESC, games ASC LIMIT 5").fetchall()
    return web.json_response({"leaders":[{"rank":i+1,
        "name":("@"+r["username"]) if r["username"] else (r["first_name"] or "Игрок"),
        "score":r["best_score"]} for i,r in enumerate(rows)]})
