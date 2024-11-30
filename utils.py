def map_commutator(input_string, mapping):
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
