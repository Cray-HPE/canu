# Purpose
Data driven generation of cabling documentation from standards

# Usage
```./cabling.py > generated/cabling.md```

# Files
* cabling.yaml - cabling standards file (likely should be moved to CANU repo)
* cabling.md.j2 - Jinja2 template creating markdown from the cabling.yaml
* cabling.py - loads the cabling standardsa yaml and renders it with Jinja2

# Administration
`cabling.yaml` supplies the data, `cabling.md.j2` formats the data and `cabling.py` executes these actions.

Each `cabling.yaml` must specify a hardware type and software version.
* **hardware_type**: (required scalar) One-word (lower case) description of the system hardware type.  Examples:  hpe, gigabyte.
* **version**: (required) Shasta software release version.  Dotted decimal version (no alpha characters) description of the software version the cabling standard is developed for.  Examples:  1.4, 1.5.2 .

To add a new node or modify an existing:
1. Edit cabling.yaml to add a new node type with the following elements:
    * **type**: (required scalar) One-word descripion (lower case) of the node type.  Examples:  ncn, mountain, etc...
    * **subtype**: (required scalar) One-word description (lower case) of the node subtype: Examples, storage, cmm, etc...
    * **devices**: (required list) One-word description (lower case) of the device type:  Examples: ocp, pcie, cmm, etc...  Requires the following sub-elements:
        * **ports**: (required).  Should use an anchored expansion from definitions where possible. Otherwise provides a key for a list of ports which have the following elements:
            * **destination_description**: (required) Text description of where the device port goes to.
            * **destination_use**: (required) Text description of what network(s) or service the link provides.
    * **notes**: (optional list) A list of text descriptions referring to the node, device or port. 
2. Render the document:  ```./cabling.py > generated/test.md```
3. View and confirm the document looks ok.
4. In general no changes to the `cabling.md.j2` should be required, but if you are going to modify this file remember that it effects all other devices and nodes.

TODO: Better description of the port definition anchors for reuse.