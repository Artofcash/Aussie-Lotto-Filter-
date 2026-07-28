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

def get_group(number):

    if 1 <= number <= 10:
        return "1-10"

    elif 11 <= number <= 19:
        return "11-19"

    elif 20 <= number <= 29:
        return "20-29"

    elif 30 <= number <= 39:
        return "30-39"

    elif 40 <= number <= 49:
        return "40-49"

    else:
        return "50-59"



# =========================
# FILTER FUNCTIONS
# =========================

def has_sequence(ticket):

    nums = sorted(ticket)

    count = 1

    for i in range(len(nums)-1):

        if nums[i+1] == nums[i] + 1:

            count += 1

            if count >= 3:
                return True

        else:
            count = 1

    return False



def missing_group_count(ticket):

    all_groups = set()

    for n in range(1,60):
        all_groups.add(get_group(n))


    ticket_groups = set(
        get_group(n)
        for n in ticket
    )


    return len(
        all_groups - ticket_groups
    )



def apply_filters(
        combinations,
        fixed_numbers,
        odd_count,
        golden_sum,
        allowed_missing_groups):

    results=[]


    for ticket in combinations:


        # Fixed numbers

        if fixed_numbers:

            if not all(
                x in ticket
                for x in fixed_numbers
            ):
                continue



        # Odd / Even

        if odd_count is not None:

            odds=sum(
                1
                for x in ticket
                if x % 2 != 0
            )

            if odds != odd_count:
                continue



        # Golden Sum

        if golden_sum:

            total=sum(ticket)

            if not (
                golden_sum[0]
                <= total
                <= golden_sum[1]
            ):
                continue



        # Number groups filter

        missing = missing_group_count(ticket)

        if missing < allowed_missing_groups:

            continue



        # Remove sequences

        if has_sequence(ticket):

            continue



        results.append(
            list(ticket)
        )


    return results



# =========================
# DISTRIBUTION PICK
# =========================

def choose_distributed(results, amount):

    if len(results) <= amount:

        return results


    random.shuffle(results)


    selected=[]

    used_numbers={}


    for ticket in results:

        if len(selected)>=amount:
            break


        score=sum(
            used_numbers.get(n,0)
            for n in ticket
        )


        if score < 5:

            selected.append(ticket)

            for n in ticket:

                used_numbers[n]=(
                    used_numbers.get(n,0)+1
                )


    if len(selected)<amount:

        for ticket in results:

            if ticket not in selected:

                selected.append(ticket)

            if len(selected)>=amount:
                break


    return selected



# =========================
# USER INTERFACE
# =========================

st.title(
    "🎯 Aussie Lotto Filter Pro"
)


game=st.selectbox(
    "Choose Lotto Game",
    list(games.keys())
)


pick=games[game]["pick"]


st.info(
    f"{game} requires {pick} numbers"
)



numbers_text=st.text_input(
    "Enter your numbers"
)


user_numbers=[]


if numbers_text:

    try:

        user_numbers=sorted(
            set(
                int(x.strip())
                for x in numbers_text.split(",")
            )
        )

    except:

        st.error(
            "Invalid numbers"
        )



fixed_text=st.text_input(
    "Fixed numbers (optional)"
)


fixed_numbers=[]


if fixed_text:

    fixed_numbers=[
        int(x.strip())
        for x in fixed_text.split(",")
    ]



odd_count=st.selectbox(
    "Odd numbers required (optional)",
    [
        None,
        0,1,2,3,4,5,6,7
    ]
)



enable_sum=st.checkbox(
    "Enable Golden Sum Filter"
)


golden_sum=None


if enable_sum:

    minimum=st.number_input(
        "Minimum sum",
        value=50
    )

    maximum=st.number_input(
        "Maximum sum",
        value=250
    )

    golden_sum=(
        minimum,
        maximum
    )



# =========================
# GROUPS FILTER UPDATED
# =========================

st.subheader(
    "Number Groups Filter"
)


allowed_missing_groups=st.selectbox(

    "How many number groups can be missing?",

    [
        0,
        1,
        2,
        3,
        4,
        5
    ]

)


st.caption(
    "0 = all groups must be represented. Higher values allow more missing groups."
)



tickets_number=st.number_input(
    "Number of tickets wanted",
    min_value=1,
    value=50
)



# =========================
# GENERATE
# =========================

if st.button(
    "🚀 Generate"
):


    if len(user_numbers)<pick:

        st.error(
            "Not enough numbers"
        )


    else:


        all_combinations=list(
            itertools.combinations(
                user_numbers,
                pick
            )
        )


        st.write(
            "Total combinations:",
            len(all_combinations)
        )


        valid=apply_filters(
            all_combinations,
            fixed_numbers,
            odd_count,
            golden_sum,
            allowed_missing_groups
        )


        st.success(
            f"Valid combinations: {len(valid)}"
        )


        final=choose_distributed(
            valid,
            int(tickets_number)
        )


        st.info(
            f"Generated tickets: {len(final)}"
        )


        output=""


        for i,ticket in enumerate(
            final,
            1
        ):

            line=(
                f"{i}: "
                +
                " - ".join(
                    map(str,ticket)
                )
            )

            st.write(line)

            output+=line+"\n"



        st.download_button(
            "Download TXT",
            output,
            file_name=
            f"lotto_results_{datetime.now().date()}.txt"
        )
