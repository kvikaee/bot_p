import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json

# ========== НАСТРОЙКИ ==========
TOKEN = "vk1.a.xFslFAk5bRTY9worDG7Wq9tNeVLOCopyZanzcZXYmx_bISmANyKf7gDZSg1ec-lbKW2h9c2Acgf54Dsih-s48CidPcSgXKoKLn4crhxW0IE49xG3S1jO1t5goetzdiR9cjsrAg55z50_S1DHBP4HVGjU6hRTJHpA04B0qOOucT7Mvn_qnhlGIvlFxyhQ14zOWVXBQmmhBx0R23RXPZkkJg"
GROUP_ID = 238640930  # Укажите ID вашего сообщества (числом) – необязательно

# Хранилище состояний пользователей (user_id -> данные)
user_states = {}

# ========== ФУНКЦИИ ДЛЯ ОТПРАВКИ СООБЩЕНИЙ И КЛАВИАТУР ==========
def send_message(vk, user_id, text, keyboard=None, attachment=None):
    """Отправляет сообщение пользователю с возможностью прикрепить клавиатуру и вложение."""
    params = {
        "user_id": user_id,
        "message": text,
        "random_id": 0
    }
    if keyboard:
        params["keyboard"] = keyboard.get_keyboard()
    if attachment:
        params["attachment"] = attachment
    vk.messages.send(**params)

def create_main_keyboard():
    """Клавиатура главного меню (приветствие)"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Да, начнём", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("Расскажи коротко о проекте", color=VkKeyboardColor.PRIMARY)
    return keyboard

def create_problem_keyboard():
    keyboard = VkKeyboard(one_time=False)
    problems = [
        "Помощь людям с инвалидностью",
        "Помощь бездомным",
        "Детям-сиротам",
        "Трудные подростки",
        "Пожилые люди",
        "Экология",
        "Животные",
        "Паллиативная помощь / профилактика"   # ← сокращено
    ]
    for i, problem in enumerate(problems):
        keyboard.add_button(problem, color=VkKeyboardColor.SECONDARY)
        if i != len(problems) - 1:
            keyboard.add_line()
    return keyboard

def create_help_format_keyboard():
    """Клавиатура выбора формата помощи для выбранной проблемы"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Разовое дело (помочь один раз)", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Регулярное волонтёрство", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Pro bono (применить свои навыки)", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("Игра", color=VkKeyboardColor.NEGATIVE)
    return keyboard

def create_pro_bono_keyboard():
    """Клавиатура после информации о pro bono"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Да, покажи", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("Игра", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button("Выбрать другую проблему", color=VkKeyboardColor.PRIMARY)
    return keyboard

def create_game_result_keyboard():
    """Клавиатура после ответа в игре"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Показать список проверенных НКО", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("Другая социальная проблема", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("В начало", color=VkKeyboardColor.NEGATIVE)
    return keyboard

def create_resources_keyboard():
    """Клавиатура для ресурсного раздела"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Сохранить сообщение", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button("Поделиться с другом", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("В главное меню", color=VkKeyboardColor.NEGATIVE)
    return keyboard

def create_final_keyboard():
    """Клавиатура завершающего сообщения"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Выбрать другую проблему", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Показать ресурсы ещё раз", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button("Всё, спасибо, выхожу", color=VkKeyboardColor.NEGATIVE)
    return keyboard

# ========== ОБРАБОТЧИКИ ДИАЛОГА ПО СОСТОЯНИЯМ ==========
def handle_start(vk, user_id):
    """Обработка команды /start или первого входа"""
    text = ("Привет! Я чат-бот проекта «Конструктор доброты».\n"
            "Помогаю студентам разобраться, как помогать людям, животным, экологии — безопасно и без фейковых сборов.\n"
            "Хочешь попробовать игровой сценарий?")
    keyboard = create_main_keyboard()
    send_message(vk, user_id, text, keyboard)
    user_states[user_id] = {"state": "main_menu"}

def handle_project_info(vk, user_id):
    """Отправка краткой информации о проекте"""
    text = ("«Конструктор доброты» — проект, который учит студентов безопасно и осознанно помогать другим. "
            "Мы рассказываем о социальных проблемах, форматах помощи (разово, регулярно, pro bono) и учим распознавать мошеннические сборы.\n\n"
            "А теперь давай начнём игру!")
    keyboard = create_main_keyboard()  # возвращаем к выбору "Да, начнём"
    send_message(vk, user_id, text, keyboard)
    user_states[user_id]["state"] = "main_menu"

def handle_problem_choice(vk, user_id, problem):
    """После выбора проблемы – показываем форматы помощи"""
    text = (f"Вы выбрали: **{problem}**\n\n"
            "В городе много одиноких пожилых (пример для темы). Им нужна не только еда, но и помощь с документами, ремонтом техники, общение.\n\n"
            "Что для тебя ближе?")
    keyboard = create_help_format_keyboard()
    send_message(vk, user_id, text, keyboard)
    user_states[user_id] = {
        "state": "chosen_problem",
        "problem": problem
    }

def handle_format_choice(vk, user_id, choice, problem):
    """Обработка выбора формата помощи (разовое, регулярное, pro bono, игра)"""
    if choice == "Разовое дело (помочь один раз)":
        text = ("Отличный выбор! Разовые дела помогают быстро и без долгой привязки. "
                "Примеры: почистить снег у дома пожилого соседа, сходить за продуктами, покормить бездомных животных.\n\n"
                "Хочешь попробовать другой формат или выбрать новую тему?\n"
                "→ [Выбрать другую проблему] или [Pro bono / Игра]")
        keyboard = create_help_format_keyboard()
        send_message(vk, user_id, text, keyboard)
        # остаёмся в том же состоянии, но можно и сбросить
        user_states[user_id]["state"] = "chosen_problem"
    elif choice == "Регулярное волонтёрство":
        text = ("Регулярное волонтёрство даёт глубокую связь с делом. "
                "Можно стать помощником в приюте, репетитором для детей или сопровождающим на мероприятиях.\n\n"
                "Что дальше?")
        keyboard = create_help_format_keyboard()
        send_message(vk, user_id, text, keyboard)
    elif choice == "Pro bono (применить свои навыки)":
        text = ("Pro bono — помогать бесплатно, но профессионально.\n"
                "Пример: студент-дизайнер делает буклет для НКО, IT-студент настраивает сайт, психолог консультирует по телефону.\n\n"
                "Что ты получаешь:\n"
                "• Реальный кейс в портфолио\n"
                "• Опыт работы\n"
                "• Рекомендательное письмо\n\n"
                "Хочешь посмотреть конкретные pro bono-задачи по этой теме?")
        keyboard = create_pro_bono_keyboard()
        send_message(vk, user_id, text, keyboard)
        user_states[user_id]["state"] = "pro_bono_menu"
    elif choice == "Игра":
        start_game(vk, user_id, problem)
    else:
        # fallback
        send_message(vk, user_id, "Пожалуйста, выбери один из вариантов с помощью кнопок.")

def handle_pro_bono(vk, user_id, action):
    """Обработка ветки pro bono: показать задачи, игра, другая проблема"""
    if action == "Да, покажи":
        text = ("Примеры pro bono-задач по теме «Пожилые люди»:\n"
                "• IT-специалисту: помочь подключить пенсионера к госуслугам\n"
                "• Юристу: проконсультировать по льготам\n"
                "• Дизайнеру: оформить открытки для поздравлений\n"
                "• Психологу: провести телефонную линию доверия\n\n"
                "Платформы для поиска: ProCharity, Добро.ру, волонтёрские центры вузов.")
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button("Игра", color=VkKeyboardColor.SECONDARY)
        keyboard.add_button("Выбрать другую проблему", color=VkKeyboardColor.PRIMARY)
        send_message(vk, user_id, text, keyboard)
        user_states[user_id]["state"] = "after_pro_bono"
    elif action == "Игра":
        problem = user_states[user_id].get("problem", "Пожилые люди")
        start_game(vk, user_id, problem)
    elif action == "Выбрать другую проблему":
        text = "Выбери новую тему:"
        keyboard = create_problem_keyboard()
        send_message(vk, user_id, text, keyboard)
        user_states[user_id] = {"state": "selecting_problem"}

def start_game(vk, user_id, problem):
    """Запуск мини-игры про проверку сборов"""
    text = ("Тест: настоящий сбор или мошенники?\n\n"
            "«Срочно! Больному ребёнку нужны лекарства. Карта Сбер 1234 ... Елена. Переведите любую сумму, фото чека пришлите сюда».\n\n"
            "Что ты думаешь?")
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Это настоящий сбор", color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button("Скорее всего, мошенники", color=VkKeyboardColor.POSITIVE)
    send_message(vk, user_id, text, keyboard)
    user_states[user_id]["state"] = "game_waiting"

def handle_game_answer(vk, user_id, answer, problem):
    """Обработка ответа в игре"""
    if answer == "Скорее всего, мошенники":
        text = ("✅ Верно. Признаки фейка: личная карта, нет названия фонда, нет отчётов.\n"
                "Проверяй НКО через реестр Минюста и официальный сайт.")
    else:
        text = ("❌ Опасная ошибка. Такие сборы почти всегда мошеннические.\n"
                "Вот алгоритм проверки:\n"
                "1. Убедись, что сбор ведёт официальный фонд (проверь по реестру Минюста).\n"
                "2. На сайте фонда должны быть отчёты и реквизиты юрлица.\n"
                "3. Никогда не переводите на личные карты.\n"
                "4. При сомнениях — поищите название фонда + слова «отзывы» или «мошенники».")
    send_message(vk, user_id, text)
    # После ответа показываем клавиатуру с дальнейшими действиями
    keyboard = create_game_result_keyboard()
    send_message(vk, user_id, "Что хочешь сделать дальше?", keyboard)
    user_states[user_id]["state"] = "after_game"

def handle_after_game(vk, user_id, action):
    """Действия после игры"""
    if action == "Показать список проверенных НКО":
        text = ("Проверенные НКО (примеры):\n"
                "• Фонд «Старость в радость» – помощь пожилым\n"
                "• «Ночлежка» – помощь бездомным\n"
                "• «Русфонд» – лечение детей\n"
                "Всегда сверяйте с реестром Минюста.")
        send_message(vk, user_id, text)
        # остаемся в after_game, предлагаем другие кнопки
        keyboard = create_game_result_keyboard()
        send_message(vk, user_id, "Что ещё?", keyboard)
    elif action == "Другая социальная проблема":
        text = "Выбери другую тему:"
        keyboard = create_problem_keyboard()
        send_message(vk, user_id, text, keyboard)
        user_states[user_id] = {"state": "selecting_problem"}
    elif action == "В начало":
        handle_start(vk, user_id)

def show_resources(vk, user_id):
    """Показывает ресурсный раздел"""
    text = ("Полезные ресурсы:\n"
            "— Реестр НКО Минюста: https://minjust.gov.ru/ru/activity/nko/reestr-nko/\n"
            "— Платформы pro bono: ProCharity (procharity.ru), Добро.ру\n"
            "— Контакты организаторов проекта: почта: dobroy@example.com, ВК: vk.com/dobro\n\n"
            "Хочешь сохранить эти данные?")
    keyboard = create_resources_keyboard()
    send_message(vk, user_id, text, keyboard)
    user_states[user_id]["state"] = "resources_menu"

def handle_resources_action(vk, user_id, action):
    """Обработка действий в ресурсном разделе"""
    if action == "Сохранить сообщение":
        send_message(vk, user_id, "Ты можешь скопировать это сообщение или нажать «Поделиться», чтобы отправить себе в личные сообщения.")
        # можно просто отправить сообщение с ресурсами повторно
        show_resources(vk, user_id)  # повторно показываем то же меню
    elif action == "Поделиться с другом":
        send_message(vk, user_id, "Поделись этим сообщением с другом: скопируй ссылки и отправь ему.")
        # можно отправить текст ссылок ещё раз
        text = ("Поделитесь полезными ресурсами:\n"
                "Реестр НКО Минюста: https://minjust.gov.ru/ru/activity/nko/reestr-nko/\n"
                "ProCharity: procharity.ru\n"
                "Добро.ру\n"
                "Контакты проекта: vk.com/dobro")
        send_message(vk, user_id, text)
        show_resources(vk, user_id)  # возвращаем в меню ресурсов
    elif action == "В главное меню":
        handle_start(vk, user_id)

def handle_final_menu(vk, user_id, action):
    """Обработка завершающего сообщения"""
    if action == "Выбрать другую проблему":
        text = "Выбери новую тему:"
        keyboard = create_problem_keyboard()
        send_message(vk, user_id, text, keyboard)
        user_states[user_id] = {"state": "selecting_problem"}
    elif action == "Показать ресурсы ещё раз":
        show_resources(vk, user_id)
    elif action == "Всё, спасибо, выхожу":
        send_message(vk, user_id, "Рады были помочь! Если захочешь вернуться — напиши «Старт» или просто любое сообщение. Добрых дел!")
        user_states[user_id] = {"state": "exited"}
        # можно также удалить состояние, но оставим, чтобы при следующем сообщении начать сначала

def handle_global_commands(vk, user_id, text):
    """Обработка команд типа /start, /resources, /menu, а также кнопки «В начало»"""
    if text.lower() in ["/start", "старт", "начать", "привет"]:
        handle_start(vk, user_id)
        return True
    elif text.lower() in ["/resources", "ресурсы", "полезные ссылки"]:
        show_resources(vk, user_id)
        return True
    elif text.lower() in ["/menu", "меню", "главное меню"]:
        handle_start(vk, user_id)
        return True
    return False

# ========== ОСНОВНОЙ ЦИКЛ ==========
def main():
    vk_session = vk_api.VkApi(token=TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    print("Бот запущен и слушает сообщения...")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            message_text = event.text.strip()

            # Игнорируем пустые сообщения или только стикеры
            if not message_text:
                continue

            # Обработка глобальных команд (в любом состоянии)
            if handle_global_commands(vk, user_id, message_text):
                continue

            # Получаем состояние пользователя (если нет – начинаем заново)
            if user_id not in user_states:
                handle_start(vk, user_id)
                continue

            state_data = user_states[user_id]
            current_state = state_data.get("state")

            # Машина состояний
            if current_state == "main_menu":
                if message_text == "Да, начнём":
                    text = "Выбери тему, которая тебе интересна:"
                    keyboard = create_problem_keyboard()
                    send_message(vk, user_id, text, keyboard)
                    user_states[user_id] = {"state": "selecting_problem"}
                elif message_text == "Расскажи коротко о проекте":
                    handle_project_info(vk, user_id)
                else:
                    send_message(vk, user_id, "Пожалуйста, нажми на одну из кнопок.", create_main_keyboard())

            elif current_state == "selecting_problem":
                # Список всех возможных проблем (можем проверить вхождение, но проще принять любой текст)
                if message_text in [
                    "Помощь людям с инвалидностью", "Помощь бездомным", "Детям-сиротам",
                    "Трудные подростки", "Пожилые люди", "Экология", "Животные",
                    "Паллиативная помощь / профилактика заболеваний"
                ]:
                    handle_problem_choice(vk, user_id, message_text)
                else:
                    send_message(vk, user_id, "Пожалуйста, выбери тему из списка с помощью кнопок.", create_problem_keyboard())

            elif current_state == "chosen_problem":
                problem = state_data.get("problem", "")
                if message_text in ["Разовое дело (помочь один раз)", "Регулярное волонтёрство",
                                     "Pro bono (применить свои навыки)", "Игра"]:
                    handle_format_choice(vk, user_id, message_text, problem)
                else:
                    send_message(vk, user_id, "Используй кнопки для выбора формата помощи.", create_help_format_keyboard())

            elif current_state == "pro_bono_menu":
                if message_text in ["Да, покажи", "Игра", "Выбрать другую проблему"]:
                    handle_pro_bono(vk, user_id, message_text)
                else:
                    send_message(vk, user_id, "Нажми одну из кнопок.", create_pro_bono_keyboard())

            elif current_state == "after_pro_bono":
                if message_text == "Игра":
                    problem = state_data.get("problem", "Пожилые люди")
                    start_game(vk, user_id, problem)
                elif message_text == "Выбрать другую проблему":
                    text = "Выбери новую тему:"
                    keyboard = create_problem_keyboard()
                    send_message(vk, user_id, text, keyboard)
                    user_states[user_id] = {"state": "selecting_problem"}
                else:
                    send_message(vk, user_id, "Выбери: Игра или Другая проблема.", create_pro_bono_keyboard())

            elif current_state == "game_waiting":
                if message_text in ["Это настоящий сбор", "Скорее всего, мошенники"]:
                    problem = state_data.get("problem", "Пожилые люди")
                    handle_game_answer(vk, user_id, message_text, problem)
                else:
                    send_message(vk, user_id, "Пожалуйста, выбери один из вариантов.")

            elif current_state == "after_game":
                if message_text in ["Показать список проверенных НКО", "Другая социальная проблема", "В начало"]:
                    handle_after_game(vk, user_id, message_text)
                else:
                    send_message(vk, user_id, "Используй кнопки меню.", create_game_result_keyboard())

            elif current_state == "resources_menu":
                if message_text in ["Сохранить сообщение", "Поделиться с другом", "В главное меню"]:
                    handle_resources_action(vk, user_id, message_text)
                else:
                    send_message(vk, user_id, "Нажми на одну из кнопок.", create_resources_keyboard())

            elif current_state == "final_menu":
                if message_text in ["Выбрать другую проблему", "Показать ресурсы ещё раз", "Всё, спасибо, выхожу"]:
                    handle_final_menu(vk, user_id, message_text)
                else:
                    send_message(vk, user_id, "Пожалуйста, выбери действие.", create_final_keyboard())

            elif current_state == "exited":
                # Если пользователь вышел, при новом сообщении можно начать сначала
                handle_start(vk, user_id)
            else:
                # Неизвестное состояние – перезапуск
                handle_start(vk, user_id)

if __name__ == "__main__":
    main()