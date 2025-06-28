from dotenv import load_dotenv
load_dotenv()
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import sqlite3
import logging
from datetime import datetime
from functools import wraps

# Настройка логирования
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Константы
import os
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [6409536793, 5917382999]
CHANNEL = "mov1eswave"
DB_NAME = "movie_codes.db"

# Проверка подписки
async def is_subscribed(bot, user_id):
    try:
        member = await bot.get_chat_member(f"@{CHANNEL}", user_id)
        return member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except:
        return False

# Декоратор подписки
def require_subscription(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if not await is_subscribed(context.bot, user_id):
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Подписаться", url=f"https://t.me/{CHANNEL}")],
                [InlineKeyboardButton("✅ Я подписался", callback_data="check_sub")]
            ])
            if update.message:
                await update.message.reply_text("❗ Для использования этой функции подпишитесь на канал:", reply_markup=keyboard)
            elif update.callback_query:
                await update.callback_query.message.reply_text("❗ Для использования этой функции подпишитесь на канал:", reply_markup=keyboard)
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

# Инициализация базы данных
def init_db():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                description TEXT,
                added_date TEXT DEFAULT CURRENT_TIMESTAMP
            )''')
            c.execute("PRAGMA table_info(media)")
            columns = [col[1] for col in c.fetchall()]
            if "image" not in columns:
                c.execute("ALTER TABLE media ADD COLUMN image TEXT")
                logger.info("Поле image добавлено в таблицу media.")
            c.execute('''CREATE TABLE IF NOT EXISTS activations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_id INTEGER,
                user_id INTEGER,
                activation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(code_id) REFERENCES media(id)
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                join_date TEXT DEFAULT CURRENT_TIMESTAMP,
                referred_by INTEGER,
                premium_days INTEGER DEFAULT 0
            )''')
            test_data = [
                ("Дюна часть2 (2024)", "1408", "Величественные пейзажи, культовая музыка Ханса Циммера и философский сюжет — всё это делает Дюну продолжением, о котором спорят до сих пор. Кто-то считает её шедевром визуального кино, кто-то — слишком затянутой фантазией без эмоционального центра.", "images/duna2.jpg"),
                ("3 тела", "1376", "Экранизация культового китайского романа Задача трёх тел от авторов Игры престолов. Перенос истории в современный Лондон, сложные научные концепции и тайные послания из глубин космоса — сериал буквально взрывает мозг.", "images/tritela.jpg"),
                ("Дэдпул и Росомаха", "8549" ,"Уэйд Уилсон попадает в организацию «Управление временными изменениями», что вынуждает его вернуться к своему альтер-эго Дэдпулу и изменить историю с помощью Росомахи.", "images/deadpulrasomaha.jpg"),
                ("Библиотекарь", "1301", "Актёр-неудачник Алексей Вязинцев узнаёт, что при загадочных обстоятельствах был убит его отец. Алексей едет в Широнино, родной город отца, чтобы продать его квартиру, но вместо этого оказывается втянут в череду опасных событий.", "images/bibliotekar.jpg"),
                ("Она (2013)", "5623", "История любви мужчины и искусственного интеллекта сегодня звучит особенно остро. Главный герой влюбляется в голосовой ИИ, который не просто отвечает — он чувствует, развивается и... эволюционирует.", "images/ona.jpg"),
                ("Очень странные дела", "1945", "Благоприятное течение местной жизни нарушает загадочное исчезновение подростка по имени Уилл. Выяснить обстоятельства дела полны решимости родные мальчика и местный шериф, также события затрагивают лучшего друга Уилла – Майка.", "images/stranniedela.jpg"),
                ("Оппенгеймер", "9573", "История жизни американского физика-теоретика Роберта Оппенгеймера, который во времена Второй мировой войны руководил Манхэттенским проектом — секретными разработками ядерного оружия.", "images/oppengaimer.jpg"),
                ("Астрал5: Красная дверь", "7921", "Далтон вырос и отправляется в художественное училище, где, следуя указаниям преподавательницы, пытается погрузиться в собственное подсознание. Парень начинает рисовать загадочную дверь, которая как-то связана с его детскими годами, о которых он ничего не помнит.", "images/astral.jpg"),
                ("Ванильное небо", "6218", "У Дэвида было всё, так он и жил без оглядки, пока в один прекрасный момент не попал в автокатастрофу и очнулся после комы инвалидом с изуродованным лицом, которое теперь приходится скрывать.", "images/vanilnoenebo.jpg"),
                ("Гангстерленд", "3189", "Две могущественных криминальных семьи, Харриганы и Стивенсоны, ведут войну за власть, избегая прямой конфронтации. Но шаткое перемирие может нарушить исчезновение Томми, сына главы клана Стивенсонов, которого в последний раз видели в ночном клубе с Эдди Харриганом.", "images/gangsterlend.jpg"),
                ("Голяк", "7491", "Мелкий воришка Винни и его друзья живут в английской глубинке и ежедневно промышляют нелегальными делами, приносящими небольшой доход. Все меняется, когда компания переходит дорогу местному криминальному авторитету.", "images/golyak.jpg"),
                ("Лучше звоните Солу", "4761", "История об испытаниях и невзгодах, которые приходится преодолеть Солу Гудману, адвокату по уголовным делам, в тот период, когда он пытается открыть свою собственную адвокатскую контору в Альбукерке, штат Нью-Мексико.", "images/solu.jpg"),
                ("Джентльмен (2024)", "7202", "Молодой человек по имени Эдди Холстед узнаёт, что полученное им большое наследство связано с наркоимперией Бобби Гласса.", "images/gentelmen.jpg"),
                ("ПРО это самое", "9755", "Молодой врач-сексолог приезжает работать в родное село. Дерзкая комедия о борьбе с предрассудками", "images/proetosamoe.jpg"),
                ("Бесстыжие", "9538", "О взбалмошной многодетной семье Галлагеров и их соседях, которые веселятся, попадают в самые невероятные ситуации и пытаются выжить в этом мире всеми возможными средствами, но при этом как можно меньше работая.", "images/besstizhie.jpg"),
                ("Запах женщины", "8662", "Американская драма 1992 года, полнометражный фильм, рассказывающий историю ученика подготовительной школы, который устраивается на краткосрочную работу в качестве компаньона/ассистента к отставному армейскому подполковнику, слепому, подавленному и раздражительному.", "images/scent.jpg"),
                ("Пушки Акимбо", "3965", "Однажды Майлз хамит очередному незнакомцу на сайте, где транслируются жестокие игры на выживание, и вскоре, вычислив местоположение нашего диванного героя по IP, в его дом вламывается группа отморозков.", "images/guns_akimbo.jpg"),
                ("Во все тяжкие", "0357", "Школьный учитель химии Уолтер Уайт узнаёт, что болен раком лёгких. Учитывая сложное финансовое состояние дел семьи, а также перспективы, Уолтер решает заняться изготовлением метамфетамина. Для этого он привлекает своего бывшего ученика Джесси Пинкмана, когда-то исключённого из школы при активном содействии Уайта.", "images/vosetyazhkie.jpg"),
                ("Два холма", "2015", "Подруги и «приматы» объединяются, чтобы пережить зиму. Новая глава комедийного суперхита", "images/dvaholma.jpg"),
                ("Урок", "4100", "Антон был успешным музыкантом, но после аварии, в которой погибла его девушка Лиза и года в наркологической клинике он все потерял. Теперь он возвращается в родной город, где у него остался лишь старший брат Константин, который всегда был его полной противоположностью.", "images/urok.jpg"),
                ("Жизнь по вызову", "9340", "Александр Шмидт — хозяин элитного эскорт-агентства. Его называют Мэджик — он и его команда способны выполнить практически любое желание. Среди клиентов уважаемые люди: бизнесмены, политики, силовики, общественные деятели. Команда — в лице бывшего бандита по кличке Рыбак и секретаря Галины Михайловны — исполняет любые капризы клиентов.", "images/zhiznpovizovu.jpg"),
                ("Кухня", "1598", "Российский телесериал в жанре ситуационной комедии с элементами мелодрамы. Сериал посвящён работе сотрудников элитного ресторана французской кухни Claude Monet и ресторана Victor, находящегося внутри отеля «ELEON».", "images/kitchen.jpg"),
                ("Снегопад", "9471", "Рассказ о начале кокаиновой эпидемии в Лос-Анджелесе начала 1980-х, когда на улицах Америки появился дешёвый крэк из Доминиканы, и страну захлестнул неконтролируемый рост преступности.", "images/snegopad.jpg"),
                ("Легион", "3278", "Бог окончательно разуверился в человечестве и послал ангелов смерти стереть свое творение с лица земли. На защиту людей встал лишь архангел Михаил, объединив под своим командованием горстку изгоев, которые в закусочной посреди пустыни терпеливо ожидают рождения Мессии.", "images/legion.jpg"),
                ("Игра", "8217", "Николас Ван Ортон - само воплощение успеха. Он преуспевает, он невозмутим и спокоен, привык держать любую ситуацию под контролем. На день рождения Николас получает необычный подарок - билет для участия в «Игре».", "images/igra.jpg"),
                ("Молчание", "5469", "Героиня — глухая. Окружающий мир — кричащий, сумасшедший, глупый. А она — спокойна. Внутри неё целая вселенная.", "images/silence.jfif"),
                ("Темный город", "9876", "Убийцу, не помнящего своего имени и прошлого, преследует полицейский инспектор Фрэнк Бастед. Его ищет жена Эмма, за ним охотятся чужаки, а он по обрывкам воспоминаний пытается разобраться, что происходит.", "images/darkcity.jpg"),
                ("Тьма", "9365", "История четырёх семей, живущих спокойной и размеренной жизнью в маленьком немецком городке. Видимая идиллия рушится, когда бесследно исчезают двое детей и воскресают тёмные тайны прошлого.", "images/tma.jpg"),
                ("Охота", "4961", "Несколько человек имели неосторожность обсуждать в групповом чате охоту на людей. Некоторое время спустя та же компания летит на частном самолёте, когда к ним в салон вваливается ничего непонимающий грязный мужчина, и встречает свою смерть — пассажиры жестоко его убивают.", "images/ohota.jpg"),
                ("45 лет", "8495", "Пожилая женщина теряет мужа. Её жизнь меняется. Вроде бы всё медленно, просто, камерно. Но ты не можешь оторваться.", "images/year.jpg"),
                ("1917", "0175", "Без склеек. Без остановок. Камера движется, а ты не замечаешь, что прошло уже 90 минут. Потому что ты — не зритель. Ты внутри.", "images/1917.jpg"),
                ("Патч Адамс", "2865", "Познакомьтесь с Целителем Адамсом - доктором, который резко отличается от своих чопорных и важных коллег. Адамс совершил невероятное открытие в современной медицине. Оказывается, лучшим лекарством от любых болезней является смех. И доктор Адамс готов сделать все возможное, чтобы заставить своих пациентов, как, впрочем, и зрителей этой прекрасной картины, смеяться без перерыва!..", "images/patchadams.jpg")
            ]
            for title, code, desc, image in test_data:
                c.execute("INSERT OR IGNORE INTO media (title, code, description, image) VALUES (?, ?, ?, ?)",
                          (title, code, desc, image))
            conn.commit()
            logger.info("База данных инициализирована.")
    except sqlite3.Error as e:
        logger.error(f"Ошибка инициализации БД: {e}")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    referred_by = None
    if context.args:
        try:
            referred_by = int(context.args[0])
        except:
            pass
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user.id,))
        existing = c.fetchone()
        if not existing:
            c.execute('''INSERT INTO users (user_id, username, first_name, last_name, referred_by)
                         VALUES (?, ?, ?, ?, ?)''',
                      (user.id, user.username, user.first_name, user.last_name, referred_by))
            if referred_by:
                c.execute("UPDATE users SET premium_days = premium_days + 1 WHERE user_id = ?", (referred_by,))
        conn.commit()
    keyboard = [
        [InlineKeyboardButton("Как это работает?", callback_data="how_it_works")],
        [InlineKeyboardButton("Проверить подписку", callback_data="check_sub")]
    ]
    await update.message.reply_text(
        f"🎬 Привет, {user.first_name}!\n"
        "Я бот для проверки кодов фильмов и сериалов.\n\n"
        "🔹 Отправь мне код, чтобы узнать, к какому фильму или сериалу он привязан\n"
        "🔹 Коды доступны в канале:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Команда /invite
@require_subscription
async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🔗 Ваша реферальная ссылка:\nhttps://t.me/{context.bot.username}?start={user.id}"
        f"\n🔗 Приглашай друзей по ссылке и получай бонусы!\n\n"
        f"🎁 Бонусы:\n"
        f"• 1 покупка — 3 дня премиум\n"
        f"• 3 покупки — 7 дней\n"
        f"• 7 покупок — 14 дней\n"
        f"• 10 покупок — 30 дней"
    )

# Команда /bonus
@require_subscription
async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT premium_days FROM users WHERE user_id = ?", (user.id,))
        row = c.fetchone()
        premium = row[0] if row else 0
        c.execute("SELECT COUNT(*) FROM users WHERE referred_by = ?", (user.id,))
        referred_count = c.fetchone()[0]
    await update.message.reply_text(
        f"🎁 Вы пригласили: <b>{referred_count}</b> пользователей\n"
        f"💎 Премиум-дней начислено: <b>{premium}</b>",
        parse_mode="HTML"
    )

# Команда /addcode
async def add_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет прав для добавления кодов.")
        return
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("❗ Использование: /addcode <код> <название> <описание>")
        return
    code = args[0]
    title = args[1]
    description = " ".join(args[2:])
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT INTO media (code, title, description) VALUES (?, ?, ?)", (code, title, description))
            conn.commit()
            await update.message.reply_text("✅ Код успешно добавлен.")
        except sqlite3.IntegrityError:
            await update.message.reply_text("⚠️ Такой код уже существует.")

# Команда /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет доступа к статистике.")
        return
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM media")
        total_codes = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM activations")
        total_activations = c.fetchone()[0]
    await update.message.reply_text(
        f"📊 Статистика:\n"
        f"👥 Пользователей: {total_users}\n"
        f"🎬 Кодов: {total_codes}\n"
        f"✅ Активаций: {total_activations}"
    )

# Обработка кода
@require_subscription
async def handle_code_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    user_id = update.effective_user.id
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT id, title, description, image FROM media WHERE code = ?", (code,))
        row = c.fetchone()
        if row:
            code_id, title, description, image_path = row
            c.execute("INSERT INTO activations (code_id, user_id) VALUES (?, ?)", (code_id, user_id))
            conn.commit()
            caption = f"🎬 <b>{title}</b>\n\n{description}"
            if image_path:
                await update.message.reply_photo(photo=open(image_path, 'rb'), caption=caption, parse_mode="HTML")
            else:
                await update.message.reply_text(caption, parse_mode="HTML")
        else:
            await update.message.reply_text("❌ Код не найден. Попробуйте ещё раз.")

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "how_it_works":
        await query.edit_message_text(
            "📌 <b>Как пользоваться ботом:</b>\n\n"
            "1. Получи код в канале\n"
            "2. Отправь его боту\n"
            "3. Узнай фильм или сериал\n\n"
            f"Канал: @{CHANNEL}",
            parse_mode="HTML"
        )

    elif query.data == "check_sub":
        try:
            # Удаляем сообщение с кнопками (если бот может)
            await query.message.delete()
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение: {e}")

        if await is_subscribed(context.bot, query.from_user.id):
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="✅ Подписка подтверждена!"
            )
        else:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="❌ Подписка не обнаружена. Подпишитесь и нажмите кнопку ещё раз:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔗 Подписаться", url=f"https://t.me/{CHANNEL}")],
                    [InlineKeyboardButton("✅ Я подписался", callback_data="check_sub")]
                ])
            )




# Запуск
def main():
    init_db()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("invite", invite))
    app.add_handler(CommandHandler("bonus", bonus))
    app.add_handler(CommandHandler("addcode", add_code))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code_input))
    logger.info("Бот запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
