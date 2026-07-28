import streamlit as st
import itertools
import random
from datetime import datetime

st.set_page_config(
    page_title="Aussie Lotto Filter Pro",
    page_icon="🎯",
    layout="centered"
)

# =========================
# LOTTO DATABASE
# =========================

games = {
    "Saturday Lotto": {"pick": 6, "max": 45},
    "Monday & Wednesday Lotto": {"pick": 6, "max": 45},
    "Oz Lotto": {"pick": 7, "max": 47},
    "Powerball": {"pick": 7, "max": 35},
    "Set for Life": {"pick": 5, "max": 44},
    "Lotto Strike": {"pick": 4, "max": 37}
}


# =========================
# NUMBER GROUPS
# =========================

groups = {
    "1-10": range(1, 11),
    "11-19": range(11, 20),
    "20-29": range(20, 30),
    "30-39": range(30, 40),
    "40-49": range(40, 50),
    "50-59": range(50, 60)
}


def get_group(number):

    for name, nums in groups.items():
        if number in nums:
            return name

    return None



# =========================
# FILTERS
# =========================

def has_sequence(ticket):

    nums = sorted(ticket)

    counter = 1

    for i in range(len(nums)-1):

        if nums[i+1] == nums[i] + 1:

            counter += 1

            if counter >= 3:
                return True

        else:
            counter = 1

    return False



def filter_combinations(
        combinations,
        fixed_numbers,
        odd_count,
        golden_sum,
        banned_groups):

    results = []


    for ticket in combinations:


        # fixed numbers

        if fixed_numbers:

            if not all(
                n in ticket
                for n in fixed_numbers
            ):
                continue



        # odd / even

        if odd_count is not None:

            odds = sum(
                1 for n in ticket
                if n % 2 != 0
            )

            if odds != odd_count:
                continue



        # golden sum

        if golden_sum:

            total = sum(ticket)

            if not (
                golden_sum[0]
                <= total
                <= golden_sum[1]
            ):
                continue



        # banned groups

        ticket_groups = set(
            get_group(n)
            for n in ticket
        )


        if any(
            g in ticket_groups
            for g in banned_groups
        ):
            continue



        # remove sequences

        if has_sequence(ticket):
            continue



        results.append(
            list(ticket)
        )


    return results



# =========================
# DISTRIBUTION SELECTOR
# =========================

def choose_best(results, amount):

    if len(results) <= amount:
        return results


    frequency = {}

    for ticket in results:

        for n in ticket:

            frequency[n] = (
                frequency.get(n,0)+1
            )


    scored = []


    for ticket in results:

        score = 0

        for n in ticket:

            score += abs(
                frequency[n]
            )


        scored.append(
            (
                score,
                ticket
            )
        )


    scored.sort(
        key=lambda x:x[0]
    )


    selected=[]


    for score,ticket in scored:

        if len(selected)>=amount:
            break

        selected.append(ticket)


    return selected



# =========================
# INTERFACE
# =========================

st.title(
    "🎯 Aussie Lotto Filter Pro"
)


game = st.selectbox(
    "Choose Lotto Game",
    list(games.keys())
)


pick = games[game]["pick"]


st.info(
    f"{game} needs {pick} numbers"
)



numbers_text = st.text_input(
    "Enter your numbers"
)


user_numbers=[]


if numbers_text:

    try:

        user_numbers = sorted(
            set(
                int(x.strip())
                for x in numbers_text.split(",")
            )
        )

    except:

        st.error(
            "Invalid numbers"
        )



fixed_text = st.text_input(
    "Fixed numbers (optional)"
)


fixed_numbers=[]


if fixed_text:

    fixed_numbers=[
        int(x.strip())
        for x in fixed_text.split(",")
    ]



odd_count = st.selectbox(
    "Required odd numbers",
    [
        None,
        0,1,2,3,4,5,6,7
    ]
)



enable_sum = st.checkbox(
    "Enable Golden Sum"
)


golden_sum=None


if enable_sum:

    minimum = st.number_input(
        "Minimum sum",
        value=50
    )

    maximum = st.number_input(
        "Maximum sum",
        value=250
    )


    golden_sum=(
        minimum,
        maximum
    )



st.subheader(
    "Groups to exclude"
)


banned_groups=[]


for g in groups.keys():

    if st.checkbox(
        f"Exclude {g}",
        key=g
    ):

        banned_groups.append(g)



tickets_number = st.number_input(
    "Number of tickets wanted",
    min_value=1,
    value=50
)



# =========================
# RUN
# =========================

if st.button(
    "🚀 Generate"
):


    if len(user_numbers)<pick:

        st.error(
            "Not enough numbers"
        )


    else:


        all_combinations = list(
            itertools.combinations(
                user_numbers,
                pick
            )
        )


        st.write(
            "Total combinations:",
            len(all_combinations)
        )


        valid = filter_combinations(
            all_combinations,
            fixed_numbers,
            odd_count,
            golden_sum,
            banned_groups
        )


        st.success(
            f"Valid combinations: {len(valid)}"
        )


        selected = choose_best(
            valid,
            int(tickets_number)
        )


        st.info(
            f"Generated: {len(selected)} tickets"
        )


        output=""


        for i,ticket in enumerate(
            selected,
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

            output += line+"\n"



        st.download_button(
            "Download TXT",
            output,
            file_name=
            f"lotto_results_{datetime.now().date()}.txt"
        )
