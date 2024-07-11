def create_faq(faq, bot_username, bot_full_name) -> str:
    if len(faq) == 0:
        text = f"FAQ for @{bot_username} is empty!"
    else:
        text = f"{bot_full_name}:"
        for i, faq_obj in enumerate(faq):
            text += f"\n\n<b>{i + 1}.</b> {faq_obj['question']}"

    return text
