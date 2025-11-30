"""
Word Lists Module
Contiene listas de palabras para análisis de sentimiento y procesamiento de texto
Author: Mauricio J. @synaw_w
"""

POSITIVE_WORDS = {
    "bueno", "excelente", "genial", "fantástico", "maravilloso", "perfecto", "increíble",
    "amor", "adorar", "encantar", "feliz", "alegre", "satisfecho", "contento",
    "satisfacción", "recomendar", "recomendado", "recomendable", "mejor", "superior",
    "delicioso", "rico", "sabroso", "exquisito", "divino", "espectacular", "magnífico",
    "estupendo", "fabuloso", "sorprendente", "extraordinario", "brillante", "ideal",
    "óptimo", "satisfactorio", "agradable", "placentero", "disfrutar", "volver",
    "gustar", "favorito", "preferido", "destacado", "notable", "sobresaliente",
    "excepcional", "único", "especial", "impresionante", "asombroso", "radiante",
    "espléndido", "luminoso"
}

NEGATIVE_WORDS = {
    "malo", "mala", "malos", "malas", "terrible", "horrible", "pésimo", "pésima",
    "pésimos", "pésimas", "decepcionante", "decepcionantes", "mal", "malísimo",
    "malísima", "malísimos", "malísimas", "asqueroso", "asquerosa", "asquerosos",
    "asquerosas", "repugnante", "repugnantes", "desagradable", "desagradables",
    "odio", "odiar", "odio", "odiamos", "odiarás", "triste", "tristes", "tristeza",
    "deprimido", "deprimida", "deprimidos", "deprimidas", "frustrado", "frustrada",
    "frustrados", "frustradas", "enojado", "enojada", "enojados", "enojadas",
    "molesto", "molesta", "molestos", "molestas", "irritado", "irritada",
    "irritados", "irritadas", "furioso", "furiosa", "furiosos", "furiosas",
    "disgustado", "disgustada", "disgustados", "disgustadas", "descontento",
    "descontenta", "descontentos", "descontentas", "insatisfecho", "insatisfecha",
    "insatisfechos", "insatisfechas", "decepcionado", "decepcionada", "decepcionados",
    "decepcionadas", "desilusionado", "desilusionada", "desilusionados",
    "desilusionadas", "desesperado", "desesperada", "desesperados", "desesperadas",
    "desesperanzado", "desesperanzada", "desesperanzados", "desesperanzadas",
    "desalentado", "desalentada", "desalentados", "desalentadas", "desanimado",
    "desanimada", "desanimados", "desanimadas", "desmotivado", "desmotivada",
    "desmotivados", "desmotivadas", "desalentado", "desalentada", "desalentados",
    "desalentadas", "desilusionado", "desilusionada", "desilusionados",
    "desilusionadas", "decepcionado", "decepcionada", "decepcionados",
    "decepcionadas", "insatisfecho", "insatisfecha", "insatisfechos",
    "insatisfechas", "descontento", "descontenta", "descontentos", "descontentas",
    "molesto", "molesta", "molestos", "molestas", "irritado", "irritada",
    "irritados", "irritadas", "furioso", "furiosa", "furiosos", "furiosas",
    "enojado", "enojada", "enojados", "enojadas", "disgustado", "disgustada",
    "disgustados", "disgustadas", "repugnante", "repugnantes", "asqueroso",
    "asquerosa", "asquerosos", "asquerosas", "desagradable", "desagradables",
    "horrible", "horribles", "terrible", "terribles", "pésimo", "pésima",
    "pésimos", "pésimas", "malo", "mala", "malos", "malas", "mal", "malísimo",
    "malísima", "malísimos", "malísimas", "decepcionante", "decepcionantes",
    "desastroso", "desastrosa", "desastrosos", "desastrosas", "catastrófico",
    "catastrófica", "catastróficos", "catastróficas", "devastador", "devastadora",
    "devastadores", "devastadoras", "destructivo", "destructiva", "destructivos",
    "destructivas", "perjudicial", "perjudiciales", "dañino", "dañina", "dañinos",
    "dañinas", "nocivo", "nociva", "nocivos", "nocivas", "tóxico", "tóxica",
    "tóxicos", "tóxicas", "venenoso", "venenosa", "venenosos", "venenosas",
    "peligroso", "peligrosa", "peligrosos", "peligrosas", "riesgoso", "riesgosa",
    "riesgosos", "riesgosas", "arriesgado", "arriesgada", "arriesgados",
    "arriesgadas", "inseguro", "insegura", "inseguros", "inseguras", "inestable",
    "inestables", "inconstante", "inconstantes", "variable", "variables",
    "impredecible", "impredecibles", "imprevisible", "imprevisibles",
    "inesperado", "inesperada", "inesperados", "inesperadas", "sorpresivo",
    "sorpresiva", "sorpresivos", "sorpresivas", "inesperado", "inesperada",
    "inesperados", "inesperadas", "sorpresivo", "sorpresiva", "sorpresivos",
    "sorpresivas", "inesperado", "inesperada", "inesperados", "inesperadas"
}

SPANISH_STOPWORDS = {
    "el", "la", "de", "que", "y", "a", "en", "un", "ser", "se", "no", "haber",
    "por", "con", "su", "para", "como", "estar", "tener", "le", "lo", "todo",
    "pero", "más", "hacer", "o", "poder", "decir", "este", "ir", "otro", "ese",
    "la", "si", "me", "ya", "ver", "porque", "dar", "cuando", "él", "muy", "sin",
    "vez", "mucho", "saber", "qué", "sobre", "mi", "alguno", "mismo", "yo", "también",
    "hasta", "año", "dos", "querer", "entre", "así", "primero", "desde", "grande",
    "eso", "ni", "nos", "llegar", "pasar", "tiempo", "ella", "sí", "día", "uno",
    "bien", "poco", "deber", "entonces", "poner", "cosa", "tanto", "hombre", "parecer",
    "nuestro", "tan", "donde", "ahora", "parte", "después", "vida", "quedar", "siempre",
    "creer", "hablar", "llevar", "dejar", "nada", "cada", "seguir", "menos", "nuevo",
    "encontrar", "algo", "solo", "mientras", "entrar", "trabajar", "pues", "aunque",
    "salir", "hacer", "también", "cual", "menos", "mismo", "muy", "nunca", "siempre",
    "todo", "todos", "toda", "todas", "cada", "cual", "cuales", "cuando", "donde",
    "como", "porque", "que", "quien", "quienes", "cual", "cuales", "cuanto", "cuanta",
    "cuantos", "cuantas", "este", "esta", "estos", "estas", "ese", "esa", "esos",
    "esas", "aquel", "aquella", "aquellos", "aquellas", "mi", "mis", "tu", "tus",
    "su", "sus", "nuestro", "nuestra", "nuestros", "nuestras", "vuestro", "vuestra",
    "vuestros", "vuestras", "su", "sus", "mío", "mía", "míos", "mías", "tuyo",
    "tuya", "tuyos", "tuyas", "suyo", "suya", "suyos", "suyas", "nuestro", "nuestra",
    "nuestros", "nuestras", "vuestro", "vuestra", "vuestros", "vuestras", "suyo",
    "suya", "suyos", "suyas", "me", "te", "le", "nos", "os", "les", "se", "lo",
    "la", "los", "las", "le", "les", "me", "te", "nos", "os", "se", "mi", "conmigo",
    "ti", "contigo", "sí", "consigo", "mí", "ti", "él", "ella", "ello", "nosotros",
    "nosotras", "vosotros", "vosotras", "ellos", "ellas", "usted", "ustedes"
}

