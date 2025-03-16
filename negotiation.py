# negotiation.py

def generate_personal_message(llm, info, purposes):
    """
    Combine text blocks into one single message that references
    extracted information (seller_name, title, etc.).
    """
    introduction = (
        f"Sehr geehrte/r {info.get('seller_name')},\n\n"
        f"ich bin Gabi und zusammen mit meinem Freund auf Deutschlandtour. "
        f"Wir richten uns neu ein und da ist uns '{info.get('title')}' aufgefallen.\n\n"
    )

    text_parts = {
        "Erstkontakt": "Ist der Artikel noch verfügbar?",
        "Preisverhandlung": "Wäre eine Preisanpassung möglich?",
        "Zustandsabfrage": f"Könnten Sie den Zustand näher beschreiben? "
                           f"Aktueller Zustand laut Anzeige: {info.get('condition')}",
        "Terminvereinbarung": f"Könnten wir einen Termin in {info.get('location')} vereinbaren?"
    }

    # Create a message body by appending each selected text block
    body = "\n".join([text_parts[p] for p in purposes if p in text_parts])
    
    # Feed the combined text into the LLM for a refined final message
    prompt = (
        f"{introduction}{body}\n\n"
        f"Bitte verfasse eine freundliche, höfliche Nachricht in meinem Namen."
    )

    return llm.generate(prompt)
