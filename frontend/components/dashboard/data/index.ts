export const allMentions = [
  {
    id: 1,
    platform: "tiktok" as const,
    username: "@delivery_fails",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "Cuando Rappi dice 10 minutos pero llevas esperando 45 minutos #rappi #delivery #perú",
    engagement: "245k vistas",
    time: "2h",
    sentiment: "negative" as const,
  },
  {
    id: 2,
    platform: "instagram" as const,
    username: "@foodie_lima",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "Probé el nuevo RappiPrime y vale cada centavo. Envío ilimitado gratis y buenas promociones",
    engagement: "1.2k me gusta",
    time: "3h",
    sentiment: "positive" as const,
  },
  {
    id: 3,
    platform: "youtube" as const,
    username: "Tech Review Peru",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "Comparativa completa: Rappi vs PedidosYa vs DiDi Food - ¿Cuál es mejor en 2024? | Reseña completa",
    engagement: "89k vistas",
    time: "5h",
    sentiment: "neutral" as const,
  },
  {
    id: 4,
    platform: "x" as const,
    username: "@carlosm_pe",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "La app de Rappi cada día va más lenta. ¿Alguien más con problemas? No puedo ni ordenar correctamente.",
    engagement: "342 retuits",
    time: "6h",
    sentiment: "negative" as const,
  },
  {
    id: 5,
    platform: "article" as const,
    username: "El Comercio",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "Rappi anuncia expansión a 5 nuevas ciudades en Perú y promete 2.000 nuevos empleos para repartidores",
    engagement: "Economía",
    time: "8h",
    sentiment: "positive" as const,
  },
  {
    id: 6,
    platform: "facebook" as const,
    username: "Lima Deals",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "CÓDIGO DE DESCUENTO RAPPI: Usa 'SAVE30' para 30% de descuento en tu próximo pedido. ¡Válido hasta mañana!",
    engagement: "2.3k compartidos",
    time: "10h",
    sentiment: "positive" as const,
  },
  {
    id: 7,
    platform: "tiktok" as const,
    username: "@delivery_official",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "Un día normal como repartidor de Rappi en Lima. Vida de repartidor #rappi #trabajo",
    engagement: "567k vistas",
    time: "12h",
    sentiment: "neutral" as const,
  },
  {
    id: 8,
    platform: "instagram" as const,
    username: "@peruvian_restaurant",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "¡Ahora estamos en Rappi! Pide tu ceviche favorito con delivery gratis esta semana. Enlace en la bio",
    engagement: "856 me gusta",
    time: "14h",
    sentiment: "positive" as const,
  },
  {
    id: 9,
    platform: "x" as const,
    username: "@startup_latam",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "Rappi reporta 40% de crecimiento en Perú durante el tercer trimestre. El mercado de delivery sigue expandiéndose en la región.",
    engagement: "189 me gusta",
    time: "16h",
    sentiment: "positive" as const,
  },
  {
    id: 10,
    platform: "youtube" as const,
    username: "3 Pepitos Podcast",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "Ep. 234: Hablamos sobre la guerra de apps de delivery en Perú. Rappi, PedidosYa y nuevos actores",
    engagement: "12k vistas",
    time: "1d",
    sentiment: "neutral" as const,
  },
];

// Paleta de 3 colores: azul, púrpura, esmeralda
export const platformColors = {
  youtube: "text-white bg-blue-500 border-blue-400 shadow-sm",
  tiktok: "text-white bg-purple-500 border-purple-400 shadow-sm",
  instagram: "text-white bg-purple-500 border-purple-400 shadow-sm",
  x: "text-white bg-blue-500 border-blue-400 shadow-sm",
  facebook: "text-white bg-blue-500 border-blue-400 shadow-sm",
  article: "text-white bg-emerald-500 border-emerald-400 shadow-sm",
};

export const sentimentColors = {
  positive: "bg-emerald-50 text-emerald-700 border-emerald-200 shadow-sm",
  negative: "bg-blue-50 text-blue-700 border-blue-200 shadow-sm",
  neutral: "bg-purple-50 text-purple-700 border-purple-200 shadow-sm",
};
