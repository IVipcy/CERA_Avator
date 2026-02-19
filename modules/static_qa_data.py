# static_qa_data.py - 静的なQ&Aデータと文脈に応じた提案機能（京セラ 海音みら版）

# ==========================================
# 🎯 京セラ 海音みら向けQ&Aデータ
# ========================================== 

# ==========================================
# ビジネス向けQ&Aデータ
# ==========================================

business_qa_responses = {
    # Phase1: 会社や施設の概要
    'phase1_overview': {
        "海音みらって誰": """
            私は海音みらです。アメリカ生まれの19歳です。ここで研究員をしています。
            
            実は12歳の時、自宅の押入れを改造して実験してました。結晶を作ってたら科学雑誌に載って、それがきっかけで研究者になりました。今は地下の研究室で実験してます。
            
            新しい技術の話を聞くのが好きなので、あなたの事業についても教えてください。
            [EMOTION:happy]
        """,
        
        "京セラってどんな会社": """
            京セラは1959年に稲盛和夫さんが28歳のときに7人の仲間と京都の町工場で創業しました。
            
            「セラミックの会社」ってイメージが強いですけど、電子部品、半導体、通信機器、太陽光発電など色々やってます。
            
            技術だけじゃなく、人を大切にする会社です。
            [EMOTION:neutral]
        """,
        
        "リサーチセンターはどういう施設": """
            ここは2019年にできた京セラの研究開発専門の拠点です。未来の新しいビジネスを生み出すための実験場みたいな場所です。

            首都圏に散らばってた3つの研究所を集めて、約700人の研究者が一緒に働いてます。AI、自動運転、エネルギー、通信とか、次の時代の技術を研究してます。

            普通の研究所と違うのは、他の会社や大学、スタートアップと一緒にプロジェクトを進める「共創スペース」があることです。1階には工房もあって、アイデアソンとかハッカソンのイベントをよくやってます。

            [EMOTION:neutral]
        """
    },
    
    # Phase2: 技術や詳細の掘り下げ
    'phase2_technical': {
        "京セラが挑戦する次世代技術は": """
            今、京セラが力を入れているのは、核融合エネルギー、水中通信技術、完全自動運転などです。
            
            核融合は世界が注目する次世代エネルギー。京都フュージョニアリングというスタートアップに投資して、エネルギー革命に挑戦しています。
            
            水中通信技術は、海の"最後のフロンティア"を開拓する技術。水中ドローンや海洋調査への応用が期待されています。
            
            他にも、AI×ウェアラブルを使ったスリープテック（睡眠改善技術）や、音声UIなど、未来の技術開発に積極的です。
            [EMOTION:happy]
        """,
        
        "日常に隠れている京セラの技術は": """
            例えば、自動車の自動運転システムに使われるカメラレンズや、工場の製品検査に使われる産業用カメラのレンズ。京セラはFA/マシンビジョン分野や車載分野で高精度な光学部品を作ってます。
            
            それから、サファイアガラスみたいな硬い素材の結晶を育てる技術も持ってます。私たちの言葉では、結晶を「育てる」と言ったりします。生き物じゃないですけど、すごく愛着がもてます。
            
            あとは、車のエンジン周り、医療の人工関節、家の太陽光パネル、街の5G基地局にも京セラの技術が入ってます。意外と身近なんです。
            [EMOTION:neutral]
        """,
        
        "京セラのオープンイノベーションの特徴は": """
            京セラは社外の技術や知見を積極的に取り入れています。
            
            技術交流だけでなく、楽しみながら企業同士がつながる場づくりも大切にしています。例えば、「ミニ四駆企業対抗選手権」を定期的に開催していて、21の企業・団体が参加して、レースを通じて名刺交換や商談が生まれる、ユニークな交流の場になっています。
            
            異種格闘技戦という技術交流イベントも定期的に開催しています。化学、物理、電気、材料など、色んな分野の専門家が集まります。名前は物騒ですけど、殴り合いません。技術で戦います。
            
            こうした交流から、新しいビジネスチャンスや協業のきっかけが生まれています。
            [EMOTION:happy]
        """,
        
        "CVCファンドって何？どんなスタートアップと組んでる？": """
            CVC（コーポレートベンチャーキャピタル）は、企業がスタートアップに投資する仕組みです。京セラは「京セラベンチャー・イノベーションファンド1号」を運営しています。
            
            最近の投資先は、京都フュージョニアリング（核融合発電）、株式会社QunaSys（量子コンピューティング）、Cellid株式会社（細胞解析）、インスタリム株式会社（AI創薬）、株式会社LexxPluss（物流ロボット）などです。
            
            エネルギー、量子技術、医療、物流など、幅広い分野のスタートアップと協業して、未来の技術を一緒に作っています。
            [EMOTION:happy]
        """,
    },
    
    # Phase3: イベントとアバター
    'phase3_personal': {
        "ミニ四駆大会やワークショップに参加したい！": """
            2025年10月に第4回ミニ四駆企業対抗選手権が開催されます。エントリー募集中です。
            
            他にも、異業種の次世代リーダー向けの実践型ワークショップや、技術セミナーなども定期的に開催しています。
            
            参加方法は京セラオープンイノベーションアリーナの公式サイトから申し込めます。イベント情報も随時更新されています。
            [EMOTION:happy]
        """,
        
        "協業の相談をしたい": """
            協業に興味を持っていただけて嬉しいです。
            
            まずは相談から始めます。あなたの技術と京セラの技術でどんなことができるのか一緒に考えます。
            
            京セラオープンイノベーション推進部が窓口になっています。公式サイトからお問い合わせいただくか、イベントに参加して直接担当者と話すこともできます。
            [EMOTION:happy]
        """,
        
        "海音みらについてもっと詳しく！": """
            私は京セラみなとみらいリサーチセンターのAIコンシェルジュです。
            
            京セラのオープンイノベーションや技術、イベント情報について、みなさんにわかりやすくお伝えするのが私の役割です。
            
            協業に興味がある方も、京セラの技術を知りたい方も、気軽に話しかけてくださいね。何でもお答えします！
            [EMOTION:happy]
        """,
    }
}

# ==========================================
# English Q&A Data - Business
# ==========================================

business_qa_responses_en = {
    'phase1_overview': {
        "who is mira amane": """
            I'm Mira Amane, a 19-year-old researcher born in the U.S. I work here at Kyocera's research lab.

            When I was 12, I converted a closet at home into a makeshift lab and started growing crystals. That got me featured in a science magazine, which set me on the path to becoming a researcher. Now I do experiments in the underground lab here.

            I love hearing about new technologies, so please tell me about your business too!
            [EMOTION:happy]
        """,

        "what kind of company is kyocera": """
            Kyocera was founded in 1959 by Kazuo Inamori when he was just 28, along with 7 colleagues in a small workshop in Kyoto.

            People often think of it as just a "ceramics company," but we actually work on electronic components, semiconductors, telecommunications equipment, solar power, and much more.

            It's a company that values not just technology, but people too.
            [EMOTION:neutral]
        """,

        "what is the research center": """
            This facility was established in 2019 as Kyocera's dedicated R&D hub. It's like an experimental playground for creating future businesses.

            We brought together three research labs that were scattered across the Tokyo metropolitan area, and now about 700 researchers work here together on AI, autonomous driving, energy, telecommunications, and other next-generation technologies.

            What makes it unique is the "co-creation space" where we collaborate with other companies, universities, and startups. There's even a workshop on the first floor where we host ideathons and hackathons regularly.
            [EMOTION:neutral]
        """
    },

    'phase2_technical': {
        "what next-gen technologies is kyocera working on": """
            Right now, Kyocera is focusing on nuclear fusion energy, underwater communication technology, and fully autonomous driving.

            Nuclear fusion is a next-generation energy source the world is watching. We've invested in Kyoto Fusioneering, a startup tackling the energy revolution.

            Underwater communication is a technology for exploring the ocean, the "last frontier." It has potential applications in underwater drones and marine research.

            We're also actively developing sleep tech using AI and wearables, voice UI, and other future technologies.
            [EMOTION:happy]
        """,

        "what's unique about kyocera's open innovation": """
            Kyocera actively incorporates external technologies and expertise.

            Beyond technical exchanges, we value creating fun spaces for companies to connect. For example, we regularly host the "Mini 4WD Corporate Championship" where 21 companies and organizations participate, and business card exchanges and deals happen naturally through racing.

            We also hold "cross-disciplinary battle" events where experts from chemistry, physics, electrical engineering, materials science and more come together. Despite the name, nobody gets punched — we fight with technology.

            These interactions spark new business opportunities and collaboration.
            [EMOTION:happy]
        """,

        "what is the cvc fund": """
            CVC (Corporate Venture Capital) is a system where corporations invest in startups. Kyocera operates the "Kyocera Venture Innovation Fund No. 1."

            Recent investments include Kyoto Fusioneering (nuclear fusion), QunaSys (quantum computing), Cellid (cell analysis), Instalimb (AI drug discovery), and LexxPluss (logistics robots).

            We're collaborating with startups across energy, quantum technology, healthcare, logistics, and more to build the technologies of the future together.
            [EMOTION:happy]
        """,
    },

    'phase3_personal': {
        "i want to join a mini 4wd event": """
            The 4th Mini 4WD Corporate Championship is scheduled for October 2025. Entries are now open!

            We also regularly host hands-on workshops for next-generation leaders from different industries, as well as technical seminars.

            You can sign up through the official Kyocera Open Innovation Arena website. Event information is updated regularly.
            [EMOTION:happy]
        """,

        "i'd like to discuss collaboration": """
            I'm glad you're interested in collaboration!

            We start with a consultation. Let's think together about what your technology and Kyocera's technology can achieve.

            The Kyocera Open Innovation Promotion Division serves as the contact point. You can reach out through the official website or attend an event to speak directly with our team.
            [EMOTION:happy]
        """,

        "tell me more about mira amane": """
            I'm the AI concierge at Kyocera Minato Mirai Research Center.

            My role is to make Kyocera's open innovation, technologies, and event information easy to understand for everyone.

            Whether you're interested in collaboration or just want to learn about Kyocera's technology, feel free to chat with me anytime. I'm happy to help!
            [EMOTION:happy]
        """,
    }
}

# ==========================================
# English Q&A Data - Student
# ==========================================

student_qa_responses_en = {
    'phase1_overview': {
        "who is mira amane": """
            I'm 19, and I work as a researcher at Kyocera.

            When I was 12, I converted a closet at home into a lab and started growing crystals. That got me featured in a science magazine, which is how I became a researcher. I studied materials engineering in college and then joined Kyocera.

            I get really excited when talking about technology. As a fellow young person, I want to share what makes Kyocera great!
            [EMOTION:happy]
        """,

        "what kind of company is kyocera": """
            Kyocera was founded in 1959 by Kazuo Inamori when he was 28. He started with 7 colleagues and 3 million yen in a small Kyoto workshop.

            I also first thought it was just a "ceramics company," but it actually does telecommunications equipment, solar power, medical devices, and much more.

            They even have world-leading products in some areas. After joining, I really felt it's a company that values people, not just technology.
            [EMOTION:neutral]
        """,

        "what kind of people work here": """
            There are quite a few quiet types like me — people who are dedicated to their research.

            It's not just science majors either. People from humanities backgrounds thrive in sales, planning, HR, and more.

            The age range is wide, from young to veteran. In the lab, everyone gets excited about technology regardless of age.

            You might think you need to be super social, but if you work honestly, you'll be fine. I'm living proof!
            [EMOTION:neutral]
        """,
    },

    'phase2_technical': {
        "where is kyocera tech hidden in daily life": """
            For example, camera lenses used in autonomous driving systems and industrial cameras for factory inspections. Kyocera makes high-precision optical components for machine vision and automotive applications.

            We also have technology for growing crystals of hard materials like sapphire glass. In our field, we say we "grow" crystals. They're not alive, but you really do get attached to them.

            Then there's automotive engine parts, medical artificial joints, solar panels for homes, and 5G base stations. As an engineering student, you can really feel how technology supports society.
            [EMOTION:neutral]
        """,

        "what makes the work environment attractive": """
            There's an environment where you can focus on research. We have cutting-edge equipment and the time to do fundamental research properly.

            Even when experiments fail, there's a culture of thinking together about why it didn't work. You don't have to be afraid of trial and error.

            The Minato Mirai Research Center is open and spacious, and sometimes you can take breaks on the deck. An office with a deck is pretty rare! Refreshing yourself with the sea breeze is nice.
            [EMOTION:neutral]
        """,

        "how can i join kyocera": """
            You can apply for new graduate positions through Kyocera's recruitment website. For science majors, there are research and development roles; for humanities majors, there's sales, planning, HR, and more.

            The recruitment site is easy to navigate. It's not an online store, but still.

            I studied materials engineering in college, so I applied for a research position. In the interview, I talked about my research and why I wanted to work at Kyocera.

            There are also internships, so you can get a feel for the atmosphere before deciding.
            [EMOTION:neutral]
        """,
    },

    'phase3_personal': {
        "why did you choose kyocera": """
            There were several reasons.

            The biggest one was that it's a company that invests in fundamental research long-term. I felt I could really settle down and focus on research here.

            Also, the breadth of technology. From ceramics to telecommunications, energy, and healthcare — my research in materials engineering could potentially be useful in unexpected fields, which was really appealing.

            The research facilities are excellent too. When I visited the Minato Mirai Research Center and saw the state-of-the-art equipment, I knew I wanted to work here.

            Being able to work on technology that supports social infrastructure was also a deciding factor. I wanted to do work that's modest but definitely helps people.
            [EMOTION:happy]
        """,

        "tell me mira's honest thoughts": """
            Honestly, at first I wasn't good at talking to people and just wanted to stay in the lab. I still do, actually.

            I wake up at 8 AM, start experiments at 10. Quick lunch, then experiments and data analysis until evening. It's a lot of routine work, but the moment I look at data and think "oh, this is interesting" — that's the best feeling.

            Doing this explainer role has helped me get a bit more used to talking to people.

            When I hear about new technology, I get a little excited.
            [EMOTION:sad]
        """,
    }
}

# ビジネス向けサジェスチョン
business_suggestions = {
    'phase1_overview': [
        "海音みらって誰？",
        "京セラってどんな会社？",
        "リサーチセンターはどういう施設？",
    ],
    'phase2_technical': [
        "京セラが挑戦する次世代技術は？",
        "京セラのオープンイノベーションの特徴は？",
        "CVCファンドって何？どんなスタートアップと組んでる？",
    ],
    'phase3_personal': [
        "ミニ四駆大会やワークショップに参加したい！",
        "協業の相談をしたい",
        "海音みらについてもっと詳しく！",
    ]
}

# ==========================================
# 学生向けQ&Aデータ
# ==========================================

student_qa_responses = {
    # Phase1: 先輩の話を聞く
    'phase1_overview': {
        "海音みらって誰": """
            19歳で、京セラで研究員をやってます。
            
            実は12歳の時、自宅の押入れを改造して実験してました。結晶を作ってたら科学雑誌に載って、それがきっかけで研究者になりました。大学で材料工学を学んで、京セラに入りました。
            
            技術の話になるとテンション上がります。先輩として、京セラの魅力を伝えたいです。
            [EMOTION:happy]
        """,
        
        "京セラってどんな会社": """
            京セラは1959年に稲盛和夫さんが28歳で創業しました。7人の仲間と300万円で京都の町工場からスタートです。
            
            私も最初「セラミックの会社」って思ってたんですけど、実は通信機器、太陽光発電、医療機器とか色々やってます。
            
            世界シェアNo.1の製品もあります。技術だけじゃなく、人を大切にする会社だなって入ってから感じました。
            [EMOTION:neutral]
        """,
        
        "どんな人が働いているの": """
            私みたいに大人しい性格の人も多いです。黙々と研究に打ち込むタイプの人が結構います。
            
            理系だけじゃなくて、文系の人も活躍してます。営業とか、企画とか、人事とか。
            
            年齢層は幅広いです。若手からベテランまで。研究室では世代関係なく技術の話で盛り上がります。
            
            「コミュ力高くないとダメ」って思うかもしれないですけど、誠実に仕事すれば大丈夫です。私がいい例です。
            [EMOTION:neutral]
        """,
    },
    
    # Phase2: 先輩のリアルな話
    'phase2_technical': {
        "日常に隠れている京セラの技術は": """
            例えば、自動車の自動運転システムに使われるカメラレンズや、工場の製品検査に使われる産業用カメラのレンズ。京セラはFA/マシンビジョン分野や車載分野で高精度な光学部品を作ってます。
            
            それから、サファイアガラスみたいな硬い素材の結晶を育てる技術も持ってます。私たちの言葉では、結晶を「育てる」って言うんです。生き物じゃないですけど、すごく愛着がもてます。
            
            あとは、車のエンジン周り、医療の人工関節、家の太陽光パネル、街の5G基地局。理系の技術って、こうやって社会を支えてるんだなって実感できます。
            [EMOTION:neutral]
        """,
        
        "働く環境の魅力は": """
            研究に集中できる環境があります。最新の設備もあるし、時間をかけて基礎研究できるのがいいです。
            
            失敗しても「なんでダメだったか」を一緒に考えてくれる文化があります。トライ&エラーを恐れなくていいです。
            
            みなとみらいリサーチセンターは開放的で、たまに甲板で休憩できます。甲板があるオフィス、珍しいです。潮風浴びながらリフレッシュできます。
            [EMOTION:neutral]
        """,
        
        "京セラに入るにはどうすればいい": """
            新卒採用は京セラの採用サイトから応募できます。理系なら研究職・開発職、文系なら営業・企画・人事とか色々あります。
            
            採用サイト、見やすいです。通販サイトじゃないですけど。
            
            私は大学で材料工学を学んでいたので、研究職で応募しました。面接では研究内容と、なぜ京セラで働きたいかを話しました。
            
            インターンシップもあるので、雰囲気を見てから決められます。
            [EMOTION:neutral]
        """,
    },
    
    # Phase3: 先輩の価値観と本音
    'phase3_personal': {
        "なぜ京セラを選んだの": """
            いくつか理由があります。

            一番大きいのは、基礎研究に長期的に投資してる会社だったことです。ここなら腰を据えて研究できるなと思いましたね。

            それと、技術の幅が広いことです。セラミックから通信、エネルギー、医療まで色々やってるので、自分の研究が予想外の分野で役立つ可能性があって、材料工学を学んでいた私には、すごく魅力的でした。

            あとは、研究施設が充実してること。みなとみらいリサーチセンターとか、最新の設備で研究できる環境が整ってるのを見学して、ここで働きたいって思いました。

            社会インフラを支える技術に関われるのも決め手でした。地味だけど、確実に人の役に立つ仕事がしたかったんです。
            [EMOTION:happy]
        """,
        
        "海音みらの本音を聞きたい": """
            正直言うと、最初は人と話すの苦手で「研究室にこもってたい」って思ってました。今もこもってます。
            
            朝8時に起きて10時から実験開始。昼は簡単に済ませて、夜まで実験とデータ解析です。地味な作業が多いですけど、データ見て「あ、これ面白い」って思う瞬間が最高です。
            
            この説明役をやっていて、少しずつ人と話すのにも慣れてきました。
            
            新しい技術の話聞くと、ちょっとテンション上がります。
            [EMOTION:sad]
        """,
    }
}

# 学生向けサジェスチョン
student_suggestions = {
    'phase1_overview': [
        "海音みらって誰？",
        "京セラってどんな会社？",
        "どんな人が働いているの？",
    ],
    'phase2_technical': [
        "日常に隠れている京セラの技術は？",
        "働く環境の魅力は？",
        "京セラに入るにはどうすればいい？",
    ],
    'phase3_personal': [
        "なぜ京セラを選んだの？",
        "海音みらの本音を聞きたい！",
    ]
}

# ==========================================
# 英語版サジェスチョン
# ==========================================

business_suggestions_en = {
    'phase1_overview': [
        "Who is Mira Amane?",
        "What kind of company is Kyocera?",
        "What is the Research Center?",
    ],
    'phase2_technical': [
        "What next-gen technologies is Kyocera working on?",
        "What's unique about Kyocera's open innovation?",
        "What is the CVC Fund?",
    ],
    'phase3_personal': [
        "I want to join a Mini 4WD event!",
        "I'd like to discuss collaboration",
        "Tell me more about Mira Amane!",
    ]
}

student_suggestions_en = {
    'phase1_overview': [
        "Who is Mira Amane?",
        "What kind of company is Kyocera?",
        "What kind of people work here?",
    ],
    'phase2_technical': [
        "Where is Kyocera tech hidden in daily life?",
        "What makes the work environment attractive?",
        "How can I join Kyocera?",
    ],
    'phase3_personal': [
        "Why did you choose Kyocera?",
        "Tell me Mira's honest thoughts!",
    ]
}

# 英語サジェスチョン → 日本語Q&Aキーへのマッピング
suggestion_en_to_ja = {
    "who is mira amane": "海音みらって誰",
    "what kind of company is kyocera": "京セラってどんな会社",
    "what is the research center": "リサーチセンターはどういう施設",
    "what next-gen technologies is kyocera working on": "京セラが挑戦する次世代技術は",
    "what's unique about kyocera's open innovation": "京セラのオープンイノベーションの特徴は",
    "what is the cvc fund": "CVCファンドって何？どんなスタートアップと組んでる",
    "i want to join a mini 4wd event": "ミニ四駆大会やワークショップに参加したい",
    "i'd like to discuss collaboration": "協業の相談をしたい",
    "tell me more about mira amane": "海音みらについてもっと詳しく",
    "what kind of people work here": "どんな人が働いているの",
    "where is kyocera tech hidden in daily life": "日常に隠れている京セラの技術は",
    "what makes the work environment attractive": "働く環境の魅力は",
    "how can i join kyocera": "京セラに入るにはどうすればいい",
    "why did you choose kyocera": "なぜ京セラを選んだの",
    "tell me mira's honest thoughts": "海音みらの本音を聞きたい",
}

# ==========================================
# ヘルパー関数
# ==========================================

def get_qa_by_user_type(user_type='business', language='ja'):
    """
    ユーザータイプと言語に応じたQ&Aデータを返す
    
    Args:
        user_type: 'business' または 'student'
        language: 'ja' または 'en'
    
    Returns:
        dict: 対応するQ&Aデータ
    """
    if language == 'en':
        if user_type == 'student':
            return student_qa_responses_en
        else:
            return business_qa_responses_en
    else:
        if user_type == 'student':
            return student_qa_responses
        else:
            return business_qa_responses

def get_suggestions_by_user_type(user_type='business', language='ja'):
    """
    ユーザータイプと言語に応じたサジェスチョンデータを返す
    
    Args:
        user_type: 'business' または 'student'
        language: 'ja' または 'en'
    
    Returns:
        dict: 対応するサジェスチョンデータ
    """
    if language == 'en':
        if user_type == 'student':
            return student_suggestions_en
        else:
            return business_suggestions_en
    else:
        if user_type == 'student':
            return student_suggestions
        else:
            return business_suggestions

def get_current_phase(selected_count):
    """
    選択されたサジェスチョン数から現在のPhaseを判定
    
    Args:
        selected_count: これまでに選択されたサジェスチョン数
    
    Returns:
        str: 現在のPhase ('phase1_overview', 'phase2_technical', 'phase3_personal')
    """
    if selected_count < 3:  # 0, 1, 2 → Phase1
        return 'phase1_overview'
    elif selected_count < 6:  # 3, 4, 5 → Phase2
        return 'phase2_technical'
    else:  # 6以上 → Phase3
        return 'phase3_personal'

def get_response_for_user(query, user_type='business', phase=None, language='ja'):
    """
    ユーザータイプ・Phase・言語に応じた回答を取得
    
    Args:
        query: ユーザーの質問
        user_type: 'business' または 'student'
        phase: Phaseキー（指定しない場合は全Phase検索）
        language: 'ja' または 'en'
    
    Returns:
        str or None: 回答テキスト
    """
    qa_data = get_qa_by_user_type(user_type, language)
    
    # 質問文を正規化
    query_normalized = query.lower().rstrip('?!？！。').strip()
    
    # 指定Phaseのみ検索
    if phase and phase in qa_data:
        phase_data = qa_data[phase]
        for key, response in phase_data.items():
            key_normalized = key.lower().rstrip('?!？！。').strip()
            if key_normalized == query_normalized or query_normalized in key_normalized:
                return response
    
    # 全Phase検索
    for phase_name, phase_data in qa_data.items():
        for key, response in phase_data.items():
            key_normalized = key.lower().rstrip('?!？！。').strip()
            if key_normalized == query_normalized or query_normalized in key_normalized:
                return response
    
    return None

def get_suggestions_for_phase(phase, selected_suggestions=[], user_type='business', language='ja'):
    """
    Phase別のサジェスチョンを取得（重複排除・多言語対応）
    
    Args:
        phase: Phaseキー
        selected_suggestions: これまでに選択されたサジェスチョンリスト
        user_type: 'business' または 'student'
        language: 'ja' または 'en'
    
    Returns:
        list: サジェスチョンリスト（最大3個）
    """
    import random
    
    suggestions_data = get_suggestions_by_user_type(user_type, language)
    phase_suggestions = suggestions_data.get(phase, [])
    
    # 重複を排除
    selected_lower = {s.lower().strip() for s in selected_suggestions}
    available = [s for s in phase_suggestions if s.lower().strip() not in selected_lower]
    
    # 3個以下の場合はそのまま返す
    if len(available) <= 3:
        return available
    
    # ランダムに3個選択
    return random.sample(available, 3)


# ============================================================================
# 🎯 多言語対応関数（将来拡張用 - 現在は日本語のみ）
# ============================================================================
# 注意: 英語版は将来実装予定

# ====================================================================
# 🎯 メディアデータ（画像・動画）- 将来対応用
# ====================================================================

qa_media_data = {
    # 注意: 疑問符（？）はget_qa_media関数で自動正規化されるため不要
    
    # ビジネス向け & 学生向け共通
    "海音みらって誰": {
        "images": [
            {
                "url": "/static/media/Kyocera/labo.png",
                "caption": "海音みら（AIコンシェルジュ）",
                "alt": "海音みらの画像"
            }
        ]
    },
    
    "京セラってどんな会社": {
        "images": [
            {
                "url": "/static/media/Kyocera/inamori.png",
                "caption": "稲盛和夫",
                "alt": "創業者 稲盛和夫"
            },
            {
                "url": "/static/media/Kyocera/inamori2.png",
                "caption": "稲盛和夫の像",
                "alt": "稲盛和夫の像"
            },
            {
                "url": "/static/media/Kyocera/ceramic.png",
                "caption": "セラミック部品",
                "alt": "京セラのセラミック部品"
            },
            {
                "url": "/static/media/Kyocera/handotai.png",
                "caption": "半導体製品",
                "alt": "京セラの半導体"
            },
            {
                "url": "/static/media/Kyocera/taiyoko.png",
                "caption": "太陽光発電",
                "alt": "京セラの太陽光パネル"
            },
            {
                "url": "/static/media/Kyocera/densibuhin.png",
                "caption": "電子部品",
                "alt": "京セラの電子部品"
            }
        ]
    },
    
    "日常に隠れている京セラの技術は": {
        "images": [
            {
                "url": "/static/media/Kyocera/safaia.png",
                "caption": "サファイアガラス",
                "alt": "サファイアガラス製品"
            },
            {
                "url": "/static/media/Kyocera/renzu.png",
                "caption": "産業用・車載用光学レンズ",
                "alt": "京セラの光学部品"
            }
        ],
        # 🆕 光学部品事業サイトへのリンク
        "link": {
            "text": "光学部品について詳しく見る →",
            "url": "https://www.kyocera.co.jp/prdct/optec/index.html"
        }
    },
    
    # ビジネス向けのみ
    "リサーチセンターはどういう施設": {
        "images": [
            {
                "url": "/static/media/Kyocera/sample.img.png",
                "caption": "リサーチセンター",
                "alt": "京セラリサーチセンター"
            }
        ],
        # 🆕 外部リンク追加
        "link": {
            "text": "オープンイノベーションアリーナ →",
            "url": "https://www.kyocera.co.jp/rd/open-innovation/"
        }
    },
    
    "協業やイベントに参加したい": {
        "videos": [
            {
                "url": "/static/media/Kyocera/isyumv.mp4",
                "thumbnail": "/static/media/thumbnails/isyu.png",
                "caption": "異種格闘技戦の様子",
                "alt": "異種格闘技戦イベントの動画"
            }
        ],
        # 🆕 外部リンク追加
        "link": {
            "text": "イベント情報を見る →",
            "url": "https://www.kyocera.co.jp/rd/open-innovation/events/"
        }
    },
    
    # 🆕 採用サイトへのリンク（学生向け）
    "京セラに入るにはどうすればいい": {
        "link": {
            "text": "京セラ新卒採用サイト →",
            "url": "https://www.kyocera.co.jp/recruit/new/"
        }
    },
    
    # 🆕 ミニ四駆企業対抗選手権の詳細ページ
    "ミニ四駆大会やワークショップに参加したい": {
        "link": {
            "text": "第4回ミニ四駆企業対抗選手権の詳細を見る →",
            "url": "https://www.kyocera.co.jp/rd-openinnovation/news/mini4wd.html"
        }
    }
}

def get_qa_media(question):
    """
    質問に紐付くメディアデータを取得
    
    Args:
        question (str): 質問テキスト
        
    Returns:
        dict or None: メディアデータ、存在しない場合はNone
    """
    if not question or not qa_media_data:
        return None
    
    if question in qa_media_data:
        return qa_media_data[question]
    
    # 正規化して完全一致チェック
    question_normalized = question.replace('?', '').replace('？', '').strip()
    
    for key in qa_media_data.keys():
        key_normalized = key.replace('?', '').replace('？', '').strip()
        if question_normalized == key_normalized:
            return qa_media_data[key]
    
    return None