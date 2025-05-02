import random

# Collection of Nakano Miku facts and captions
MIKU_FACTS = [
    # Personality traits
    "Miku is known for being the most soft-spoken and reserved of the quintuplets.",
    "Despite her shy nature, Miku has shown she can be quite stubborn when determined.",
    "Miku's development from shy to more confident is a fan-favorite character arc.",
    "Miku tends to overthink situations, especially those involving Fuutarou.",
    "She has the most noticeable pout face among the quintuplets, which fans adore.",
    
    # Relationships
    "Miku and Nino have a complex relationship, but they deeply care for each other.",
    "Miku and Yotsuba share a special bond as the quieter sisters among the quintuplets.",
    "Miku was the first sister to recognize Fuutarou when he changed his hair color.",
    "Miku and Ichika have a tender relationship despite later complications.",
    "Miku tends to be protective of Yotsuba, the fourth sister.",
    
    # Appearance
    "Miku's casual outfit typically includes a sweater, skirt, and thigh-high socks.",
    "Miku's hairstyle features a side bang that often partially covers her face.",
    "Unlike her sisters, Miku rarely changes her hairstyle throughout the series.",
    "Miku's blue headphones match her eye color, creating her signature look.",
    "Miku is often drawn with a slightly more subdued expression than her sisters.",
    
    # Interest in History
    "Miku can recite the names and achievements of over 30 Sengoku-era warlords.",
    "Miku has collected several replicas of historical Japanese swords.",
    "Miku has visited numerous historical sites in Japan as seen in flashbacks.",
    "Her knowledge of the Sengoku period has helped the sisters in school projects.",
    "Miku keeps a special notebook where she writes historical facts she learns.",
    "Nakano Miku is one of the quintuplet sisters in 'The Quintessential Quintuplets' (Gotoubun no Hanayome).",
    "Miku is the third sister among the Nakano quintuplets.",
    "Miku's favorite subject is History, especially Japanese History.",
    "Miku's birthday is May 5th, which she shares with her sisters.",
    "Miku is a huge fan of Sengoku era warlords and often quotes them.",
    "Miku's signature accessory is her blue headphones, which she wears around her neck.",
    "In the popularity polls, Miku consistently ranked as one of the most popular characters.",
    "Miku is generally shy and introverted, but becomes passionate when discussing her interests.",
    "Miku has a talent for cooking, though she starts out quite terrible at it.",
    "The color associated with Miku is blue, reflected in her character design.",
    "Miku's voice actress in the anime is Miku Itō.",
    "Miku developed feelings for Fuutarou after he acknowledged her effort in studying.",
    "Despite being quintuplets, Miku can be distinguished by her more serious and reserved expression.",
    "Miku enjoys reading historical books in her free time.",
    "Miku has the lowest confidence among her sisters but shows great determination.",
    "Her room is decorated with historical figures and Japanese warlord memorabilia.",
    "Miku often disguises herself as her sisters to test if Fuutarou can recognize her.",
    "She is especially knowledgeable about the Sengoku period in Japanese history.",
    "Miku's favorite food is matcha-flavored sweets.",
    "She has a notable pouting face that fans adore.",
    "Miku once dressed as a Japanese warlord for a school event.",
    "She tends to have a pessimistic outlook but works hard to overcome it.",
    "Miku is often seen reading books about Japanese warlords.",
    "She has a collection of historical figurines in her room.",
    "Miku puts great effort into improving her cooking skills to impress Fuutarou.",
    "Her dream is to become a history teacher.",
    "Miku can be very competitive when it comes to getting Fuutarou's attention.",
    "She is the first among the quintuplets to fall in love with Fuutarou.",
    "Miku's favorite Sengoku warlord is Date Masamune.",
    "She tends to hide her face behind her bangs when embarrassed.",
    "Miku excels at memorization, especially historical dates and facts.",
    "She often wears thigh-high socks as part of her casual outfit.",
    "Miku can be surprisingly bold when pursuing her goals.",
    "Her cooking improves significantly throughout the series.",
    "Miku enjoys listening to classical music through her headphones.",
    "She has a special bread that she likes to bake.",
    "Miku has a habit of quietly observing others before taking action.",
    "She is skilled at impersonating her sisters' mannerisms.",
    "Miku's room is the neatest among the quintuplets.",
    "She has a collection of history books that she treasures.",
    "Miku struggles with expressing her feelings directly.",
    "She often uses historical quotes to express her thoughts.",
    "Miku is the third born but often acts like a middle child.",
    "Her favorite season is autumn because it's good for reading.",
    "Miku has the highest test scores in history among her sisters.",
    "She can recite historical battle strategies from memory.",
    "Miku's love for history was partly inspired by a teacher she admired.",
    "She practices calligraphy as a hobby.",
    "Miku can identify historical artifacts with impressive accuracy.",
    "She blushes easily when complimented by Fuutarou."
]

# Collection of cute/positive captions for image posts
MIKU_CAPTIONS = [
    # Reference to her interests
    "History lessons with Professor Miku when? 📚💙",
    "POV: You just asked Miku about the Sengoku period 📜",
    "Caught Miku reading about Date Masamune again! 📚",
    "When the history textbook mentions your favorite warlord 👀",
    "Miku's headphones probably playing historical audiobooks 🎧",
    
    # Character traits
    "That special moment when shy Miku becomes confident 💪",
    "The duality of Miku: shy around people, passionate about history 💙",
    "Miku's pout is a national treasure 😤💙",
    "Behind those bangs is the cutest quintuplet 💙",
    "When Miku gets determined, there's no stopping her 🔥",
    
    # Sister interactions
    "Miku secretly helping her sisters study history 📚",
    "When Miku successfully disguises as one of her sisters 🕵️‍♀️",
    "Miku and Yotsuba moments are the sweetest 💙💚",
    "The special bond between Miku and her sisters is everything 💕",
    "Just Miku being the most supportive sister 💙",
    
    # Series moments
    "The bread scene with Miku was top tier anime content 🍞",
    "Still thinking about that confession scene... 💙",
    "Miku's character development is a masterpiece 📈",
    "When Miku stood up for herself, I cheered! 🙌",
    "The way Miku looks at Fuutarou... pure love 💙",
    "Just Miku being adorable as always! 💙",
    "Miku's smile brightens the darkest days! 🎧",
    "History buff Miku looking cute today! 📚",
    "The best quintuplet don't @ me 💙",
    "Miku Nakano appreciation post! 💙🎧",
    "Those blue headphones are iconic! 🎧",
    "Miku Monday motivation! 💪💙",
    "POV: You just complimented Miku's cooking 🍳",
    "Headphone gang rise up! 🎧",
    "That shy smile though... 💙",
    "Miku in her natural habitat 📚",
    "The cutest pout in anime history! 😤💙",
    "History nerd Miku is best Miku 📜",
    "Miku's determination is inspiring! 💪",
    "Blue-themed everything because Miku deserves it! 💙",
    "Miku Monday! The best day of the week! 💙",
    "Just finished another episode featuring Miku! 🎧",
    "Daily dose of Miku cuteness! 💙",
    "Miku's cooking has improved so much! 🍜",
    "Can't get enough of those beautiful blue eyes! 👀💙",
    "Miku being effortlessly adorable as usual! 💙",
    "Team Miku forever! 🎧💙",
    "The way she hides behind her bangs... adorable! 💙",
    "Miku deserves all the happiness! 💙",
    "POV: Miku notices you noticing her 👀",
    "Sengoku era enthusiast looking precious! 🎧",
    "Miku's character development is top tier! 📈",
    "That moment when Miku gets competitive... 💪",
    "Headphones: On. History book: Open. Heart: Stolen. 💙",
    "When she talks about history, her eyes light up! ✨",
    "Miku trying her best as always! 💙",
    "The quintuplet with the biggest heart! 💙",
    "Miku appreciation hours are 24/7! 🕒",
    "Protecting this smile at all costs! 💙",
    "POV: You recognized Miku despite her disguise 👀",
    "The perfect balance of shy and determined! 💙",
    "Miku's journey is so inspiring! 📈",
    "That moment when she removes her headphones... 🎧",
    "Living for Miku's rare smiles! 💙",
    "Miku in her element! 📚💙"
]

def get_random_miku_fact():
    """
    Get a random fact about Nakano Miku.
    
    Returns:
        str: A random Miku fact
    """
    return random.choice(MIKU_FACTS)

def get_random_miku_caption():
    """
    Get a random caption for a Miku image post.
    
    Returns:
        str: A random Miku caption
    """
    return random.choice(MIKU_CAPTIONS)
