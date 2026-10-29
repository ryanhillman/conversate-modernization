export const LESSONS = [
  {
    id: 1,
    slug: "avere-essere",
    answerLang: "it",
    menuTitle: "<it>Avere</it> and <it>Essere</it>",
    title: "<i><it>Avere</it></i> and <i><it>Essere</it></i>",
    sections: [
      { t: "h", level: 1, size: 3, html: "To have and to be" },
      {
        t: "p",
        html: "Two of the most important verbs in the Italian language are <strong><it>avere</it></strong> (to have) and <strong><it>essere</it></strong> (to be). Both are extremely common in everyday use, and they also support many other verbs and tenses throughout the language.",
      },
      { t: "h", level: 2, size: 4, html: "<it>Avere</it>" },
      {
        t: "conj",
        rows: [
          ["io", "ho", "I have"],
          ["tu", "hai", "You have"],
          ["lui/lei", "ha", "He or she has"],
          ["noi", "abbiamo", "We have"],
          ["voi", "avete", "You all have"],
          ["loro", "hanno", "They have"],
        ],
      },
      { t: "h", level: 3, size: 5, html: "Example uses" },
      {
        t: "ul",
        items: [
          '"<it>Ho un gatto.</it>" → I have a cat.',
          '"<it>Hai un ombrello.</it>" → You have an umbrella.',
          '"<it>Lei ha due fratelli.</it>" → She has two brothers.',
          '"<it>Abbiamo pesce per cena stasera.</it>" → We have fish for dinner tonight.',
          '"<it>Avete una casa grande.</it>" → You all have a big house.',
          '"<it>Loro hanno troppo cibo!</it>" → They have too much food!',
        ],
      },
      {
        t: "p",
        html: "It's worth becoming familiar with <it>avere</it>, because it not only shows possession or ownership but also acts as an auxiliary verb for many other verbs and tenses — so learning it early is a fundamental step toward mastering the language.",
      },
      { t: "h", level: 2, size: 4, html: "<it>Essere</it>" },
      {
        t: "conj",
        rows: [
          ["io", "sono", "I am"],
          ["tu", "sei", "You are"],
          ["lui/lei", "è", "He or she is"],
          ["noi", "siamo", "We are"],
          ["voi", "siete", "You all are"],
          ["loro", "sono", "They are"],
        ],
      },
      { t: "h", level: 3, size: 5, html: "Example uses" },
      {
        t: "ul",
        items: [
          '"<it>Sono uno studente.</it>" → I am a student.',
          '"<it>Sei in ritardo.</it>" → You are late.',
          '"<it>È una bella giornata.</it>" → It is a beautiful day.',
          '"<it>Siamo in montagna.</it>" → We are in the mountains.',
          '"<it>Siete ragazzi alti.</it>" → You are tall kids.',
          '"<it>Loro sono molto gentili.</it>" → They are very kind.',
        ],
      },
      {
        t: "p",
        html: "It's also worth getting comfortable with <it>essere</it>: like <it>avere</it>, it serves as an auxiliary verb for many tenses and verbs, so mastering it early is another fundamental step toward mastering the Italian language.",
      },
    ],
    questions: [
      { id: "lesson-1-question-1", prompt: "We have", correctAnswers: ["abbiamo"] },
      { id: "lesson-1-question-2", prompt: "They are", correctAnswers: ["sono"] },
      { id: "lesson-1-question-3", prompt: "I have", correctAnswers: ["ho"] },
      { id: "lesson-1-question-4", prompt: "You are", correctAnswers: ["sei"] },
      { id: "lesson-1-question-5", prompt: "You all have", correctAnswers: ["avete"] },
      { id: "lesson-1-question-6", prompt: "They have", correctAnswers: ["hanno"] },
    ],
  },
  {
    id: 2,
    slug: "basic-greetings",
    answerLang: "en",
    menuTitle: "Basic greetings",
    title: "Basic greetings",
    sections: [
      { t: "h", level: 1, size: 3, html: "<it>Ciao!</it>" },
      {
        t: "p",
        html: 'One of the most important phrases — and one you may already use — is "<it>ciao</it>". In Italian, <it>ciao</it> can mean both hello and goodbye, and it\'s typically used in informal settings.',
      },
      { t: "p", html: "Some different ways to use <it>ciao</it>:" },
      {
        t: "ul",
        items: ['"<it>Ciao bella</it>" → Hello beautiful', '"<it>Ciao ciao!</it>" → Bye-bye!'],
      },
      {
        t: "p",
        html: "In order to avoid being repetitive, it's important to learn more than just one way to say hello.",
      },
      { t: "h", level: 2, size: 4, html: "Common greetings" },
      {
        t: "ul",
        items: [
          "<it>Buongiorno!</it> → Good morning (typically only used before noon)",
          "<it>Buon pomeriggio!</it> → Good afternoon (typically used from noon to around 3 in the afternoon)",
          "<it>Buona sera!</it> → Good evening (typically used after 4 or 5 in the afternoon)",
          "<it>Salve!</it> → Similar to <it>ciao</it>, but <it>salve</it> is the formal use.",
        ],
      },
      { t: "h", level: 3, size: 5, html: "Greeting examples" },
      {
        t: "ul",
        items: [
          '"<it>Buongiorno, come stai oggi?</it>" → Good morning! How are you today?',
          '"<it>Buon pomeriggio, ragazzi!</it>" → Good afternoon, kids!',
          '"<it>Buonasera, signor Valentino!</it>" → Good evening, Mr. Valentino.',
          '"<it>Ciao, come va?</it>" → Hi, how\'s it going?',
        ],
      },
      {
        t: "p",
        html: "Greeting someone is one of the first things you do when visiting another country, so it helps to know more than one way to do it and keep your greetings from feeling repetitive.",
      },
    ],
    questions: [
      {
        id: "lesson-2-question-1",
        prompt: "<it>Ciao</it>",
        correctAnswers: ["hi", "hello", "hey", "goodbye", "bye"],
      },
      {
        id: "lesson-2-question-2",
        prompt: "<it>Buona sera</it>",
        correctAnswers: ["good evening"],
      },
      {
        id: "lesson-2-question-3",
        prompt: "<it>Buon pomeriggio</it>",
        correctAnswers: ["good afternoon"],
      },
      {
        id: "lesson-2-question-4",
        prompt: "<it>Buongiorno</it>",
        correctAnswers: ["good morning"],
      },
    ],
  },
  {
    id: 3,
    slug: "essere-versus-stare",
    answerLang: "it",
    menuTitle: "<it>Essere</it> versus <it>Stare</it>",
    title: "<i><it>Essere</it> vs. <it>Stare</it></i>",
    sections: [
      { t: "h", level: 1, size: 3, html: "<it>Stare</it> (to be)" },
      {
        t: "p",
        html: "<it>Stare</it> is close to <it>essere</it> in literal meaning, but the two are used quite differently depending on the situation.",
      },
      {
        t: "h",
        level: 2,
        size: 5,
        html: "Let's begin by talking about the differences between the two verbs",
      },
      {
        t: "p",
        html: "Use <i><it>essere</it></i> for identity and description: who or what someone or something is — nationality, profession, physical traits — as well as where people and things are located. Use <i><it>stare</it></i> for how someone is feeling or doing (health), for staying or remaining somewhere, and in a handful of fixed idiomatic expressions you simply memorize.",
      },
      {
        t: "ul",
        items: [
          'When expressing your nationality: "<it>Ciao, sono Paolo e sono tedesco</it>" → Hi, I\'m Paolo and I am German.',
          'Identifying one\'s profession: "<it>Sono un avvocato!</it>" → I am a lawyer!',
          'Describing one\'s physical appearance: "<it>Sono basso e grasso</it>" → I am short and fat.',
          'Describing and locating objects: "<it>Dov\'è lo zucchero?</it>" → Where is the sugar?',
        ],
      },
      {
        t: "p",
        html: "First, let's learn to conjugate the verb <i><it>stare</it></i> so that we can see how it is used.",
      },
      {
        t: "conj",
        rows: [
          ["io", "sto", "I am"],
          ["tu", "stai", "You are"],
          ["lui/lei", "sta", "He or she is"],
          ["noi", "stiamo", "We are"],
          ["voi", "state", "You all are"],
          ["loro", "stanno", "They are"],
        ],
      },
      {
        t: "p",
        html: "In contrast to <i><it>essere</it></i>, <it>stare</it> generally deals with transient states or temporary feelings. Below are some examples of when to use <i><it>stare</it></i> instead of <i><it>essere</it></i>.",
      },
      {
        t: "ul",
        items: [
          '<it>Stare</it> can be used to express remaining in place: "<it>Oggi sto a casa.</it>" → Today I stay home.',
          '<it>Stare</it> can be used to express one\'s health: "<it>Come stai?</it>" → How are you feeling?',
          '<it>Stare</it> is used when speaking about someone\'s appearance: "<it>Questa maglia mi sta benissimo.</it>" → This shirt looks great on me.',
        ],
      },
      {
        t: "p",
        html: "<it>Stare</it> also has many different idiomatic expressions that it is used with. These require memorization as there is no easy rule set to remember them by.",
      },
      {
        t: "ul",
        items: [
          "<it>Stare in piedi</it> → to be standing",
          "<it>Stare attento</it> → to pay attention",
          "<it>Stare con...</it> → to be in a relationship with...",
          "<it>Stare a cuore</it> → to matter to someone",
        ],
      },
    ],
    practiceInstructions:
      "Let's see if you can recognize which verb to use where: choose <i><it>stare</it></i> or <i><it>essere</it></i>.",
    questions: [
      {
        id: "lesson-3-question-1",
        prompt: "<it>Oggi, (sto/sono) bene!</it>",
        correctAnswers: ["sto"],
      },
      {
        id: "lesson-3-question-2",
        prompt: "<it>Noi (siamo/stiamo) americani.</it>",
        correctAnswers: ["siamo"],
      },
      {
        id: "lesson-3-question-3",
        prompt: "<it>Quanto (sei/stai) alto?</it>",
        correctAnswers: ["sei"],
      },
      {
        id: "lesson-3-question-4",
        prompt: "<it>Come (sei/stai)?</it>",
        correctAnswers: ["stai"],
      },
      {
        id: "lesson-3-question-5",
        prompt: "<it>(Sto/Sono) attento in classe.</it>",
        correctAnswers: ["sto"],
      },
      {
        id: "lesson-3-question-6",
        prompt: "<it>Dove (siamo/stiamo) adesso?</it>",
        correctAnswers: ["siamo"],
      },
    ],
  },
  {
    id: 4,
    slug: "regular-are-verbs",
    answerLang: "it",
    menuTitle: "Conjugating regular <it>-are</it> verbs",
    title: "Conjugating regular <it>-are</it> verbs",
    sections: [
      {
        t: "p",
        html: "When conjugating verbs that end in <it>-are</it>, most verbs fall into a set pattern that can be repeated in order to correctly conjugate each verb in each different tense. There are irregular verbs that do not follow these rules, but they are rare and must be memorized; we will address those in a future lesson.",
      },
      {
        t: "p",
        html: "The first step is to drop the <it>-are</it> ending and replace it with the following endings, depending on which person the verb requires.",
      },
      {
        t: "ul",
        items: [
          "<it>-o</it>",
          "<it>-i</it>",
          "<it>-a</it>",
          "<it>-iamo</it>",
          "<it>-ate</it>",
          "<it>-ano</it>",
        ],
      },
      {
        t: "h",
        level: 1,
        size: 5,
        html: "Let's begin by looking at the verb <i><it>parlare</it></i>, which means to speak",
      },
      {
        t: "conj",
        rows: [
          ["io", "parlo", "I speak"],
          ["tu", "parli", "You speak"],
          ["lui/lei", "parla", "He or she speaks"],
          ["noi", "parliamo", "We speak"],
          ["voi", "parlate", "You all speak"],
          ["loro", "parlano", "They speak"],
        ],
      },
      {
        t: "p",
        html: "Now let's look at another <it>-are</it> ending verb, <i><it>mangiare</it></i>, so that we can have another example of how the endings of <it>-are</it> verbs are changed depending on the usage.",
      },
      {
        t: "conj",
        rows: [
          ["io", "mangio", "I eat"],
          ["tu", "mangi", "You eat"],
          ["lui/lei", "mangia", "He or she eats"],
          ["noi", "mangiamo", "We eat"],
          ["voi", "mangiate", "You all eat"],
          ["loro", "mangiano", "They eat"],
        ],
      },
    ],
    practiceInstructions: "Fill in the correct form of the verb.",
    questions: [
      {
        id: "lesson-4-question-1",
        prompt: "I buy (<it>comprare</it>)",
        correctAnswers: ["compro"],
      },
      {
        id: "lesson-4-question-2",
        prompt: "We buy (<it>comprare</it>)",
        correctAnswers: ["compriamo"],
      },
      {
        id: "lesson-4-question-3",
        prompt: "You walk (<it>camminare</it>)",
        correctAnswers: ["cammini"],
      },
      {
        id: "lesson-4-question-4",
        prompt: "They walk (<it>camminare</it>)",
        correctAnswers: ["camminano"],
      },
      {
        id: "lesson-4-question-5",
        prompt: "You all eat (<it>mangiare</it>)",
        correctAnswers: ["mangiate"],
      },
      {
        id: "lesson-4-question-6",
        prompt: "I speak (<it>parlare</it>)",
        correctAnswers: ["parlo"],
      },
      {
        id: "lesson-4-question-7",
        prompt: "You swim (<it>nuotare</it>)",
        correctAnswers: ["nuoti"],
      },
      {
        id: "lesson-4-question-8",
        prompt: "She swims (<it>nuotare</it>)",
        correctAnswers: ["nuota"],
      },
    ],
  },
  {
    id: 5,
    slug: "regular-ere-verbs",
    answerLang: "it",
    menuTitle: "Conjugating regular <it>-ere</it> verbs",
    title: "Conjugating regular <it>-ere</it> verbs",
    sections: [
      {
        t: "p",
        html: "Similar to <it>-are</it> ending verbs, there are many regular <it>-ere</it> ending verbs that follow a set pattern that will allow you to conjugate any regular <it>-ere</it> verb depending on the situation.",
      },
      {
        t: "p",
        html: "The first step, same as <it>-are</it> verbs, is to drop the <it>-ere</it> ending and replace it with the following endings, depending on which person the verb is in.",
      },
      {
        t: "ul",
        items: [
          "<it>-o</it>",
          "<it>-i</it>",
          "<it>-e</it>",
          "<it>-iamo</it>",
          "<it>-ete</it>",
          "<it>-ono</it>",
        ],
      },
      {
        t: "p",
        html: "First, let's practice with the verb <i><it>credere</it></i>, meaning to believe, so that we can see how it looks in action.",
      },
      {
        t: "conj",
        rows: [
          ["io", "credo", "I believe"],
          ["tu", "credi", "You believe"],
          ["lui/lei", "crede", "He or she believes"],
          ["noi", "crediamo", "We believe"],
          ["voi", "credete", "You all believe"],
          ["loro", "credono", "They believe"],
        ],
      },
    ],
    practiceInstructions: "Fill in the correct form of the verb.",
    questions: [
      {
        id: "lesson-5-question-1",
        prompt: "I believe (<it>credere</it>)",
        correctAnswers: ["credo"],
      },
      {
        id: "lesson-5-question-2",
        prompt: "We believe (<it>credere</it>)",
        correctAnswers: ["crediamo"],
      },
      {
        id: "lesson-5-question-3",
        prompt: "They ask (<it>chiedere</it>)",
        correctAnswers: ["chiedono"],
      },
      {
        id: "lesson-5-question-4",
        prompt: "I ask (<it>chiedere</it>)",
        correctAnswers: ["chiedo"],
      },
    ],
  },
  {
    id: 6,
    slug: "regular-ire-verbs",
    answerLang: "it",
    menuTitle: "Conjugating regular <it>-ire</it> verbs",
    title: "Conjugating regular <it>-ire</it> verbs",
    sections: [
      {
        t: "p",
        html: "Like the other two verb groups in Italian, most <it>-ire</it> verbs follow a predictable pattern, so let's look at how their endings are formed.",
      },
      {
        t: "ul",
        items: [
          "<it>-o</it>",
          "<it>-i</it>",
          "<it>-e</it>",
          "<it>-iamo</it>",
          "<it>-ite</it>",
          "<it>-ono</it>",
        ],
      },
      {
        t: "p",
        html: "First, let's practice with the verb <i><it>dormire</it></i>, meaning to sleep, so that we can see how it looks in action.",
      },
      {
        t: "conj",
        rows: [
          ["io", "dormo", "I sleep"],
          ["tu", "dormi", "You sleep"],
          ["lui/lei", "dorme", "He or she sleeps"],
          ["noi", "dormiamo", "We sleep"],
          ["voi", "dormite", "You all sleep"],
          ["loro", "dormono", "They sleep"],
        ],
      },
      {
        t: "p",
        html: "Many other <it>-ire</it> verbs, like <i><it>capire</it></i> (to understand), follow a second regular pattern: they add <it>-isc-</it> before the ending in every form but <it>noi</it> and <it>voi</it>.",
      },
      {
        t: "conj",
        rows: [
          ["io", "capisco", "I understand"],
          ["tu", "capisci", "You understand"],
          ["lui/lei", "capisce", "He or she understands"],
          ["noi", "capiamo", "We understand"],
          ["voi", "capite", "You all understand"],
          ["loro", "capiscono", "They understand"],
        ],
      },
      {
        t: "p",
        html: "As you can see, in the <it>io</it> form we drop the ending and add '<it>isco</it>'; in the <it>tu</it> form we drop the ending and add '<it>isci</it>'; while in the third person singular form we drop the ending and add '<it>isce</it>'. The <it>noi</it>/<it>voi</it> forms follow the usual pattern, and in the third person plural form we again drop the ending and add a new ending of '<it>iscono</it>'.",
      },
    ],
    practiceInstructions: "Fill in the correct form of the verb.",
    questions: [
      {
        id: "lesson-6-question-1",
        prompt: "I sleep (<it>dormire</it>)",
        correctAnswers: ["dormo"],
      },
      {
        id: "lesson-6-question-2",
        prompt: "We feel (<it>sentire</it>)",
        correctAnswers: ["sentiamo"],
      },
      {
        id: "lesson-6-question-3",
        prompt: "They sleep (<it>dormire</it>)",
        correctAnswers: ["dormono"],
      },
      { id: "lesson-6-question-4", prompt: "I hear (<it>sentire</it>)", correctAnswers: ["sento"] },
      {
        id: "lesson-6-question-5",
        prompt: "I understand (<it>capire</it>)",
        correctAnswers: ["capisco"],
      },
      {
        id: "lesson-6-question-6",
        prompt: "She understands (<it>capire</it>)",
        correctAnswers: ["capisce"],
      },
    ],
  },
  {
    id: 7,
    slug: "irregular-verbs",
    answerLang: "it",
    menuTitle: "Conjugating irregular verbs",
    title: "Conjugating irregular verbs",
    sections: [
      {
        t: "p",
        html: "Beyond the verb groups covered so far lies another group whose patterns differ from the rest — these are known as irregular verbs. There are often noticeable patterns to help you, but most simply require memorization.",
      },
      {
        t: "p",
        html: "Now let's look at two verbs almost as common as <i><it>essere</it></i> and <i><it>stare</it></i>: <i><it>fare</it></i>, meaning to do or make, and <i><it>andare</it></i>, meaning to go. Both are irregular, with their own conjugation rules, so they take some memorization to master.",
      },
      { t: "h", level: 1, size: 5, html: "Let's begin by taking a look at <i><it>andare</it></i>" },
      {
        t: "conj",
        rows: [
          ["io", "vado", "I go"],
          ["tu", "vai", "You go"],
          ["lui/lei", "va", "He or she goes"],
          ["noi", "andiamo", "We go"],
          ["voi", "andate", "You all go"],
          ["loro", "vanno", "They go"],
        ],
      },
      { t: "h", level: 1, size: 5, html: "Now let's take a look at <i><it>fare</it></i>" },
      {
        t: "conj",
        rows: [
          ["io", "faccio", "I do"],
          ["tu", "fai", "You do"],
          ["lui/lei", "fa", "He or she does"],
          ["noi", "facciamo", "We do"],
          ["voi", "fate", "You all do"],
          ["loro", "fanno", "They do"],
        ],
      },
      {
        t: "p",
        html: "As these two common irregular verbs show, there isn't a simple pattern to fall back on, so for verbs like these it's best to memorize their forms.",
      },
    ],
    practiceInstructions: "Fill in the correct form of the verb.",
    questions: [
      {
        id: "lesson-7-question-1",
        prompt: "We do/make (<it>fare</it>)",
        correctAnswers: ["facciamo"],
      },
      { id: "lesson-7-question-2", prompt: "They go (<it>andare</it>)", correctAnswers: ["vanno"] },
      { id: "lesson-7-question-3", prompt: "We go (<it>andare</it>)", correctAnswers: ["andiamo"] },
      { id: "lesson-7-question-4", prompt: "I make (<it>fare</it>)", correctAnswers: ["faccio"] },
    ],
  },
  {
    id: 8,
    slug: "pronouns",
    menuTitle: "Italian pronouns",
    title: "Italian pronouns",
    sections: [
      {
        t: "p",
        html: "Italian subject pronouns identify who is performing an action. Let's take a look at the full set.",
      },
      {
        t: "ul",
        items: [
          "First person singular: <it>io</it> → I",
          "Second person singular: <it>tu</it> → you",
          "Third person singular masculine: <it>lui</it> → he",
          "Third person singular feminine: <it>lei</it> → she",
          "First person plural: <it>noi</it> → we",
          "Second person plural: <it>voi</it> → you all",
          "Third person plural: <it>loro</it> → they",
        ],
      },
      {
        t: "p",
        html: "In the third person singular there are two forms, one masculine and one feminine. Gender is an important concept in Italian — every noun is either masculine or feminine, which affects how the words around it behave. We'll cover this in more detail in a future lesson; for now, it's enough to know that a noun carries one of the two genders.",
      },
      {
        t: "p",
        html: "An interesting feature of Italian pronouns is that when the subject is understood, you can usually drop the pronoun entirely — it's mainly kept for emphasis, or to add clarity when the subject would otherwise be ambiguous.",
      },
      {
        t: "p",
        html: "One other thing to note is that <strong><it>Lei</it></strong> (capitalized) — the third person singular feminine form — can stand in for the second person singular (<it>tu</it>) when speaking to someone formally, as a sign of respect. This applies regardless of whether you're addressing a man or a woman; <it>lui</it> is never used this way.",
      },
      {
        t: "p",
        html: "There isn't much to practice in this lesson — it's simply important to know what the Italian pronouns are and where they're used, so you have a strong foundation to build on.",
      },
    ],
    questions: [],
  },
  {
    id: 9,
    slug: "direct-object-pronouns",
    answerLang: "it",
    menuTitle: "Italian direct object pronouns",
    title: "Italian direct object pronouns",
    sections: [
      { t: "p", html: "First, what is a direct object pronoun?" },
      {
        t: "p",
        html: "A direct object pronoun stands in for the noun that directly receives the action — a person, place, or thing.",
      },
      {
        t: "h",
        level: 1,
        size: 5,
        html: "Let's begin by taking a look at the Italian direct object pronouns",
      },
      {
        t: "ul",
        items: [
          "First person singular: <it>mi</it> → me",
          "Second person singular: <it>ti</it> → you",
          "Third person singular masculine: <it>lo</it> → him/it",
          "Third person singular feminine: <it>la</it> → her/it",
          "First person plural: <it>ci</it> → us",
          "Second person plural: <it>vi</it> → you all",
          "Third person plural masculine: <it>li</it> → them",
          "Third person plural feminine: <it>le</it> → them",
        ],
      },
      {
        t: "p",
        html: "As with the pronouns we saw earlier, the third person singular has two forms — one masculine and one feminine. Keep the difference in mind, since it matters in later lessons.",
      },
      {
        t: "h",
        level: 1,
        size: 5,
        html: "Now let's look at a couple of examples of direct object pronouns in action, so we can see how they work!",
      },
      {
        t: "ul",
        items: [
          "<it>Federico legge il libro. → Federico lo legge.</it> <i>(Federico reads the book. → Federico reads it.)</i>",
          "<it>Margherita beve il vino. → Margherita lo beve.</it> <i>(Margherita drinks the wine. → Margherita drinks it.)</i>",
          "<it>Paolo mangia il pane. → Paolo lo mangia.</it> <i>(Paolo eats the bread. → Paolo eats it.)</i>",
        ],
      },
    ],
    practiceInstructions:
      "Type the correct direct object pronoun that replaces the object noun in the sentence.",
    questions: [
      {
        id: "lesson-9-question-1",
        prompt: "<it>Io mangio la pizza. → Io __ mangio.</it>",
        correctAnswers: ["la"],
      },
      {
        id: "lesson-9-question-2",
        prompt: "<it>Tu leggi il libro. → Tu __ leggi.</it>",
        correctAnswers: ["lo"],
      },
      {
        id: "lesson-9-question-3",
        prompt: "<it>Noi vediamo i ragazzi. → Noi __ vediamo.</it>",
        correctAnswers: ["li"],
      },
    ],
  },
  {
    id: 10,
    slug: "indirect-object-pronouns",
    answerLang: "it",
    menuTitle: "Italian indirect object pronouns",
    title: "Italian indirect object pronouns",
    sections: [
      { t: "p", html: "First, what is an indirect object pronoun?" },
      {
        t: "p",
        html: "An indirect object pronoun is used to indicate to whom or to what an action is directed.",
      },
      {
        t: "h",
        level: 1,
        size: 5,
        html: "Let's begin by taking a look at the Italian indirect object pronouns",
      },
      {
        t: "ul",
        items: [
          "First person singular: <it>mi</it> → to me",
          "Second person singular: <it>ti</it> → to you",
          "Third person singular masculine: <it>gli</it> → to him",
          "Third person singular feminine: <it>le</it> → to her",
          "First person plural: <it>ci</it> → to us",
          "Second person plural: <it>vi</it> → to you all",
          "Third person plural: <it>gli</it> (or <it>loro</it>) → to them",
        ],
      },
      {
        t: "p",
        html: 'The easiest way to think about indirect object pronouns is to ask "to whom?" or "to what?" the action is directed.',
      },
      {
        t: "h",
        level: 1,
        size: 5,
        html: "Now let's look at a couple of examples of indirect object pronouns in action, so we can see how they work!",
      },
      {
        t: "ul",
        items: [
          "<it>Io parlo a Marco. → Io gli parlo.</it> <i>(I speak to Marco. → I speak to him.)</i>",
          "<it>Lei scrive a Maria. → Lei le scrive.</it> <i>(She writes to Maria. → She writes to her.)</i>",
          "<it>Noi diamo il libro a loro. → Noi gli diamo il libro.</it> <i>(We give the book to them. → We give them the book.)</i>",
        ],
      },
    ],
    practiceInstructions:
      'Type the correct indirect object pronoun that replaces the indirect object (the "to whom") in the sentence.',
    questions: [
      {
        id: "lesson-10-question-1",
        prompt: "<it>Io parlo a Marco. → Io __ parlo.</it>",
        correctAnswers: ["gli"],
      },
      {
        id: "lesson-10-question-2",
        prompt: "<it>Tu scrivi a Maria. → Tu __ scrivi.</it>",
        correctAnswers: ["le"],
      },
      {
        id: "lesson-10-question-3",
        prompt: "<it>Lui telefona a me. → Lui __ telefona.</it>",
        correctAnswers: ["mi"],
      },
      {
        id: "lesson-10-question-4",
        prompt: "<it>Loro danno il regalo a noi. → Loro __ danno il regalo.</it>",
        correctAnswers: ["ci"],
      },
    ],
  },
];
