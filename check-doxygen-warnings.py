#!/usr/bin/env python3
import tempfile
import os
import re
import sys
import subprocess

def build_doxygen_config(input_filename, warning_log_filename, user_config_filename="Doxyfile"):
    config_options = {
        "INPUT": input_filename,
        "WARN_LOGFILE": warning_log_filename,
        "GENERATE_HTML": "NO",
        "GENERATE_XML": "NO",
        "GENERATE_LATEX": "NO"
    }

    user_config = ""

    if os.path.exists(user_config_filename):
        with open(user_config_filename, "r") as fp:
            user_config = fp.read()


    return user_config + "\n".join(["=".join(option) for option in config_options.items()])


def filter_doxygen_messages(messages):
    filters = [
        re.compile("documented symbol '.*' was not declared or defined")
    ]
    return [msg for msg in messages if not any((f.search(msg) for f in filters))]

def main(filename):
    with tempfile.TemporaryDirectory() as temp_dir:
        warn_log_filename = os.path.join(temp_dir, "warn_log.txt")
        config = build_doxygen_config(filename, warn_log_filename)
        try:
            ret = subprocess.run(["doxygen", "-"], input=config.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print("Unable to call doxygen")
            return 0

        with open(warn_log_filename, "r") as log_fp:
            warnings = filter_doxygen_messages(log_fp.readlines())

        if warnings != []:
            print("Doxygen check failed for " + filename)
            print("".join(warnings))
            return 1

    return 0



if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
