"""
File: provenance.py

Description: Provenance object for the project
Author(s): Raaid Arshad and Michael Clawar

Notes: Can be used as a global provenance object, or for a single script
"""

from prov.model import ProvDocument

from mjclawar_rarshad.reference import dir_info
from mjclawar_rarshad.reference import mcra_structures as mcras
from mjclawar_rarshad.tools.database_helpers import DatabaseHelper


class ProjectProvenance:
    def __init__(self, database_helper):
        assert isinstance(database_helper, DatabaseHelper)

        self.database_helper = database_helper
        self.prov_doc = ProvDocument()
        self.prov_doc.add_namespace(mcras.BDP_NAMESPACE.name, mcras.BDP_NAMESPACE.link)
        self.prov_doc.add_namespace(mcras.ALG_NAMESPACE.name, mcras.ALG_NAMESPACE.link)
        self.prov_doc.add_namespace(mcras.DAT_NAMESPACE.name, mcras.DAT_NAMESPACE.link)
        self.prov_doc.add_namespace(mcras.LOG_NAMESPACE.name, mcras.LOG_NAMESPACE.link)
        self.prov_doc.add_namespace(mcras.ONT_NAMESPACE.name, mcras.ONT_NAMESPACE.link)

    def write_provenance_json(self):
        self.prov_doc.serialize(dir_info.provenance_file)
