# -*- coding: utf-8 -*-
from pyramid_oereb.lib.records.plr import PlrRecord
from pyramid_oereb.lib.sources import BaseDatabaseSource


class PlrDatabaseSource(BaseDatabaseSource):

    def read(self, geometry):
        """
        Central method to read all plrs.
        :param geometry: The geometry as WKT string which represents the desired property. It can be used for
        intersection operations.
        :type geometry: str
        """
        session = self._adapter_.get_session(self._key_)
        results = session.query(self._model_).filter(self._model_.geom.ST_Intersects(geometry)).all()
        self.records = list()
        for r in results:
            self.records.append(PlrRecord(
                r.content,
                r.topic,
                r.legal_state,
                r.published_from,
                r.subtopic,
                r.additional_topic,
                r.type_code,
                r.type_code_list,
                r.view_service,
                r.basis,
                r.refinements,
                r.documents,
                r.geometries
            ))
