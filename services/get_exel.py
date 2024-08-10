import pandas as pd
from database.requests import get_all_users


async def list_users_to_exel():
    dict_stat = {"№ п/п": [], "ID_telegram": [], "username": []}
    i = 0
    list_user = await get_all_users()
    for user in list_user:
        i += 1
        dict_stat["№ п/п"].append(i)
        dict_stat["ID_telegram"].append(user.tg_id)
        dict_stat["username"].append(user.username)
    df_stat = pd.DataFrame(dict_stat)
    with pd.ExcelWriter(path='./list_user.xlsx', engine='xlsxwriter') as writer:
        df_stat.to_excel(writer, sheet_name=f'Список пользователей', index=False)

