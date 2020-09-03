#!/usr/bin/env python3
import os
import re
import subprocess
import sys
import tempfile


def build_doxygen_config(warning_log_filename, user_config_filename="Doxyfile"):
    config_options = {
        "WARN_LOGFILE": warning_log_filename,
        "GENERATE_HTML": "NO",
        "GENERATE_XML": "NO",
        "GENERATE_LATEX": "NO",
    }

    user_config = ""

    if os.path.exists(user_config_filename):
        with open(user_config_filename, "r") as fp:
            user_config = fp.read()

    return user_config + "\n".join(
        ["=".join(option) for option in config_options.items()]
    )


def filter_doxygen_messages(filenames, messages):
    # Filter only the files we are interested in
    interesting_messages = [
        msg.strip()
        for msg in messages
        if any((os.path.samefile(msg.partition(":")[0], f) for f in filenames))
    ]

    # Filter some common false positives
    filters = [re.compile("documented symbol '.*' was not declared or defined")]
    return [
        msg for msg in interesting_messages if not any((f.search(msg) for f in filters))
    ]


def main(filenames):
    with tempfile.TemporaryDirectory() as temp_dir:
        warn_log_filename = os.path.join(temp_dir, "warn_log.txt")
        config = build_doxygen_config(warn_log_filename)
        try:
            subprocess.run(
                ["doxygen", "-"],
                input=config.encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            print("Unable to call doxygen:", str(e))
            return 1

        with open(warn_log_filename, "r") as log_fp:
            warnings = filter_doxygen_messages(filenames, log_fp.readlines())

        if warnings != []:
            print("\n".join(warnings))
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
