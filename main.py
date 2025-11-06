import asyncio, os, modules
from modules.ai import *



os.system("cls" if os.name == "nt" else "clear")

print(r"""  ______ _                        _____                _____ _    _          _____ _   _ 
 |  ____(_)                      |_   _|   /\         / ____| |  | |   /\   |_   _| \ | |
 | |__   _ _ __   __ _ _ __   ___  | |    /  \ ______| |    | |__| |  /  \    | | |  \| |
 |  __| | | '_ \ / _` | '_ \ / __| | |   / /\ \______| |    |  __  | / /\ \   | | | . ` |
 | |    | | | | | (_| | | | | (__ _| |_ / ____ \     | |____| |  | |/ ____ \ _| |_| |\  |
 |_|    |_|_| |_|\__,_|_| |_|\___|_____/_/    \_\     \_____|_|  |_/_/    \_\_____|_| \_|
                                                                                         
                                                                                         """)

while True:
    user_input= input("Prompt >> ")
    asyncio.run(call_ai(user_input))
    
#Modify local functions to work being called by IDE's version without commenting the @tool decorator

# Must re-do the transactions_reading due to non-coherency betwen user's query and embedding output (Just adding filters and many handlers)

# https://medium.com/@abhyankarharshal22/mastering-browser-automation-with-langchain-agent-and-playwright-tools-c70f38fddaa6 This could help with web searching (Its scrapping)

# DEBUG SWITCHER IS IMPLEMENTED BUT WITH NO FUNCTIONS