import re

import pandas as pd


def map_commutator(input_string: str, mapping: dict[str, str]) -> str:
    """
    Maps the elements inside curly brackets using the provided dictionary
    For example
    input_string = "F' {LUF,LDF} F"
    output = "F' (B, T) F"
    """
    # Find the start and end of the curly brackets
    if "{" in input_string and "}" in input_string:
        start = input_string.index("{")
        end = input_string.index("}")

        # Extract the elements inside the curly brackets
        elements = input_string[start + 1:end].split(',')

        # Map each element using `mappy`
        mapped_elements = [mapping.get(elem, elem) for elem in elements]

        # Rebuild the string with the mapped elements
        mapped_part = f"({''.join(mapped_elements)})"
        return input_string[:start] + mapped_part + input_string[end + 1:]
    return input_string  # Return original if no curly brackets found


def remove_cancellations(commutator: str) -> str:
    """
    Turns
        (Can U. RB.) U      into
        U' (RB.) U
    """
    commutator = re.sub(r'\(Can (\w)\.\s*', r"\1' (", commutator)
    commutator = re.sub(r'\(Can (\w)\'\.\s*', r"\1 (", commutator)
    commutator = re.sub(r'\(BR\. Can (\w)\'\.\)', r"(BR.) \1", commutator)
    commutator = re.sub(r'\(BR\. Can (\w)\.\)', r"(BR.) \1'", commutator)

    return commutator


def remove_periods(commutator: str) -> str:
    """
    Turns
        U' (RB.) U.   into
        U' (RB) U
    """
    commutator = commutator.strip()

    if commutator[-1] == ".":
        commutator = commutator[:-1].strip()

    commutator = re.sub(r'\((\w{2})\.\)', r'(\1)', commutator)

    return commutator


def clean_commmutator(commutator: str, verbose: bool = False) -> str:
    fns = [lambda x: x, remove_cancellations, remove_periods]
    for f in fns:
        commutator = f(commutator)

        if verbose:
            print(commutator)

    return commutator


def commutator_to_sticker_commutator(commutator: str, letter2sticker: dict[str, str]) -> str:
    """
    Turns
        U' (RB) U         into
        U' {FR,UB} U
        or similar, depending on the letters_guille dictionary
    """
    try:
        if "(" not in commutator:
            return commutator

        pre, rest = commutator.split("(")
        inside, post = rest.split(")")
        first_letter, second_letter = inside

        first_sticker = letter2sticker[first_letter]
        second_sticker = letter2sticker[second_letter]

        return f"{pre}{{{first_sticker},{second_sticker}}}{post}"
    except:
        return ""


def unravel_commutator_wrt_master(commutator: str, all_comms: pd.DataFrame) -> str:
    """
    Turns
    u' L {LB,LU} Lu    into
    u' L LU'M'UL'U'MU Lu
    Args:
        commutator: str
        all_comms: pd.DataFrame with index ["first_sticker", "second_sticker"]
    """
    if "{" not in commutator:
        return commutator
    else:
        pre, rest = commutator.split("{")
        rest, post = rest.split("}")
        first_sticker, second_sticker = rest.split(",")

        try:
            unraveled = all_comms.loc[first_sticker, second_sticker].iloc[0].iloc[0]
            return pre + unraveled + post
        except:
            return ""
