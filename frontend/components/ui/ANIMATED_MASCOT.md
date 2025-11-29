# AnimatedMascot component

Este componente muestra una mascota animada hecha en SVG y CSS. Es una criatura genérica (no es un Pokémon) para evitar problemas de derechos de autor, pero el componente está diseñado para que puedas usar tu propia imagen / sprite (por ejemplo: un sprite de Pokémon que tengas derecho a usar).

Mejoras recientes
- La animación ahora es continua y más rápida (flotación más viva).
- Añadidos: parpadeo automático, movimiento de cola, twitch de orejas, movimiento de boca y sombra pulsante para dar más vida.

El resultado es un ciclo animado siempre activo (respetando `prefers-reduced-motion`).
- Si tienes una imagen con sprites (p. ej. un pequeño walker/idle frame set), sube el archivo a `public/mi-mascota-sprite.png` y crea una versión de CSS que haga `background-position` para animar el sprite.
- Alternativamente, puedo adaptar este componente para aceptar una ruta a un sprite y animarlo automáticamente.

Si quieres que el comportamiento sea aún más "anime-style" (más frames, efectos de iluminación, expresión facial dinámica), puedo:

- Adaptar el componente para usar una hoja de sprites y manejar ciclos de animación (idle, blink, walk) y/o
- Añadir animaciones adicionales por JavaScript para sincronizar timing y efectos (p. ej. brillo en ojos cuando el usuario pasa el cursor).

Uso del SVG del repositorio
- Si colocaste `pikachu.svg` en `frontend/svs/pikachu.svg`, ya lo copié a `frontend/public/pikachu.svg` y el componente ahora lo carga desde `/pikachu.svg`.
- El resultado es una animación continua (flotación, balanceo, destellos eléctricos) aplicada al archivo SVG que proporcionaste — si quieres animaciones internas (cola/orejas/ojos en concreto) necesitaría que confirmes si quieres que modifique el SVG internamente (o me des permiso para usar/alterar ese asset).

Recuerda: si vas a usar un personaje con derechos de autor (por ejemplo un Pokémon), asegúrate de que tienes permiso para distribuir ese asset. Yo puedo integrar tu sprite mientras me confirmes que está bien usarlo.

Cómo usar un sprite personalizado (opcional)
- Si tienes una imagen con sprites (p. ej. un pequeño walker/idle frame set), sube el archivo a `public/mi-mascota-sprite.png` y crea una versión de CSS que haga `background-position` para animar el sprite.
- Alternativamente, puedo adaptar este componente para aceptar una ruta a un sprite y animarlo automáticamente.

Notas importantes
- Evita subir o distribuir material con derechos de autor si no tienes permiso.
- Si quieres que usemos una figura concreta (p. ej. un Pokémon), indícame cuál es y confirma que tienes o quieres usar sprites libres o que tienes permiso; puedo adaptar el componente para reproducir un ciclo de caminata/idle.
