def find_group_line(lines: str) -> tuple[list, str] | None:
    for line_n, line in enumerate(lines[:5], start=1):
        n_chars = sum(1 for char in "<AtraásEdit+>" if char in line)
        if n_chars > 5:
            return lines[line_n:], line
    else:
        for line_n, line in enumerate(lines[:5], start=1):
            n_chars = sum(1 for char in "<listasEdit+>" if char in line)
            if n_chars > 5:
                return lines[line_n:], line


def extract_group_name(group_line):
    try:
        # Atrás
        _, post = group_line.split("ás ")
        
    except:
        # Mis listas
        _, post = group_line.split("stas ")

    group, _ = post.split(" Ed")
    
    return group


def keep_relevant_lines(lines):
    # those with ":" and 2 letters at begining and sth at the end
    lines_rel = []
    for line in lines:
        if ":" not in line:
            continue
        pre, post = line.split(":")
        if len(pre) != 2:
            continue
        if len(post) < 3:
            continue

        lines_rel.append(line)

    return lines_rel

def extract_commutator_from_line(lines):
    comms = []
    
    for line in lines:
        pre, post = line.split(":")
        _commutator = post.strip()
        commutator = treat_commutator_string(_commutator)
        
        comm = {
            "first_letter": pre[0],
            "second_letter": pre[1],
            "commutator": commutator,
        }
    
        comms.append(comm)

    return comms


def treat_commutator_string(commutator: str) -> str:
    """
    Treat the string to remove errors from pytesseract OCR"
    """
    commutator = commutator.replace("6%)", "")
    commutator = commutator.replace("6)", "")
    commutator = commutator.replace("É)", "")
    commutator = commutator.replace("$)", "")
    commutator = commutator.replace("€)", "")
    commutator = commutator.replace("Ó", "")
    commutator = commutator.replace("0", "")
    commutator = commutator.replace("$", "")
    
    commutator = commutator.replace('"', "'")
    commutator = commutator.replace('”', "'")
    commutator = commutator.replace("?", "'")
    commutator = commutator.replace("!", "'")

    commutator = commutator.replace(",", ".")

    commutator = commutator.replace("12", "l2")

    commutator = commutator.strip()

    return commutator

    