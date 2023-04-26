import requests

resp = requests.get("https://zenodo.org/api/records/4590232").json()

new_link = resp["links"]["doi"]
new_doi = resp["metadata"]["doi"]
new_date = resp["metadata"]["publication_date"]
new_title = resp["metadata"]["title"]

citation = f"""Citation
--------
If you use this library and want to cite it, please cite it as:

Mika Pflüger, Annika Günther, Johannes Gütschow, and Robert Gieseke. ({new_date}).
{new_title}.
Zenodo. {new_link}
"""

with open("README.rst") as fd:
    old_content = fd.read().splitlines(keepends=True)

with open("README.rst", "w") as fd:
    skip_to_next_section = False
    i = 0
    while True:
        try:
            line = old_content[i]
        except IndexError:
            break
        if line == "Citation\n":
            fd.write(citation)
            skip_to_next_section = True
            i += 2
        elif skip_to_next_section:
            if line.startswith("---"):
                fd.write("\n")
                fd.write(old_content[i - 1])
                fd.write(line)
                skip_to_next_section = False
            i += 1
        else:
            fd.write(line)
            i += 1

    fd.truncate()
