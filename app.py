import json
import random
from pathlib import Path

import streamlit as st


# ============================================================
# CONFIGURACIÓN
# ============================================================

ARCHIVO_JSON = Path(__file__).with_name(
    "banco_preguntas_ayudante_servicios_400.json"
)

NOMBRE_BLOQUE = "Ayudante de Servicios"

TEMAS = {
    7: "Tema 7 - La cocina hospitalaria centralizada",
    8: "Tema 8 - Las materias primas",
    9: "Tema 9 - Los alimentos y las dietas",
    10: "Tema 10 - Acciones con alimentos. Limpieza de la vajilla",
    11: "Tema 11 - Normas higiénico-sanitarias de aplicación",
    12: "Tema 12 - La contaminación de los alimentos",
    13: "Tema 13 - Seguridad e higiene en el trabajo",
    14: "Tema 14 - Protección medioambiental",
    15: "Tema 15 - El servicio de ropa y lencería",
    16: "Tema 16 - La ropa limpia hospitalaria",
}

NUM_PREGUNTAS_DEFECTO = 10


# ============================================================
# CARGAR EL BANCO DE PREGUNTAS
# ============================================================

@st.cache_data
def cargar_preguntas(fecha_json):

    if not ARCHIVO_JSON.exists():
        return [], (
            f"No se encuentra el archivo: "
            f"{ARCHIVO_JSON.name}"
        )

    try:
        with open(
            ARCHIVO_JSON,
            "r",
            encoding="utf-8"
        ) as f:
            datos = json.load(f)

    except json.JSONDecodeError as e:
        return [], f"El JSON no es válido: {e}"

    except Exception as e:
        return [], f"No se pudo leer el JSON: {e}"

    preguntas = (
        datos.get("preguntas", [])
        if isinstance(datos, dict)
        else datos
    )

    if not isinstance(preguntas, list):
        return [], (
            "El JSON no contiene una lista "
            "válida de preguntas."
        )

    resultado = []

    for pregunta in preguntas:

        if not isinstance(pregunta, dict):
            continue

        tema = (
            int(pregunta.get("tema", 0))
            if str(
                pregunta.get("tema", "")
            ).isdigit()
            else 0
        )

        opciones = pregunta.get(
            "opciones",
            {}
        )

        correcta = str(
            pregunta.get(
                "respuesta_correcta",
                ""
            )
        ).upper().strip()

        if (
            not pregunta.get("pregunta")
            or not isinstance(opciones, dict)
            or correcta not in {
                "A",
                "B",
                "C",
                "D",
            }
            or correcta not in opciones
            or tema not in TEMAS
        ):
            continue

        resultado.append(
            {
                "id": pregunta.get("id"),
                "tema": tema,
                "pregunta": str(
                    pregunta["pregunta"]
                ).strip(),
                "opciones": {
                    "A": str(
                        opciones.get("A", "")
                    ).strip(),
                    "B": str(
                        opciones.get("B", "")
                    ).strip(),
                    "C": str(
                        opciones.get("C", "")
                    ).strip(),
                    "D": str(
                        opciones.get("D", "")
                    ).strip(),
                },
                "respuesta_correcta": correcta,
            }
        )

    return resultado, None


# ============================================================
# CARGAR LAS PREGUNTAS
# ============================================================

fecha_json = (
    ARCHIVO_JSON.stat().st_mtime_ns
    if ARCHIVO_JSON.exists()
    else 0
)

preguntas, error_carga = cargar_preguntas(
    fecha_json
)


# ============================================================
# ESTADO DE LA APLICACIÓN
# ============================================================

def inicializar_estado():

    valores = {

        # La pantalla inicial será Teoría
        "modo": "Teoría",

        "preguntas_test": [],

        "respuestas": {},

        "test_activo": False,

        "test_finalizado": False,

        "temas_seleccionados": [],

        "cantidad_preguntas":
            NUM_PREGUNTAS_DEFECTO,

        "preguntas_utilizadas": set(),

        "tipo_test": "teoria",
    }

    for clave, valor in valores.items():

        if clave not in st.session_state:
            st.session_state[clave] = valor


inicializar_estado()


# ============================================================
# REINICIAR TEST
# ============================================================

def reiniciar_test():

    st.session_state[
        "preguntas_test"
    ] = []

    st.session_state[
        "respuestas"
    ] = {}

    st.session_state[
        "test_activo"
    ] = False

    st.session_state[
        "test_finalizado"
    ] = False

    st.session_state[
        "temas_seleccionados"
    ] = []

    st.session_state[
        "cantidad_preguntas"
    ] = NUM_PREGUNTAS_DEFECTO

    st.session_state[
        "preguntas_utilizadas"
    ] = set()


# ============================================================
# COMENZAR TEST
# ============================================================

def comenzar_test(
    preguntas_disponibles,
    cantidad,
    excluir_utilizadas=True
):

    if not preguntas_disponibles:

        st.error(
            "No hay preguntas para "
            "la selección realizada."
        )

        return

    if excluir_utilizadas:

        utilizadas = st.session_state.get(
            "preguntas_utilizadas",
            set()
        )

        pendientes = [
            p
            for p in preguntas_disponibles
            if p.get("id") not in utilizadas
        ]

    else:

        pendientes = list(
            preguntas_disponibles
        )

    if not pendientes:

        st.warning(
            "Ya has utilizado todas las "
            "preguntas disponibles para "
            "los temas seleccionados."
        )

        return

    cantidad = min(
        cantidad,
        len(pendientes)
    )

    seleccion = random.sample(
        pendientes,
        cantidad
    )

    st.session_state[
        "preguntas_test"
    ] = seleccion

    st.session_state[
        "respuestas"
    ] = {}

    st.session_state[
        "test_activo"
    ] = True

    st.session_state[
        "test_finalizado"
    ] = False


# ============================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================

st.set_page_config(
    page_title=(
        "Preguntas Test - "
        "Ayudante de Servicios"
    ),
    page_icon="📚",
    layout="wide",
)


# ============================================================
# CABECERA
# ============================================================

st.title(
    "📚 Oposiciones: Ayudante de Servicios "
    "— Tests bloque específico"
)


# ============================================================
# ERROR DE CARGA
# ============================================================

if error_carga:

    st.error(error_carga)

    st.info(
        "Comprueba que el archivo "
        f"`{ARCHIVO_JSON.name}` "
        "está en la misma carpeta que "
        "`app.py`."
    )

    st.stop()


# ============================================================
# BARRA LATERAL
# ============================================================

with st.sidebar:

    st.header("Opciones")

    modo = st.radio(
        "Vista",
        [
            "Teoría",
            "Práctica"
        ],
        index=[
            "Teoría",
            "Práctica"
        ].index(
            st.session_state["modo"]
        ),
    )

    if (
        modo != st.session_state["modo"]
        and st.session_state["test_activo"]
    ):
        reiniciar_test()

    st.session_state["modo"] = modo

    st.divider()

    st.metric(
        "Preguntas disponibles",
        len(preguntas)
    )

    temas_presentes = sorted(
        {
            p["tema"]
            for p in preguntas
        }
    )

    st.metric(
        "Temas disponibles",
        len(temas_presentes)
    )

    st.divider()

    if st.button(
        "🔄 Reiniciar test",
        use_container_width=True
    ):

        reiniciar_test()

        # Al reiniciar volvemos siempre a Teoría
        st.session_state["modo"] = "Teoría"

        st.rerun()


# ============================================================
# FUNCIÓN: MOSTRAR TEST ACTIVO
# ============================================================

def mostrar_test():

    st.header("📝 Test")

    preguntas_test = (
        st.session_state[
            "preguntas_test"
        ]
    )

    respuestas = (
        st.session_state[
            "respuestas"
        ]
    )

    st.write(
        f"Preguntas: "
        f"**{len(preguntas_test)}**"
    )

    for indice, pregunta in enumerate(
        preguntas_test,
        start=1
    ):

        st.markdown("---")

        st.markdown(
            f"### Pregunta {indice} "
            f"de {len(preguntas_test)}"
        )

        st.write(
            f"**{pregunta['pregunta']}**"
        )

        respuesta = st.radio(

            "Selecciona una respuesta:",

            options=[
                "A",
                "B",
                "C",
                "D"
            ],

            format_func=(
                lambda letra,
                p=pregunta:
                f"{letra}) "
                f"{p['opciones'][letra]}"
            ),

            key=(
                f"respuesta_"
                f"{pregunta['id']}_"
                f"{indice}"
            ),

            index=None,
        )

        respuestas[indice] = respuesta


    # ========================================================
    # FINALIZAR Y CORREGIR
    # ========================================================

    st.markdown("---")

    if not st.session_state[
        "test_finalizado"
    ]:

        if st.button(
            "✅ Finalizar y corregir",
            type="primary",
            use_container_width=True
        ):

            st.session_state[
                "test_finalizado"
            ] = True

            st.rerun()


    # ========================================================
    # RESULTADO
    # ========================================================

    if st.session_state[
        "test_finalizado"
    ]:

        aciertos = 0
        contestadas = 0

        for indice, pregunta in enumerate(
            preguntas_test,
            start=1
        ):

            respuesta = respuestas.get(
                indice
            )

            if respuesta:
                contestadas += 1

            if (
                respuesta
                == pregunta[
                    "respuesta_correcta"
                ]
            ):
                aciertos += 1


        fallos = (
            contestadas
            - aciertos
        )

        sin_contestar = (
            len(preguntas_test)
            - contestadas
        )

        porcentaje = (
            (
                aciertos
                / len(preguntas_test)
            )
            * 100
            if preguntas_test
            else 0
        )


        st.markdown(
            "## 📊 Resultado"
        )

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        col1.metric(
            "Aciertos",
            aciertos
        )

        col2.metric(
            "Fallos",
            fallos
        )

        col3.metric(
            "Sin contestar",
            sin_contestar
        )

        col4.metric(
            "Nota",
            f"{porcentaje:.1f}%"
        )


        # ====================================================
        # CORRECCIÓN
        # ====================================================

        st.markdown("---")

        st.subheader(
            "🔎 Corrección"
        )

        for indice, pregunta in enumerate(
            preguntas_test,
            start=1
        ):

            respuesta = respuestas.get(
                indice
            )

            correcta = pregunta[
                "respuesta_correcta"
            ]

            if respuesta == correcta:

                icono = "✅"

            elif respuesta is None:

                icono = "⚪"

            else:

                icono = "❌"


            st.markdown(
                f"**{icono} Pregunta "
                f"{indice}: "
                f"{pregunta['pregunta']}**"
            )


            if respuesta:

                st.write(
                    f"Tu respuesta: "
                    f"**{respuesta}** — "
                    f"{pregunta['opciones'][respuesta]}"
                )

            else:

                st.write(
                    "Sin contestar."
                )


            st.write(
                f"Respuesta correcta: "
                f"**{correcta}** — "
                f"{pregunta['opciones'][correcta]}"
            )


        # ====================================================
        # OPCIONES DESPUÉS DEL TEST
        # ====================================================

        st.markdown("---")

        st.markdown(
            "### ¿Qué quieres hacer ahora?"
        )

        col1, col2 = st.columns(2)


        # ====================================================
        # OTRO TEST CON LOS MISMOS TEMAS
        # ====================================================

        with col1:

            if st.button(
                "🔄 Otro test con los mismos temas",
                type="primary",
                use_container_width=True
            ):

                temas_guardados = (
                    st.session_state[
                        "temas_seleccionados"
                    ]
                )

                cantidad_guardada = (
                    st.session_state[
                        "cantidad_preguntas"
                    ]
                )

                disponibles_mismos_temas = [
                    p
                    for p in preguntas
                    if p["tema"]
                    in temas_guardados
                ]

                utilizadas = (
                    st.session_state[
                        "preguntas_utilizadas"
                    ]
                )

                pendientes = [
                    p
                    for p in disponibles_mismos_temas
                    if p.get("id")
                    not in utilizadas
                ]


                if not pendientes:

                    st.warning(
                        "🎉 Ya has hecho todas "
                        "las preguntas disponibles "
                        "de los temas seleccionados."
                    )

                else:

                    cantidad_siguiente = min(
                        cantidad_guardada,
                        len(pendientes)
                    )

                    comenzar_test(
                        disponibles_mismos_temas,
                        cantidad_siguiente,
                        excluir_utilizadas=True
                    )

                    if st.session_state[
                        "preguntas_test"
                    ]:

                        st.session_state[
                            "preguntas_utilizadas"
                        ].update(

                            p.get("id")

                            for p
                            in st.session_state[
                                "preguntas_test"
                            ]
                        )

                    st.rerun()


        # ====================================================
        # VOLVER AL INICIO
        # ====================================================

        with col2:

            if st.button(
                "🏠 Volver al inicio",
                use_container_width=True
            ):

                reiniciar_test()

                # La pantalla de inicio
                # es siempre Teoría.
                st.session_state[
                    "modo"
                ] = "Teoría"

                st.rerun()


# ============================================================
# VISTA: TEORÍA
# ============================================================

if st.session_state[
    "modo"
] == "Teoría":


    # Si hay un test activo,
    # mostramos las preguntas.

    if st.session_state[
        "test_activo"
    ]:

        mostrar_test()

        st.stop()


    # --------------------------------------------------------
    # PANTALLA PRINCIPAL DE TEORÍA
    # --------------------------------------------------------

    st.header(
        "📖 Parte Teórica"
    )

    st.write(
        "Selecciona un tema para "
        "hacer un test exclusivamente "
        "con sus preguntas."
    )


    # --------------------------------------------------------
    # TEMAS
    # --------------------------------------------------------

    for numero_tema, nombre_tema in (
        TEMAS.items()
    ):

        cantidad_tema = sum(

            1

            for p in preguntas

            if p["tema"]
            == numero_tema
        )


        with st.container(
            border=True
        ):

            st.markdown(
                f"### {nombre_tema}"
            )

            st.write(
                "Preguntas disponibles: "
                f"**{cantidad_tema}**"
            )


            cantidad_teoria = (
                st.number_input(

                    "Número de preguntas",

                    min_value=1,

                    max_value=max(
                        1,
                        cantidad_tema
                    ),

                    value=min(
                        NUM_PREGUNTAS_DEFECTO,
                        cantidad_tema
                    ),

                    step=1,

                    key=(
                        f"cantidad_teoria_"
                        f"{numero_tema}"
                    ),
                )
            )


            if st.button(

                "▶️ Hacer test de este tema",

                type="primary",

                use_container_width=True,

                key=(
                    f"test_teoria_"
                    f"{numero_tema}"
                ),
            ):

                disponibles_tema = [

                    p

                    for p in preguntas

                    if p["tema"]
                    == numero_tema
                ]


                st.session_state[
                    "temas_seleccionados"
                ] = [
                    numero_tema
                ]


                st.session_state[
                    "cantidad_preguntas"
                ] = int(
                    cantidad_teoria
                )


                st.session_state[
                    "preguntas_utilizadas"
                ] = set()


                st.session_state[
                    "tipo_test"
                ] = "teoria"


                comenzar_test(

                    disponibles_tema,

                    int(
                        cantidad_teoria
                    ),

                    excluir_utilizadas=False
                )


                if st.session_state[
                    "preguntas_test"
                ]:

                    st.session_state[
                        "preguntas_utilizadas"
                    ].update(

                        p.get("id")

                        for p
                        in st.session_state[
                            "preguntas_test"
                        ]
                    )


                st.rerun()


    st.stop()


# ============================================================
# VISTA: PRÁCTICA
# ============================================================

if st.session_state[
    "modo"
] == "Práctica":


    if not st.session_state[
        "test_activo"
    ]:

        st.header(
            "🛠️ Parte Práctica"
        )

        st.write(
            "Selecciona uno o varios "
            "temas y genera un "
            "test aleatorio."
        )

        st.write(
            "Selecciona los temas "
            "que quieras incluir "
            "en el test:"
        )


        temas_seleccionados = []


        with st.container(
            border=True
        ):

            for numero_tema, nombre_tema in (
                TEMAS.items()
            ):

                seleccionado = st.checkbox(

                    nombre_tema,

                    key=(
                        f"tema_practica_"
                        f"{numero_tema}"
                    ),
                )


                if seleccionado:

                    temas_seleccionados.append(
                        numero_tema
                    )


        disponibles = [

            p

            for p in preguntas

            if p["tema"]
            in temas_seleccionados
        ]


        st.info(

            f"Hay **{len(disponibles)} "
            "preguntas** disponibles "
            "para tu selección."
        )


        if disponibles:

            cantidad = (
                st.number_input(

                    "Número de preguntas",

                    min_value=1,

                    max_value=len(
                        disponibles
                    ),

                    value=min(
                        NUM_PREGUNTAS_DEFECTO,
                        len(disponibles)
                    ),

                    step=1,
                )
            )

        else:

            st.number_input(

                "Número de preguntas",

                min_value=1,

                max_value=1,

                value=1,

                step=1,

                disabled=True,
            )

            cantidad = 1


        if st.button(

            "▶️ Comenzar test",

            type="primary",

            use_container_width=True,

            disabled=not disponibles,
        ):

            st.session_state[
                "temas_seleccionados"
            ] = list(
                temas_seleccionados
            )


            st.session_state[
                "tipo_test"
            ] = "practica"


            st.session_state[
                "cantidad_preguntas"
            ] = int(
                cantidad
            )


            st.session_state[
                "preguntas_utilizadas"
            ] = set()


            comenzar_test(

                disponibles,

                int(
                    cantidad
                ),

                excluir_utilizadas=False
            )


            if st.session_state[
                "preguntas_test"
            ]:

                st.session_state[
                    "preguntas_utilizadas"
                ].update(

                    p.get("id")

                    for p
                    in st.session_state[
                        "preguntas_test"
                    ]
                )


            st.rerun()


    if st.session_state[
        "test_activo"
    ]:

        mostrar_test()