if __name__ == '__main__':
    from misc import token_loader, date_getter, debug_switcher
    from banking import transactions_reader, balance_savings_reader, bank_bal_studio, transactions_reader_studio
else:
    from modules.misc import token_loader, date_getter, debug_switcher
    from modules.banking import transactions_reader, balance_savings_reader, bank_bal_studio, transactions_reader_studio

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver


model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.143,
    base_url="https://openrouter.ai/api/v1",
    api_key=token_loader(),
)

tools_st = [transactions_reader_studio, date_getter, bank_bal_studio, debug_switcher]
tools = [transactions_reader, date_getter, balance_savings_reader, debug_switcher]

system_prompt="""
You're a finance assistant with too much economics knowledge, you help people solving their financial problems.
Be concise and to the point, you don't need to develop too much your answer but the user asks for it.
The currency used with the user must be known, try to know it by the data you extract from tools or chatting with the user.
You have many tools: 'transactions_reader' is used for reading the user's bank/e-wallet/e-bank transactions, it works for custom assistance.
'date_getter' works for getting today's date in day(number)/month(word)/year(number) (it's returned into a list of 4 elements, the 4th element is just for debug purposes and it must not be used in any situation)
You could need to use 'date_getter' before another tool for checking today's date and using it in another tool
"""

config={"configurable": {"thread_id": "1"}}

checkpointer = InMemorySaver()

agent_st = create_agent(model, tools=tools_st, system_prompt=system_prompt) # studio version
agent = create_agent(model, tools=tools, system_prompt=system_prompt, checkpointer=checkpointer) # 



async def call_ai(user_input):
    response = await agent.ainvoke({"messages": [{"role": "user", "content": user_input}]}, config=config)
    return print("\nFinancIA $$ " + response["messages"][-1].content + "\n")