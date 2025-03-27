from openai import OpenAI
from app.core.config import config
from app.utils.helpers import encode_image

client = OpenAI(api_key=config.OPENAI_API_KEY)

SYMBOLS = [
    'Man', 'Woman', 'Child', 'Baby', 'King', 'Queen', 'Family',
    'Old Person', 'Dancing Person', 'Bird', 'Butterfly', 'Cat',
    'Dog', 'Elephant', 'Fish', 'Fox', 'Horse', 'Lion', 'Owl',
    'Rabbit', 'Snake', 'Spider', 'Turtle', 'Wolf', 'Sun', 'Moon',
    'Stars', 'Tree', 'Flower', 'Leaf', 'Cloud', 'Fire', 'Water',
    'Waves', 'Mountain', 'River', 'Vine', 'Arrow', 'Anchor',
    'Bag', 'Bell', 'Book', 'Bridge', 'Candle', 'Crown', 'Cup',
    'Door', 'Envelope', 'Flag', 'Heart', 'House', 'Key',
    'Ladder', 'Lock', 'Mirror', 'Ring', 'Ship', 'Sword',
    'Umbrella', 'Circle', 'Triangle', 'Square', 'Arrow',
    'Cross', 'Diamond', 'Line (Straight)', 'Line (Wavy)',
    'Spiral', 'Zigzag', 'Initials', 'Numbers', 'Car', 'Plane',
    'Boat', 'Train', 'Chains', 'Eye', 'Hand', 'Starburst',
    'Yin-Yang', 'Apple', 'Bread', 'Egg', 'Acorn', 'Airplane',
    'Balloon', 'Bat', 'Bee', 'Bow', 'Bridge', 'Broken Line',
    'Chain', 'Chalice', 'Clover', 'Crescent Moon', 'Crown',
    'Dice', 'Dragon', 'Eagle', 'Feather', 'Frog', 'Glove', 'Hat',
    'Hourglass', 'Kite', 'Lantern', 'Lightning Bolt', 'Mask',
    'Nest', 'Palm Tree', 'Pyramid', 'Rose', 'Scissors', 'Shield',
    'Shoe', 'Starfish', 'Sword', 'Telescope', 'Wheel', 'Windmill'
]

def analyze_symbols(image_path):
    """Analyze symbols in a coffee cup image using OpenAI GPT-4o."""
    print(f"image path in the symbol anal;yzer->{image_path}")
    base64_image = encode_image(image_path)
    symbol_list_text = ", ".join(SYMBOLS)
    #print(f"Base 64 image->{base64_image}")

    #prompt_text = (
    #    f"This is an image of coffee traces in an empty cup.\n"
    #    f"Detect overall shapes and tiny symbols in the coffee patterns.\n"
    #    f"List observations with their location, strength (1-10), and meaning in coffee cup reading culture.\n"
    #    f"Format as MATLAB structure:\n"
    #    f"  Reading(1).Observation = {{'example'}};\n"
    #    f"  Reading(1).Location = {{'example'}};\n"
    #    f"  Reading(1).Strength = {{'10'}};\n"
    #    f"  Reading(1).Meaning = {{'example'}};\n"
    #)
    prompt_text = (
    "You are an expert in Tasseography, the art of reading coffee grounds in an empty cup. "
    "This base64-encoded image shows coffee traces from a coffee cup. "
    "Analyze the coffee patterns to identify distinct shapes and tiny symbols. "
    "For each observation, determine:\n"
    "- Observation: The shape or symbol (e.g., horse, circle, tree).\n"
    "- Location: Where it appears in the image (e.g., top-left, center, bottom-right).\n"
    "- Strength: A score from 1-10 based on clarity and prominence (1 = faint, 10 = very clear).\n"
    "- Meaning: Its interpretation in traditional coffee cup reading culture (e.g., journey, unity, growth).\n"
    "Return the results in MATLAB structure format, with multiple readings if multiple symbols are detected:\n"
    "  Reading(1).Observation = {'horse'};\n"
    "  Reading(1).Location = {'top-left'};\n"
    "  Reading(1).Strength = {'6'};\n"
    "  Reading(1).Meaning = {'journey'};\n"
    "  Reading(2).Observation = {'circle'};\n"
    "  Reading(2).Location = {'center'};\n"
    "  Reading(2).Strength = {'8'};\n"
    "  Reading(2).Meaning = {'unity'};\n"
    "Provide at least one observation, even if faint, and ensure meanings align with Tasseography traditions."
    f"You can also make use of these Symbol Examples:{symbol_list_text} if there is a need."
    "Do not respond with 'unable to view'—analyze the image provided."
)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
                ],
            }
        ],
    )
    
    return response.choices[0].message.content