import glob

PATHS_REQUIRING_HEADER = ["kedro_server", "tests"]
LEGAL_HEADER_FILE = "legal_header.txt"
LICENSE_MD = "LEGAL_NOTICE.md"

RED_COLOR = "\033[0;31m"
NO_COLOR = "\033[0m"

LICENSE = """Copyright (c) 2020 - present
"""


def files_at_path(path: str):
    return glob.glob(path + "/**/*.py", recursive=True)


def files_missing_substring(file_names, substring):
    for file_name in file_names:
        with open(file_name, "r", encoding="utf-8") as current_file:
            content = current_file.read()

            if content.strip() and substring not in content:
                yield file_name


def main():
    exit_code = 0

    with open(LEGAL_HEADER_FILE) as header_f:
        header = header_f.read()

    # find all .py files recursively
    files = [
        new_file for path in PATHS_REQUIRING_HEADER for new_file in files_at_path(path)
    ]

    # find all files which do not contain the header and are non-empty
    files_with_missing_header = list(files_missing_substring(files, header))

    # exit with an error and print all files without header in read, if any
    if files_with_missing_header:
        print(
            RED_COLOR
            + "The legal header is missing from the following files:\n- "
            + "\n- ".join(files_with_missing_header)
            + NO_COLOR
            + "\nPlease add it by copy-pasting the below:\n\n"
            + header
            + "\n"
        )
        exit_code = 1

    # check the LICENSE.md exists and has the right contents
    try:
        files = list(files_missing_substring([LICENSE_MD], LICENSE))
        if files:
            print(
                RED_COLOR
                + "Please make sure the LEGAL_NOTICE.md file "
                + "at the root of the project "
                + "has the right contents."
                + NO_COLOR
            )
            exit(1)
    except IOError:
        print(
            RED_COLOR
            + "Please add the LEGAL_NOTICE.md file at the root of the project "
            "with the appropriate contents." + NO_COLOR
        )
        exit(1)

    # if it doesn't exist, send a notice
    exit(exit_code)


if __name__ == "__main__":
    main()
