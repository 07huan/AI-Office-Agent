chat_memorys={}

def get_chat_history(conversation_id:str):
    if conversation_id not in chat_memorys:
        chat_memorys[conversation_id]=[]

    return chat_memorys[conversation_id]


def add_message(conversation_id:str,role:str,content:str):
    history=get_chat_history(conversation_id)

    history.append({
        "role":role,
        "content":content
    })
