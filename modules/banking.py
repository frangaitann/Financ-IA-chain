if __name__ == '__main__':
    from misc import cookies, date_getter
    from embedding import embedded_transact
else:
    from modules.misc import cookies, date_getter
    from modules.embedding import embedded_transact

from pydoc import html
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from langchain.tools import tool
import os, csv, asyncio, pandas as pd



# NOW IT CHECKS, BUT IT UPDATES THE WHOLE MercadoPago TRANSACTIONS, it needs to check if the transaction is repeated on each iteration (page) so when it finds a repeated transaction it automatically stops without reaching the ending page


bal_sav = False
async def date_getter_func():
    return date_getter.func()





#LangSmith studio functions (No Subprocess | Have to use playwright in a server in the future)
@tool
async def bank_bal_studio():
    """Reads 'bal_st.txt' file which has the current balance and savings in the following format= BALANCE: {balance_value} | SAVINGS: {savings_value} and returns them"""
    with open("bal_st.txt", "r", encoding="utf-8") as f:
        return f.read()
        

@tool
async def transactions_reader_studio(user_inp):
    """Reads 'trans.csv' file which has a table of user's transactions with and embedding function which chooses the relevant lines for the user inputs. It works for specific transactions in a specific time and/or quantity. date_getter FUNC must be called first for time coherency. The argument must be the user input raw text with today's date"""
    return embedded_transact(user_inp)






# Local running functions (Subprocess Allowed | Can use playwright locally due to no subprocess blocking)
#@tool
async def balance_savings_reader():
    """Function used for reading the balance & savings from the user's bank/e-wallet/e-bank account"""
    
    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(
            headless=True,  # MODIFY WITH DEBUG MODE
            args=[
                '--log-level=3',
                '--disable-gpu',
                '--disable_notifications',
                '--disable-search-engine-choice-screen',
                '--disable-blink-features=AutomationControlled'
            ],
        )
        
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/134.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/Argentina/Buenos_Aires",
                    
        )
        
        
        if "cookies.pkl" in os.listdir():
            await cookies(page)
            await page.goto("https://www.mercadopago.com.ar/home")
        else:
            print("No cookies") # I left how to get the cookies with .pkl file in the github repository     <--------
            return
        
        
        #Takes Bal
        bal = page.locator(".andes-money-amount__fraction").first
        await bal.wait_for()
        bal = await bal.text_content()
        bal = bal.replace(".", "")

        #Changes Tab
        tab_button = page.locator(".andes-tab__link").nth(1)
        await tab_button.click()
        
        
        # Acc Savings
        sav = page.locator(".andes-money-amount__fraction").first
        await sav.wait_for()
        sav = await sav.text_content()
        sav = sav.replace(".", "")

        bal_and_sav = [float(bal), float(sav)]
        
        with open("bal_st.txt", "w", encoding="utf-8") as f:
            f.write(f"BALANCE: {float(bal)} | SAVINGS: {float(sav)}")
            f.close()

        return bal_and_sav






#@tool
async def transactions_reader(user_inp: str):
    """Reads the user's bank transactions history previously checking if it needs to be updated or not, if it needs it will do it automatically. The Argument is the user's input (Currency is AR$)"""
    
    try:
        already = set()
        with open("trans.csv", "r", encoding="utf-8") as f:
            csv_readed = f.read()
            for line in csv_readed.splitlines():
                already.add(line.strip())
                f.close()
    except FileNotFoundError:
            csv_readed = None
            f.close()


    #Checking if the last transaction == to the last found in the website
    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(
            headless=True,  # MODIFY WITH DEBUG MODE
            args=[
                '--log-level=3',
                '--disable-gpu',
                '--disable_notifications',
                '--disable-search-engine-choice-screen',
                '--disable-blink-features=AutomationControlled'
            ],
        )
        
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/134.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/Argentina/Buenos_Aires",
                    
        )
        
        
        if "cookies.pkl" in os.listdir():
            await cookies(page)
            await page.goto("https://www.mercadopago.com.ar/activities#from-section=menu")
        else:
            print("No cookies")
            return
            
        await page.wait_for_selector("ul.mp3-list.activities-list section.activity-feed", timeout=2000)
        trans_list = page.locator("ul.mp3-list.activities-list section.activity-feed")
        
        feeds = trans_list.locator(".ui-rowfeed-container")
        current_feed = feeds.nth(0)
        
        day = await trans_list.nth(0).locator(".activity-feed__title").text_content()
               
        date_data = await date_getter_func()
        if day == "Hoy":
            day = f"{date_data[0]} de {date_data[1]} de {date_data[2]}"
        else:
            day = f"{day} de {date_data[2]}"
        trans_name = await current_feed.locator(".ui-rowfeed-title").text_content() #Who sends/receives transaction
        trans_amount = await current_feed.locator(".andes-money-amount__fraction").text_content()           # ----
        trans_amount = trans_amount.replace(".", "")                                                        #     |
        trans_cents = await current_feed.locator(".andes-money-amount__cents").text_content()               #     |---> Getting Integer + Cents and converting to float
        trans_amount = float(trans_amount + "." + trans_cents)                                              # ----

        min_symbol = current_feed.locator(".andes-money-amount__negative-symbol")
        if await min_symbol.count() != 0:
            minus = True
        else:
            minus = False

        if minus:
            trans_amount = float("-" + str(trans_amount))


        if f"{day},{trans_name},{trans_amount}" in already:
            return embedded_transact(user_inp)
        else:
            await bank_scrapping(page)
            return embedded_transact(user_inp)

        
    


async def bank_scrapping(page):
    """Uses Playwright + Cookies_Loader function for scrapping MercadoPago transaction history."""
    
    async with Stealth().use_async(async_playwright()) as p:
        
        if "cookies.pkl" in os.listdir():
            await cookies(page)
            #await page.goto("https://www.mercadopago.com.ar/home")
            await page.goto("https://www.mercadopago.com.ar/activities#from-section=menu")
        else:
            return print("No cookies")
            
        
            
        # Acc Balance
        #bal = page.locator(".andes-money-amount__fraction").first
        #await bal.wait_for()
        #bal = await bal.text_content()
        #bal = bal.replace(".", "")

        #Changes Tab
        #tab_button = page.locator(".andes-tab__link").nth(1)
        #await tab_button.click()
        
        
        # Acc Savings
        #sav = page.locator(".andes-money-amount__fraction").first
        #await sav.wait_for()
        #sav = await sav.text_content()
        #sav = sav.replace(".", "")

        #await page.goto("https://www.mercadopago.com.ar/activities#from-section=menu")
        
        
        
        dt_data = {"Name": [], "Amount": []}
        dt_dates = []
        already = set()
        
        try:
            with open("trans.csv", "r", encoding="utf-8") as f:
                csv_readed = f.read()
                for line in csv_readed.splitlines():
                    already.add(line.strip())
        except FileNotFoundError:
            csv_readed = None

        pages = True
        pages_counter = 1
        
        
        
        while pages:
            try:
                page_button = page.locator(f'.andes-pagination__link[href="/activities/{pages_counter}"][aria-label="Ir a la página {pages_counter}"]')
            
                await page_button.click()
                await page.wait_for_selector("ul.mp3-list.activities-list section.activity-feed", timeout=2000)
                
                trans_list = page.locator("ul.mp3-list.activities-list section.activity-feed")
                trans_days = await trans_list.count()
                #print(trans_days)
            except:
                pages= False
                continue
            
            try:
                html = await page.content()
                #print("activities-list" in html)
                await page.wait_for_timeout(2000)
            except:
                pages = False
                continue


            for day in range(trans_days):
                current = trans_list.nth(day)
                
                feeds = current.locator(".ui-rowfeed-container")
                day = await current.locator(".activity-feed__title").text_content()
                
                date_data = await date_getter_func()
                
                if day == "Hoy":
                    day = f"{date_data[0]} de {date_data[1]} de {date_data[2]}"
                else:
                    if date_data[3][date_data[1]] <= date_data[3][day.split(" ")[2]] and date_data[0] < int(day.split(" ")[0]):     # if im in day 5 and i have transactions from days 1 to 4, same month but last year it will print this year due to being same or major month and min day number
                        date_data[2] = date_data[2] - 1
                    
                    day = f"{day} de {date_data[2]}"
                    

                feeds_count = await feeds.count()

                for transaction in range(feeds_count):
                    current_feed = feeds.nth(transaction)

                    trans_name = await current_feed.locator(".ui-rowfeed-title").text_content() #Who sends/receives transaction

                    trans_amount = await current_feed.locator(".andes-money-amount__fraction").text_content()           # ----
                    trans_amount = trans_amount.replace(".", "")                                                        #     |
                    trans_cents = await current_feed.locator(".andes-money-amount__cents").text_content()               #     |---> Getting Integer + Cents and converting to float (again)
                    trans_amount = float(trans_amount + "." + trans_cents)                                              # ----

                    min_symbol = current_feed.locator(".andes-money-amount__negative-symbol")

                    if await min_symbol.count() != 0:
                        minus = True
                    else:
                        minus = False

                    if minus:
                        trans_amount = float("-" + str(trans_amount))


                    if f"{day},{trans_name}" in already:
                        continue
                    else:
                        dt_data["Name"].append(trans_name)
                        dt_data["Amount"].append(trans_amount)
                        dt_dates.append(day)
                        
            pages_counter += 1
    
    
    # Adding the data to the CSV file
    df = pd.DataFrame(dt_data, index=dt_dates)
    df.index.name = "Date"
    df.to_csv("trans.csv", index=True, mode='a', header=True if csv_readed is None else False)
    
    #bal_and_sav = [float(bal), float(sav)]

    #return bal_and_sav






if __name__ == '__main__':
    asyncio.run(transactions_reader("Noviembre"))
    asyncio.run(balance_savings_reader())