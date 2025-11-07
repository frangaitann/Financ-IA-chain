import json, os, pickle, locale, requests, pandas as pd
from datetime import datetime
from langchain.tools import tool

DEBUG = False




@tool
def debug_switcher():
    """This funcs switches DEBUG False/True. JUST CALL IT IF THE USER INPUTS THE KEYWORD 'DEBUG' WITH NO MORE TEXT."""
    global DEBUG
    DEBUG = not DEBUG
    



@tool
def date_getter():
    """Simple function used for getting today's day(number)/month(word)/year(number) and a 4th argument with the 12 months of the year as a dict with their number as value. The 4 objects are part of the returned list. THE 4th LIST ELEMENT MUST BE DISCARDED BY THE AI MODEL"""
    
    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
    
    
    months_number = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11,"diciembre": 12}
    now = datetime.now()
    day = now.day
    month = now.strftime("%B")
    year = now.year

    date_list = [day, month, year, months_number]
    return date_list




# MUST FINALIZE IT FOR EMBEDDING LIKE "2017 IPC" or "IPC BETWEEN 2020 and 2023" and for being usable for prices estimations

def IPC_getter():
    """Gets the Inflation Rate month-per-month since 2017 june to the latest month"""
    if "IPC.xls" in os.listdir():
        os.remove("IPC.xls")
        
    response = requests.get("https://www.indec.gob.ar/ftp/cuadros/economia/sh_ipc_precios_promedio.xls")
    with open("IPC.xls", "wb") as f:
        f.write(response.content)
        f.close()
    
    return pd.read_excel("data.xls", engine="xlrd")






def token_loader(token: str = "GPT"):
    with open("tokens.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                if data.get("model") == token:
                    main_token = data.get("token")
                    return main_token
            except json.JSONDecodeError:
                continue
            



async def cookies(page):
    if "cookies.pkl" in os.listdir():

        cookies = pickle.load(open("cookies.pkl", "rb"))
        await page.context.clear_cookies()
        for i in cookies:

            cookie_dict = {
                "domain": i["domain"],
                "httponly": i["httponly"],
                "name": i["name"],
                "path": i["path"],
                "samesite": i["samesite"],
                "secure": i["secure"],
                "value": i["value"]
            }

            await page.context.add_cookies([cookie_dict])

        await page.reload()






# def parser():  Adapt it to playwright too