import streamlit as st
import itertools
from math import comb


st.set_page_config(
    page_title="Aussie Lotto Filter Pro",
    page_icon="🎯",
    layout="centered"
)


# -----------------------------
# Australian Lotto Database
# -----------------------------

games = {
    "Saturday Lotto": {"numbers": 6, "max": 45},
    "Monday & Wednesday Lotto": {"numbers": 6, "max": 45},
    "Tuesday Lotto": {"numbers": 6, "max": 45},
    "Oz Lotto": {"numbers": 7, "max": 47},
    "Powerball": {"numbers": 7, "max": 35},
    "Set for Life": {"numbers": 5, "max": 44},
    "Lotto Strike": {"numbers": 4, "max": 37}
}


# -----------------------------
# Filters
# -----------------------------

def has_sequence(ticket):
    ticket = sorted(ticket)

    count = 1

    for i in range(len(ticket)-1):
        if ticket[i+1] == ticket[i] + 1:
            count += 1
            if count >= 3:
                return True
        else:
            count = 1

    return False



def apply_filters(
        combinations,
        fixed_numbers,
        odd_required,
        sum_range):

    filtered = []

    for ticket in combinations:

        ticket = list(ticket)


        # Fixed numbers
        if fixed_numbers:

            if not all(x in ticket for x in fixed_numbers):
                continue


        # Odd numbers
        if odd_required is not None:

            odd = len(
                [x for x in ticket if x % 2 != 0]
            )

            if odd != odd_required:
                continue


        # Golden Sum

        if sum_range:

            total = sum(ticket)

            if not (
                sum_range[0]
                <= total
                <=
                sum_range[1]
            ):
                continue


        # Remove sequences

        if has_sequence(ticket):
            continue


        filtered.append(ticket)


    return filtered



# -----------------------------
# Interface
# -----------------------------

st.title("🎯 Aussie Lotto Filter Pro")

st.write(
    "Generate lotto combinations using your own numbers and filters."
)


game = st.selectbox(
    "Choose Australian Lotto Game",
    list(games.keys())
)


required_numbers = games[game]["numbers"]


st.info(
    f"This game requires {required_numbers} numbers"
)



# User numbers

numbers_input = st.text_input(
    "Enter your numbers (example: 1,5,10,20,25,30)",
)


user_numbers = []

if numbers_input:

    try:
        user_numbers = sorted(
            list(
                set(
                    int(x.strip())
                    for x in numbers_input.split(",")
                )
            )
        )

    except:

        st.error(
            "Please enter numbers correctly"
        )



# Fixed numbers

fixed_input = st.text_input(
    "Fixed numbers (optional)"
)


fixed_numbers = []

if fixed_input:

    fixed_numbers = [
        int(x.strip())
        for x in fixed_input.split(",")
    ]



# Odd even

odd_required = st.selectbox(
    "Required odd numbers (optional)",
    [
        None,
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7
    ]
)



# Sum filter

enable_sum = st.checkbox(
    "Enable Golden Sum Filter"
)


sum_range = None


if enable_sum:

    min_sum = st.number_input(
        "Minimum total",
        value=60
    )

    max_sum = st.number_input(
        "Maximum total",
        value=220
    )


    sum_range = (
        min_sum,
        max_sum
    )



requested_cards = st.number_input(
    "Requested number of tickets",
    min_value=1,
    value=100
)



# -----------------------------
# Generate
# -----------------------------


if st.button("🚀 Calculate & Generate"):


    if len(user_numbers) < required_numbers:

        st.error(
            "You need more numbers for this game."
        )


    else:

        total_possible = comb(
            len(user_numbers),
            required_numbers
        )


        st.write(
            f"Total combinations before filters: {total_possible}"
        )


        all_combinations = itertools.combinations(
            user_numbers,
            required_numbers
        )


        results = apply_filters(
            all_combinations,
            fixed_numbers,
            odd_required,
            sum_range
        )


        available = len(results)


        st.success(
            f"Available combinations after filters: {available}"
        )


        if available == 0:

            st.warning(
                "No combinations match your filters."
            )


        else:

            final_results = results[
                :min(
                    requested_cards,
                    available
                )
            ]


            output = ""


            st.subheader(
                "Results"
            )


            for i, ticket in enumerate(
                final_results,
                1
            ):

                line = (
                    f"{i}: "
                    +
                    " - ".join(
                        map(str,ticket)
                    )
                )

                st.write(line)

                output += line + "\n"



            st.download_button(
                "💾 Download TXT",
                output,
                file_name="aussie_lotto_results.txt"
            )
