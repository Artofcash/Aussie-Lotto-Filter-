import streamlit as st
import random
from io import StringIO

st.set_page_config(
    page_title="Aussie Lotto Filter Pro",
    page_icon="🎯",
    layout="centered"
)

# -----------------------------
# Lotto Games Database
# -----------------------------

games = {
    "Saturday Lotto": {"main": 6, "max": 45},
    "Monday & Wednesday Lotto": {"main": 6, "max": 45},
    "Tuesday Lotto": {"main": 6, "max": 45},
    "Oz Lotto": {"main": 7, "max": 47},
    "Powerball": {"main": 7, "max": 35, "powerball": True},
    "Set for Life": {"main": 5, "max": 44, "bonus": True},
    "Lotto Strike": {"main": 4, "max": 37}
}


# -----------------------------
# Functions
# -----------------------------

def has_sequence(numbers):
    numbers = sorted(numbers)

    count = 1

    for i in range(len(numbers)-1):
        if numbers[i+1] == numbers[i] + 1:
            count += 1
            if count >= 3:
                return True
        else:
            count = 1

    return False


def generate_ticket(game, fixed, odd_even, total_range):

    amount = games[game]["main"]
    maximum = games[game]["max"]

    while True:

        ticket = set(fixed)

        while len(ticket) < amount:
            ticket.add(random.randint(1, maximum))

        ticket = sorted(list(ticket))

        # odd/even filter
        if odd_even:

            odd = len([x for x in ticket if x % 2])

            if odd != odd_even:
                continue


        # total sum filter
        if total_range:

            total = sum(ticket)

            if not (total_range[0] <= total <= total_range[1]):
                continue


        # remove sequences
        if has_sequence(ticket):
            continue


        return ticket



# -----------------------------
# Interface
# -----------------------------

st.title("🎯 Aussie Lotto Filter Pro")

st.write(
    "Professional lottery number filtering tool"
)


game = st.selectbox(
    "Choose Lotto Game",
    list(games.keys())
)


st.subheader("Your Numbers")

user_numbers = st.text_input(
    "Enter your numbers separated by commas (optional)",
    placeholder="Example: 5,12,18"
)


fixed_numbers = []

if user_numbers:

    try:
        fixed_numbers = [
            int(x.strip())
            for x in user_numbers.split(",")
        ]

    except:
        st.error("Invalid numbers")


st.subheader("Fixed Strong Numbers (Optional)")

strong_numbers = st.text_input(
    "Numbers to keep in every ticket",
    placeholder="Example: 7,21"
)


fixed = []

if strong_numbers:

    fixed = [
        int(x.strip())
        for x in strong_numbers.split(",")
    ]


st.subheader("Odd / Even Filter")

odd_even = st.selectbox(
    "Number of odd numbers required",
    [
        None,
        1,
        2,
        3,
        4,
        5
    ]
)


st.subheader("Golden Sum Filter")

use_sum = st.checkbox(
    "Enable total sum filter"
)


total_range = None

if use_sum:

    minimum = st.number_input(
        "Minimum total",
        min_value=1,
        value=50
    )

    maximum = st.number_input(
        "Maximum total",
        min_value=1,
        value=200
    )

    total_range = (
        minimum,
        maximum
    )


cards = st.number_input(
    "Number of tickets",
    min_value=1,
    max_value=10000,
    value=10
)


if st.button("🚀 Generate Results"):

    results = []

    for i in range(cards):

        ticket = generate_ticket(
            game,
            fixed,
            odd_even,
            total_range
        )

        results.append(ticket)


    st.success(
        f"{len(results)} tickets generated"
    )


    output = ""

    for index, ticket in enumerate(results,1):

        line = (
            f"{index}: "
            +
            " - ".join(
                map(str,ticket)
            )
        )

        output += line + "\n"

        st.write(line)


    st.download_button(
        label="💾 Download TXT",
        data=output,
        file_name="lotto_results.txt",
        mime="text/plain"
    )
