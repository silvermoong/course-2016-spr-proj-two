"""
Crime incidents API from data.cityofboston.gov

Michael Clawar and Raaid Arshad
"""

import datetime
import uuid

import prov.model


from mjclawar_rarshad import mcra_structures as mcras
from mjclawar_rarshad.database_helpers import DatabaseHelper
from mjclawar_rarshad.api.bdp_query import BDPQuery
from mjclawar_rarshad.mcra_structures import APIQuery, MCRASSettings, MCRASProvenance
from mjclawar_rarshad.setup_provenance import load_provenance_json, write_provenance_json


class CrimeSettings(MCRASSettings):
    @property
    def data_namespace(self):
        return mcras.BDP_NAMESPACE

    @property
    def data_entity(self):
        return 'crime_incidents'

    @property
    def agent(self):
        return '%s:crime_incidents' % self.data_namespace.name

    @property
    def base_url(self):
        return 'https://data.cityofboston.gov/resource/7cdf-6fgx.json'


class CrimeProvenance(MCRASProvenance):
    def __init__(self, settings, query=''):
        assert isinstance(settings, CrimeSettings)
        assert isinstance(query, str)
        self.settings = settings
        self.query = query

    def update_provenance(self, start_time, end_time):
        prov_doc = load_provenance_json()
        this_script = prov_doc.agent(self.settings.agent, mcras.PROVENANCE_PYTHON_SCRIPT)

        resource = prov_doc.entity('%s:%s' % (self.settings.data_namespace.name,
                                              self.settings.base_url))

        this_run = prov_doc.activity('%s:a%s' % (mcras.LOG_NAMESPACE.name, str(uuid.uuid4())), start_time, end_time,
                                     {prov.model.PROV_TYPE: mcras.PROVENANCE_ONT_RETRIEVAL,
                                      mcras.PROV_ONT_QUERY: '?' + self.query})

        prov_doc.wasAssociatedWith(this_run, this_script)
        prov_doc.used(this_run, resource, start_time)

        data_doc = prov_doc.entity('%s:%s' % (mcras.DAT_NAMESPACE.name, self.settings.data_entity),
                                   {prov.model.PROV_LABEL: 'Crimes Committed', prov.model.PROV_TYPE:
                                       mcras.PROV_ONT_DATASET})

        prov_doc.wasAttributedTo(data_doc, this_script)
        prov_doc.wasGeneratedBy(data_doc, this_run, end_time)
        prov_doc.wasDerivedFrom(data_doc, resource, this_run, this_run, this_run)

        write_provenance_json(prov_doc)


class CrimeAPIQuery(APIQuery):
    def __init__(self, settings, database_helper, bdp_api):
        assert isinstance(settings, CrimeSettings)
        assert isinstance(database_helper, DatabaseHelper)
        assert isinstance(bdp_api, BDPQuery)

        self.settings = settings
        self.database_helper = database_helper
        self.bdp_api = bdp_api

    def download_update_database(self):
        start_time = datetime.datetime.now()
        data_json, api_query = self.bdp_api.api_query(base_url=self.settings.base_url, limit=10, order='fromdate')

        self.database_helper.insert_permanent_db(self.settings.data_entity, data_json)

        end_time = datetime.datetime.now()

        crime_provenance = CrimeProvenance(self.settings, query=api_query)
        crime_provenance.update_provenance(start_time=start_time, end_time=end_time)
