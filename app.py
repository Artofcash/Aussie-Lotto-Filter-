import streamlit as st
import itertools
import random
from datetime import datetime

st.set_page_config(
    page_title="Aussie Lotto Filter Pro",
    page_icon="🎯",
    layout="centered"
)

# ==========================
# Games
# ==========================

games = {
    "Saturday Lotto": {"pick": 6, "max": 45},
    "Monday & Wednesday Lotto": {"pick": 6, "max": 45},
    "Oz Lotto": {"pick": 7, "max": 47},
    "Powerball": {"pick": 7, "max": 35},
    "Set for Life": {"pick": 5, "max": 44},
    "Lotto Strike": {"pick": 4, "max": 37}
}


# ==========================
# Functions
# ==========================

def number_group(n):
    if 1 <= n <= 10:
        return "1-10"
    elif 11 <= n <= 19:
        return "11-19"
    elif 20 <= n <= 29:
        return "20-29"
    elif 30 <= n <= 39:
        return "30-39"
    elif 40 <= n <= 49:
        return "40-49"
    else:
        return "50+"


def has_sequence(nums):
    nums = sorted(nums)
    count = 1

    for i in range(len(nums)-1):
        if nums[i+1] == nums[i] + 1:
            count += 1
            if count >= 3:
                return True
        else:
            count = 1

    return False


def apply_filters(
        combos,
        fixed,
        odd_required,
        golden_sum,
        groups_removed):

    output = []

    for ticket in combos:

        ticket = list(ticket)

        if fixed:
            if not all(x in ticket for x in fixed):
                continue


        if odd_required is not None:
            odd = len([x for x in ticket if x % 2])
            if odd != odd_required:
                continue


        if golden_sum:
            total = sum(ticket)

            if not (
                golden_sum[0]
                <= total
                <= golden_sum[1]
            ):
                continue


        groups = set(
            number_group(x)
            for x in ticket
        )

        all_groups = {
            number_group(x)
            for x in range(1,60)
        }

        missing = len(all_groups - groups)

        if missing > groups_removed:
            continue


        if has_sequence(ticket):
            continue


        output.append(ticket)

    return output



def score_tickets(tickets):

    frequency = {}

    for t in tickets:
        for n in t:
            frequency[n] = frequency.get(n,0)+1


    scored = []

    for t in tickets:

        score = 0

        for n in t:
            score += abs(
                frequency[n]
            )

        groups = len(
            set(number_group(x) for x in t)
        )

        score += groups * 5

        scored.append(
            (score,t)
        )


    scored.sort(
        reverse=True
    )

    return [
        x[1]
        for x in scored
    ]



# ==========================
# Interface
# ==========================

st.title("🎯 Aussie Lotto Filter Pro")


game = st.selectbox(
    "Choose Lotto Game",
    list(games.keys())
)

needed = games[game]["pick"]

st.info(
    f"{game}: choose {needed} numbers per ticket"
)


numbers_text = st.text_input(
    "Enter your numbers",
    placeholder="1,5,10,15,22,30"
)

user_numbers=[]

if numbers_text:
    try:
        user_numbers = sorted(
            list(
                set(
                    int(x.strip())
                    for x in numbers_text.split(",")
                )
            )
        )
    except:
        st.error("Wrong format")



fixed_text = st.text_input(
    "Fixed numbers (optional)"
)

fixed=[]

if fixed_text:
    fixed=[
        int(x.strip())
        for x in fixed_text.split(",")
    ]



odd_required = st.selectbox(
    "Odd numbers required (optional)",
    [
        None,0,1,2,3,4,5,6,7
    ]
)



enable_sum = st.checkbox(
    "Golden Sum Filter"
)

golden_sum=None

if enable_sum:

    a=st.number_input(
        "Minimum sum",
        value=60
    )

    b=st.number_input(
        "Maximum sum",
        value=220
    )

    golden_sum=(a,b)



groups_removed = st.selectbox(
    "How many number groups can be missing?",
    [0,1,2,3]
)


amount = st.number_input(
    "Number of tickets wanted",
    min_value=1,
    value=50
)



if st.button("🚀 Generate"):

    if len(user_numbers)<needed:

        st.error(
            "Not enough numbers"
        )

    else:

        all_combos=list(
            itertools.combinations(
                user_numbers,
                needed
            )
        )


        st.write(
            "Total combinations:",
            len(all_combos)
        )


        filtered=apply_filters(
            all_combos,
            fixed,
            odd_required,
            golden_sum,
            groups_removed
        )


        st.write(
            "After filters:",
            len(filtered)
        )


        if filtered:

            ranked=score_tickets(
                filtered
            )


            final=ranked[
                :min(
                    amount,
                    len(ranked)
                )
            ]


            result=""

            st.subheader(
                "Results"
            )


            for i,t in enumerate(final,1):

                line=f"{i}: {' - '.join(map(str,t))}"

                st.write(line)

                result+=line+"\n"


            st.download_button(
                "Download TXT",
                result,
                file_name=
                f"lotto_{datetime.now().date()}.txt"
            )

        else:

            st.warning(
                "No combinations found"
            )
