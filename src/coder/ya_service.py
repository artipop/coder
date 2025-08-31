import yadisk

async def download_file():
    client = yadisk.AsyncClient(token="<token>")
    # или
    # client = yadisk.AsyncClient("<application-id>", "<application-secret>", "<token>")
    async with client:
        # Проверяет, валиден ли токен
        print(await client.check_token())

        # Получает общую информацию о диске
        print(await client.get_disk_info())

        print([i async for i in client.get_files()])
        # Выводит содержимое "/some/path"
        # print([i async for i in client.listdir("/some/path")])
